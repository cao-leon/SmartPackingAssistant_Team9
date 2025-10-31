FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 DATA_DIR=/data
COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY api/ .
EXPOSE 8080
# uvicorn lädt api/main.py -> app
CMD ["uvicorn","main:app","--host","0.0.0.0","--port","8080"]
