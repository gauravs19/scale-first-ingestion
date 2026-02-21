FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install fastapi uvicorn redis pydantic prometheus_client PyYAML
COPY config_loader.py .
COPY config/ config/
CMD ["uvicorn", "ingestor.app:app", "--host", "0.0.0.0", "--port", "8000"]
