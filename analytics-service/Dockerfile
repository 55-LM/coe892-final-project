# Analytics Service - Metrics from operations and planning
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

ENV PYTHONUNBUFFERED=1
ENV OPERATIONS_SERVICE_URL=http://operations-service:8001
ENV PLANNING_SERVICE_URL=http://planning-service:8000

EXPOSE 8002
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
