import random
import os
import traceback

from dotenv import load_dotenv
from pathlib import Path
from google import genai
from app.schemas.extractor import BankStatementResponse
from app.utils.logs import logger

load_dotenv()

PROMPT = """
Extraisez toutes les informations pertinentes du relevé bancaire fourni et structurez-les selon le schéma JSON spécifié. Incluez :
- Le titulaire du compte (nom ou entité).
- Le numéro de compte bancaire.
- Le nom de la banque.
- Les dates de début et de fin du relevé.
- Toutes les transactions listées, avec pour chaque transaction : la date (format JJ/MM/AAAA), la description (libellé), le montant (en valeur numérique, avec signe pour débits/crédits), 
  montant du débit en valeur numérique positive (0.0 si pas de débit) et montant du crédit en valeur numérique positive (0.0 si pas de crédit).
- La devise du compte.
- Les soldes initial et final.
Si une information est manquante ou ambiguë, indiquez "None" pour ce champ. 
Pour les transactions, identifiez les tableaux ou listes dans le document et extrayez chaque ligne comme une transaction distincte. 
Pour chaque transaction, utilisez soit debit soit credit (jamais les deux), l'autre étant à 0.0.
Assurez-vous que les montants sont correctement formatés (par exemple, "1 234,56" devient 1234.56).
"""

# 3 différents clés API pour éviter les limites de quota
API_KEYS = [
    os.getenv("GOOGLE_API_KEY_1"),
    os.getenv("GOOGLE_API_KEY_2"),
    os.getenv("GOOGLE_API_KEY_3"),
]

def extract_data(file_path: str):
    google_key = random.choice(API_KEYS)
    try:
        logger.info("Téléchargement du fichier et début du traitement ...")
        file_path = Path(file_path)
        client = genai.Client(api_key=google_key) if google_key else genai.Client()
        sample_file = client.files.upload(file=file_path)
        logger.info("Fichier téléchargé ... Obtention de la réponse du client Gemini")
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=[sample_file, PROMPT],
            config={
                "response_mime_type": "application/json",
                "response_schema": BankStatementResponse
            }
        )
        logger.info("Réponse générée :)")
        
        # Log response details for debugging without accessing non-existent attributes
        logger.debug(f"Type de réponse : {type(response)}")
        
        if hasattr(response, 'parsed') and response.parsed:
            logger.info("Réponse analysée avec succès")
            # Convert pydantic model to dict if needed
            if hasattr(response.parsed, 'model_dump'):
                return response.parsed.model_dump()
            elif hasattr(response.parsed, 'dict'):
                return response.parsed.dict()
            else:
                return response.parsed
        elif hasattr(response, 'text') and response.text:
            # Fallback: try to parse the text response as JSON
            logger.info("Tentative d'analyse du texte de réponse")
            try:
                import json
                text_data = json.loads(response.text)
                return text_data
            except (json.JSONDecodeError, Exception) as json_error:
                logger.error(f"Erreur lors de l'analyse JSON du texte : {json_error}")
                return None
        else:
            logger.warning("Aucune réponse analysée ou texte disponible")
            # Log available attributes for debugging
            logger.debug(f"Attributs disponibles : {dir(response)}")
            return None
            
    except Exception as e:
        logger.error(f"Erreur lors du traitement du document : {str(e)}")
        logger.error(traceback.format_exc())
        return None
