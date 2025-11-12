FROM python:3.11-slim

WORKDIR /app

# requirements.txt liegt direkt im api/ Ordner
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Kopiere gesamten Inhalt des api/ Ordners
COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
