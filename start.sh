#!/bin/bash

echo "🌱 Iniciando Soya Insights..."
echo "================================"

# Verificar si Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado. Por favor instala Docker primero."
    exit 1
fi

# Verificar si Docker Compose está disponible
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose no está disponible. Por favor instala Docker Compose."
    exit 1
fi

echo "✅ Docker y Docker Compose detectados"
echo "🚀 Construyendo y ejecutando la aplicación..."

# Construir y ejecutar con Docker Compose
docker-compose up --build

echo "✅ Aplicación iniciada!"
echo "🌐 Abre http://localhost:8501 en tu navegador"
echo "🛑 Presiona Ctrl+C para detener la aplicación" 