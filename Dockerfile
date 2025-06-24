FROM python:3.12-slim

RUN pip install uv

WORKDIR /app

COPY pyproject.toml ./
COPY uv.lock ./
COPY requirements.txt ./
COPY README.md ./

RUN uv sync --frozen
RUN pip install -r requirements.txt

COPY app.py ./
COPY pages/ ./pages/
COPY models/ ./models/

# Generar la imagen SHAP corporativa durante la construcción
RUN python3 models/create_shap_beeswarm_corporativo.py

EXPOSE 8501

CMD ["uv", "run", "streamlit", "run", "app.py"]
