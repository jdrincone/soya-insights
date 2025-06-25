FROM python:3.12-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Actualizar pip e instalar setuptools
RUN pip install --upgrade pip setuptools wheel

# Copiar archivos de dependencias
COPY requirements.txt ./
COPY pyproject.toml ./

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY Soya_Insights.py ./
COPY src/ ./src/
COPY pages/ ./pages/
COPY data/ ./data/
COPY imagenes/ ./imagenes/
COPY models/ ./models/

# Crear directorio para logs de Streamlit
RUN mkdir -p /app/.streamlit

# Configurar Streamlit para producción
RUN echo "server.port = 8501" > /app/.streamlit/config.toml && \
    echo "server.address = '0.0.0.0'" >> /app/.streamlit/config.toml && \
    echo "server.enableCORS = false" >> /app/.streamlit/config.toml && \
    echo "server.enableXsrfProtection = false" >> /app/.streamlit/config.toml && \
    echo "browser.gatherUsageStats = false" >> /app/.streamlit/config.toml

# Exponer puerto
EXPOSE 8501

# Comando de inicio
CMD ["streamlit", "run", "Soya_Insights.py", "--server.port=8501", "--server.address=0.0.0.0"]
