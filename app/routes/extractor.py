import os
import tempfile
import zipfile
import shutil
from datetime import datetime, timezone

from fastapi import File, UploadFile, HTTPException, Request, Depends, Form
from fastapi.routing import APIRouter
from fastapi.responses import FileResponse
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.background import BackgroundTask

from app.services.llm.extractor import extract_data
from app.services.excel.generator import generate_bank_statement_excel, save_excel_to_file
from app.models.users import User
from app.models.extraction_job import ExtractionJob, JobStatus
from app.services.auth.auth import current_active_user
from app.database import get_async_session
from app.utils.logs import logger

DEFAULT_RATE_LIMIT = '10/minute'
limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/statements", tags=["statements"])


@router.post("/extract/")
@limiter.limit(DEFAULT_RATE_LIMIT)
async def extract_and_generate_excel(
    request: Request,
    document_number: str = Form(...),
    bank_code: str = Form(...),
    account_number: str = Form(...),
    file: UploadFile = File(...),
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Traite un relevé bancaire, extrait les données et retourne un fichier Excel."""
    
    logger.info(f"Reçu une demande de traitement de document pour la génération Excel : {file.filename} par l'utilisateur {user.email}")
    
    if not file.content_type in ['application/pdf']:
        logger.warning(f"Fichier rejeté avec un type non supporté : {file.content_type}")
        raise HTTPException(
            status_code=400,
            detail="Seuls les fichiers PDF sont supportés."
        )
    
    # Create extraction job record
    extraction_job = ExtractionJob(
        user_id=user.id,
        pdf_filename=file.filename,
        status=JobStatus.pending
    )
    session.add(extraction_job)
    await session.commit()
    await session.refresh(extraction_job)
    
    logger.info(f"Création du job d'extraction {extraction_job.id} pour le fichier {file.filename}")
    
    try:
        # Update status to processing
        extraction_job.status = JobStatus.processing
        await session.commit()
        
        # Sauvegarder le fichier téléchargé temporairement
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file_path = temp_file.name
            contents = await file.read()
            temp_file.write(contents)
            logger.debug(f"Fichier téléchargé sauvegardé temporairement à : {temp_file_path}")

        # Traiter le fichier
        logger.info(f"Traitement du document '{file.filename}'...")
        result = extract_data(temp_file_path)

        if isinstance(result, dict):
            logger.debug("Le résultat est un dictionnaire")
        os.unlink(temp_file_path)
        logger.debug(f"Fichier temporaire supprimé : {temp_file_path}")
        
        if not result:
            logger.error(f"Échec de l'extraction des données du document : {file.filename}")
            # Update job status to failed
            extraction_job.status = JobStatus.failed
            extraction_job.completed_at = datetime.now(timezone.utc)
            await session.commit()
            
            raise HTTPException(
                status_code=422,
                detail='Échec de l\'extraction des données du document.'
            )
        
        # Add user-provided parameters to each transaction
        if 'transactions' in result and result['transactions']:
            for transaction in result['transactions']:
                transaction['document_number'] = document_number
                transaction['bank_code'] = bank_code
                transaction['account_number'] = account_number
        
        # Générer le fichier Excel
        logger.info(f"Génération du fichier Excel à partir des données extraites")
        excel_data = generate_bank_statement_excel(result)
        
        # Créer un fichier temporaire pour la sortie Excel
        excel_filename = f"{file.filename.rsplit('.', 1)[0]}_statement.xlsx"
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as excel_temp:
            excel_path = excel_temp.name
            save_excel_to_file(excel_data, excel_path)
        
        # Update job status to success
        extraction_job.status = JobStatus.success
        extraction_job.completed_at = datetime.now(timezone.utc)
        await session.commit()
        
        logger.info(f"Job d'extraction {extraction_job.id} terminé avec succès pour le fichier {file.filename}")
        logger.info(f"Retour du fichier Excel en téléchargement : {excel_filename}")
        
        # Log de l'en-tête Content-Disposition pour debug
        content_disposition = f'attachment; filename="{excel_filename}"'
        logger.info(f"Content-Disposition header: {content_disposition}")
        
        # Retourner le fichier en réponse de téléchargement
        return FileResponse(
            path=excel_path, 
            filename=excel_filename,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": content_disposition
            },
            background=BackgroundTask(lambda: os.unlink(excel_path))
        )
    
    except Exception as e:
        logger.error(f"Erreur lors du traitement du document '{file.filename}' : {str(e)}", exc_info=True)
        
        # Update job status to failed
        try:
            extraction_job.status = JobStatus.failed
            extraction_job.completed_at = datetime.now(timezone.utc)
            await session.commit()
            logger.info(f"Job d'extraction {extraction_job.id} marqué comme échoué")
        except Exception as db_error:
            logger.error(f"Erreur lors de la mise à jour du statut du job : {db_error}")
        
        # Cleanup temporary files
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
            logger.debug(f"Nettoyage du fichier temporaire après erreur : {temp_file_path}")
        if 'excel_path' in locals() and os.path.exists(excel_path):
            os.unlink(excel_path)
            logger.debug(f"Nettoyage du fichier Excel temporaire après erreur : {excel_path}")
        
        raise HTTPException(
            status_code=500,
            detail="Une erreur est survenue lors du traitement du document"
        )

@router.post("/extract/batch")
@limiter.limit(DEFAULT_RATE_LIMIT)
async def extract_batch_and_generate_excel(
    request: Request,
    files: list[UploadFile],
    document_number: str = Form(...),
    bank_code: str = Form(...),
    account_number: str = Form(...),
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Traite plusieurs relevés bancaires et retourne un fichier zip contenant les fichiers Excel."""

    logger.info(f"Reçu une demande de traitement par lot pour la génération Excel : {len(files)} documents par l'utilisateur {user.email}")
    
    # Create extraction jobs for each file
    extraction_jobs = []
    for file in files:
        if file.content_type in ['application/pdf']:
            extraction_job = ExtractionJob(
                user_id=user.id,
                pdf_filename=file.filename,
                status=JobStatus.pending
            )
            session.add(extraction_job)
            extraction_jobs.append(extraction_job)
    
    await session.commit()
    
    # Refresh all jobs to get their IDs
    for job in extraction_jobs:
        await session.refresh(job)
    
    logger.info(f"Création de {len(extraction_jobs)} jobs d'extraction pour le traitement par lot")
    
    # Créer un répertoire temporaire pour le traitement
    temp_dir = tempfile.mkdtemp()
    excel_files = []
    
    try:
        for index, file in enumerate(files):
            logger.info(f"Traitement du fichier {index+1}/{len(files)} : {file.filename}")
            
            # Find corresponding extraction job
            extraction_job = None
            for job in extraction_jobs:
                if job.pdf_filename == file.filename:
                    extraction_job = job
                    break
            
            # Vérifier le type de fichier
            if not file.content_type in ['application/pdf']:
                logger.warning(f"Fichier ignoré avec un type non supporté : {file.content_type}")
                continue
                
            try:
                # Update job status to processing
                if extraction_job:
                    extraction_job.status = JobStatus.processing
                    await session.commit()
                
                # Sauvegarder le fichier téléchargé temporairement
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf", dir=temp_dir) as temp_file:
                    temp_file_path = temp_file.name
                    contents = await file.read()
                    temp_file.write(contents)
                
                # Traiter le fichier
                result = extract_data(temp_file_path)
                os.unlink(temp_file_path)
                
                if not result:
                    logger.error(f"Échec de l'extraction des données du document : {file.filename}")
                    # Update job status to failed
                    if extraction_job:
                        extraction_job.status = JobStatus.failed
                        extraction_job.completed_at = datetime.now(timezone.utc)
                        await session.commit()
                    continue
                
                if isinstance(result, dict):
                    result = result

                # Add user-provided parameters to each transaction
                if 'transactions' in result and result['transactions']:
                    for transaction in result['transactions']:
                        transaction['document_number'] = document_number
                        transaction['bank_code'] = bank_code
                        transaction['account_number'] = account_number
                
                # Générer le fichier Excel
                excel_data = generate_bank_statement_excel(result)
                
                # Sauvegarder le fichier Excel dans le répertoire temporaire
                excel_filename = f"{file.filename.rsplit('.', 1)[0]}_statement.xlsx"
                excel_path = os.path.join(temp_dir, excel_filename)
                save_excel_to_file(excel_data, excel_path)
                excel_files.append((excel_path, excel_filename))
                
                # Update job status to success
                if extraction_job:
                    extraction_job.status = JobStatus.success
                    extraction_job.completed_at = datetime.now(timezone.utc)
                    await session.commit()
                    logger.info(f"Job d'extraction {extraction_job.id} terminé avec succès pour le fichier {file.filename}")
                
            except Exception as e:
                logger.error(f"Erreur lors du traitement du document '{file.filename}' : {str(e)}", exc_info=True)
                
                # Update job status to failed
                if extraction_job:
                    try:
                        extraction_job.status = JobStatus.failed
                        extraction_job.completed_at = datetime.now(timezone.utc)
                        await session.commit()
                        logger.info(f"Job d'extraction {extraction_job.id} marqué comme échoué")
                    except Exception as db_error:
                        logger.error(f"Erreur lors de la mise à jour du statut du job : {db_error}")
                
                if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
        
        if not excel_files:
            # Nettoyer le répertoire temporaire si aucun fichier n'a été traité
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise HTTPException(
                status_code=422,
                detail="Échec de la génération de fichiers Excel à partir des documents téléchargés."
            )
        
        # Si un seul fichier a été traité avec succès, le retourner directement
        if len(excel_files) == 1:
            excel_path, excel_filename = excel_files[0]
            return FileResponse(
                path=excel_path,
                filename=excel_filename,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={
                    "Content-Disposition": f'attachment; filename="{excel_filename}"'
                },
                background=BackgroundTask(lambda: shutil.rmtree(temp_dir, ignore_errors=True))
            )
        
        # Sinon, créer un fichier zip avec tous les fichiers Excel
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"bank_statements_{timestamp}.zip"
        zip_path = os.path.join(temp_dir, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for excel_path, excel_filename in excel_files:
                zipf.write(excel_path, arcname=excel_filename)
        
        logger.info(f"Traitement par lot terminé avec succès. {len(excel_files)} fichiers Excel générés")
        
        return FileResponse(
            path=zip_path,
            filename=zip_filename,
            media_type="application/zip",
            headers={
                "Content-Disposition": f'attachment; filename="{zip_filename}"'
            },
            background=BackgroundTask(lambda: shutil.rmtree(temp_dir, ignore_errors=True))
        )
    except Exception as e:
        # Nettoyer en cas d'exception
        shutil.rmtree(temp_dir, ignore_errors=True)
        logger.error(f"Erreur lors du traitement par lot : {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Une erreur est survenue lors du traitement par lot"
        )