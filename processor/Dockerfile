FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install redis prometheus_client PyYAML
CMD ["python", "processor/worker.py"]
