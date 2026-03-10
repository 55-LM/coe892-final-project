# Operations Service - Pickup simulation and events
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

ENV PYTHONUNBUFFERED=1
# Planning service URL when running in Docker Compose
ENV PLANNING_SERVICE_URL=http://planning-service:8000

EXPOSE 8001
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
