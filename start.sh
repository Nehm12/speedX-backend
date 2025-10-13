#!/bin/bash

# =============================================================================
# FLUXY - Script de Démarrage
# =============================================================================
# Script pour démarrer l'application Fluxy avec toutes les vérifications
# nécessaires et la configuration appropriée.
# =============================================================================

set -e  # Arrêter le script en cas d'erreur

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration par défaut
DEFAULT_HOST="0.0.0.0"
DEFAULT_PORT="8000"
DEFAULT_WORKERS="1"
DEFAULT_LOG_LEVEL="info"

# Variables d'environnement
HOST=${HOST:-$DEFAULT_HOST}
PORT=${PORT:-$DEFAULT_PORT}
WORKERS=${WORKERS:-$DEFAULT_WORKERS}
LOG_LEVEL=${LOG_LEVEL:-$DEFAULT_LOG_LEVEL}
RELOAD=${RELOAD:-"true"}

# Fonction d'affichage des messages
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}[FLUXY]${NC} $message"
}

print_success() {
    print_message "$GREEN" "$1"
}

print_error() {
    print_message "$RED" "$1"
}

print_warning() {
    print_message "$YELLOW" "$1"
}

print_info() {
    print_message "$BLUE" "$1"
}

# Fonction d'aide
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help          Afficher cette aide"
    echo "  -p, --port PORT     Port d'écoute (défaut: 8000)"
    echo "  -H, --host HOST     Adresse d'écoute (défaut: 0.0.0.0)"
    echo "  -w, --workers N     Nombre de workers (défaut: 1)"
    echo "  -l, --log-level L   Niveau de log (défaut: info)"
    echo "  --no-reload         Désactiver le rechargement automatique"
    echo "  --prod              Mode production (désactive reload)"
    echo "  --dev               Mode développement (active reload)"
    echo ""
    echo "Variables d'environnement:"
    echo "  HOST                Adresse d'écoute"
    echo "  PORT                Port d'écoute"
    echo "  WORKERS             Nombre de workers"
    echo "  LOG_LEVEL           Niveau de log"
    echo "  RELOAD              Rechargement automatique (true/false)"
    echo "  GOOGLE_API_KEY      Clé API Google Gemini (obligatoire)"
    echo ""
    echo "Exemples:"
    echo "  $0                  # Démarrage avec les paramètres par défaut"
    echo "  $0 --port 3000      # Démarrage sur le port 3000"
    echo "  $0 --prod           # Démarrage en mode production"
    echo "  $0 --dev            # Démarrage en mode développement"
}

# Vérification de Python
check_python() {
    print_info "Vérification de Python..."
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 n'est pas installé ou non accessible"
        exit 1
    fi
    
    python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
    major_version=$(echo $python_version | cut -d'.' -f1)
    minor_version=$(echo $python_version | cut -d'.' -f2)
    
    if [ "$major_version" -lt 3 ] || [ "$major_version" -eq 3 -a "$minor_version" -lt 12 ]; then
        print_error "Python 3.12+ requis. Version détectée: $python_version"
        exit 1
    fi
    
    print_success "Python $python_version détecté ✓"
}

# Vérification des dépendances
check_dependencies() {
    print_info "Vérification des dépendances..."
    
    # Vérifier si uv est disponible
    if command -v uv &> /dev/null; then
        print_success "Gestionnaire de paquets 'uv' détecté ✓"
        PACKAGE_MANAGER="uv"
    elif command -v pip &> /dev/null; then
        print_warning "Utilisation de 'pip' (recommandé: installer 'uv')"
        PACKAGE_MANAGER="pip"
    else
        print_error "Aucun gestionnaire de paquets trouvé (pip ou uv requis)"
        exit 1
    fi
    
    # Vérifier si les dépendances sont installées
    if ! python3 -c "import fastapi" &> /dev/null; then
        print_warning "Dépendances manquantes. Installation..."
        
        if [ "$PACKAGE_MANAGER" = "uv" ]; then
            uv sync
        else
            pip install -r requirements.txt 2>/dev/null || pip install fastapi uvicorn google-genai pandas openpyxl pydantic python-multipart sqlalchemy jinja2 xlsxwriter
        fi
        
        print_success "Dépendances installées ✓"
    else
        print_success "Dépendances vérifiées ✓"
    fi
}

# Vérification de la structure du projet
check_project_structure() {
    print_info "Vérification de la structure du projet..."
    
    required_files=(
        "app/main.py"
        "app/routes/extractor.py"
        "app/services/llm/extractor.py"
        "pyproject.toml"
    )
    
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            print_error "Fichier manquant: $file"
            exit 1
        fi
    done
    
    print_success "Structure du projet vérifiée ✓"
}

# Fonction de démarrage
start_server() {
    print_info "Démarrage de Fluxy..."
    print_info "Host: $HOST"
    print_info "Port: $PORT"
    print_info "Workers: $WORKERS"
    print_info "Log Level: $LOG_LEVEL"
    print_info "Reload: $RELOAD"
    
    # Construction de la commande uvicorn
    cmd="uvicorn app.main:app --host $HOST --port $PORT --log-level $LOG_LEVEL"
    
    if [ "$RELOAD" = "true" ]; then
        cmd="$cmd --reload"
        print_info "Mode développement activé (rechargement automatique)"
    else
        cmd="$cmd --workers $WORKERS"
        print_info "Mode production activé"
    fi
    
    print_success "Fluxy est en cours de démarrage..."
    print_info "URL: http://$HOST:$PORT"
    print_info "Documentation API: http://$HOST:$PORT/docs"
    print_info "Arrêter avec Ctrl+C"
    
    echo ""
    exec $cmd
}

# Parse des arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -p|--port)
            PORT="$2"
            shift 2
            ;;
        -H|--host)
            HOST="$2"
            shift 2
            ;;
        -w|--workers)
            WORKERS="$2"
            shift 2
            ;;
        -l|--log-level)
            LOG_LEVEL="$2"
            shift 2
            ;;
        --no-reload)
            RELOAD="false"
            shift
            ;;
        --prod)
            RELOAD="false"
            WORKERS=${WORKERS:-"4"}
            LOG_LEVEL="warning"
            shift
            ;;
        --dev)
            RELOAD="true"
            WORKERS="1"
            LOG_LEVEL="debug"
            shift
            ;;
        *)
            print_error "Option inconnue: $1"
            show_help
            exit 1
            ;;
    esac
done

# Banner d'accueil
echo ""
echo -e "${BLUE}  ███████╗██╗     ██╗   ██╗██╗  ██╗██╗   ██╗${NC}"
echo -e "${BLUE}  ██╔════╝██║     ██║   ██║╚██╗██╔╝╚██╗ ██╔╝${NC}"
echo -e "${BLUE}  █████╗  ██║     ██║   ██║ ╚███╔╝  ╚████╔╝ ${NC}"
echo -e "${BLUE}  ██╔══╝  ██║     ██║   ██║ ██╔██╗   ╚██╔╝  ${NC}"
echo -e "${BLUE}  ██║     ███████╗╚██████╔╝██╔╝ ██╗   ██║   ${NC}"
echo -e "${BLUE}  ╚═╝     ╚══════╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ${NC}"
echo ""
print_info "Extracteur Automatique de Relevés Bancaires"
print_info "Version 1.0.0"
echo ""

# Exécution des vérifications
check_python
check_project_structure
check_dependencies

# Démarrage du serveur
start_server