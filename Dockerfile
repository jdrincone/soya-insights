# Usar imagen base de Python
FROM python:3.11-slim

# Instalar uv
RUN pip install uv

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos de configuración y lock
COPY pyproject.toml ./
COPY uv.lock ./
COPY README.md ./

# Instalar dependencias usando uv
RUN uv sync --frozen

# Copiar código de la aplicación
COPY app.py ./

# Exponer puerto de Streamlit
EXPOSE 8501

# Variables de entorno para Streamlit
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Comando para ejecutar la aplicación
CMD ["uv", "run", "streamlit", "run", "app.py"] 