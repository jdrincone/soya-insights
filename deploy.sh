#!/bin/bash

# Script de despliegue para Soya Insights
# Uso: ./deploy.sh [ambiente]
# Ambientes: dev, staging, prod

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para logging
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

# Verificar que Docker esté instalado
check_docker() {
    if ! command -v docker &> /dev/null; then
        error "Docker no está instalado. Por favor instale Docker primero."
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose no está instalado. Por favor instale Docker Compose primero."
    fi
    
    log "Docker y Docker Compose verificados ✓"
}

# Parar contenedores existentes
stop_containers() {
    log "Deteniendo contenedores existentes..."
    docker-compose down --remove-orphans || true
}

# Limpiar imágenes antiguas
cleanup_images() {
    log "Limpiando imágenes Docker antiguas..."
    docker image prune -f || true
}

# Construir nueva imagen
build_image() {
    log "Construyendo imagen Docker..."
    docker-compose build --no-cache
}

# Iniciar servicios
start_services() {
    log "Iniciando servicios..."
    docker-compose up -d
    
    # Esperar a que el servicio esté listo
    log "Esperando a que el servicio esté listo..."
    sleep 10
    
    # Verificar health check
    for i in {1..30}; do
        if curl -f http://localhost:8501/_stcore/health &> /dev/null; then
            log "Servicio iniciado correctamente ✓"
            return 0
        fi
        sleep 2
    done
    
    error "El servicio no se inició correctamente después de 60 segundos"
}

# Mostrar logs
show_logs() {
    log "Mostrando logs del servicio..."
    docker-compose logs -f --tail=50
}

# Función principal
main() {
    local environment=${1:-prod}
    
    log "Iniciando despliegue de Soya Insights en ambiente: $environment"
    
    # Verificar prerequisitos
    check_docker
    
    # Parar contenedores existentes
    stop_containers
    
    # Limpiar imágenes antiguas
    cleanup_images
    
    # Construir nueva imagen
    build_image
    
    # Iniciar servicios
    start_services
    
    log "🎉 Despliegue completado exitosamente!"
    log "📊 La aplicación está disponible en: http://localhost:8501"
    log "📋 Para ver logs: docker-compose logs -f"
    log "🛑 Para detener: docker-compose down"
}

# Ejecutar función principal
main "$@" 