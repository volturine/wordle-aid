# Backend Dockerfile
FROM python:3.11-slim

WORKDIR /backend

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY words_alpha.txt ./

ENV PYTHONPATH=/backend/src

EXPOSE 9191

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "9191"]
