FROM python:3.12-slim

RUN pip install uv

WORKDIR /app

COPY pyproject.toml ./
COPY uv.lock ./
COPY README.md ./

RUN uv sync --frozen

COPY app.py ./

EXPOSE 8501

CMD ["uv", "run", "streamlit", "run", "app.py"]
