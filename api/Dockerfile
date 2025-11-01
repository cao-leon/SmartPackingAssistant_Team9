FROM python:3.11-slim
WORKDIR /app
COPY api/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY api/ .
ENV WEATHER_URL=http://weather:8090
EXPOSE 8080
CMD ["uvicorn","main:app","--host","0.0.0.0","--port","8080","--http","h11"]
