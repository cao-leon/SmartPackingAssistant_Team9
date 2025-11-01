FROM python:3.11-slim
WORKDIR /app
COPY weather/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY weather/ .
ENV WEATHER_DATA_PATH=/data/weather_dummy.json
EXPOSE 8090
CMD ["uvicorn","weather_mock:app","--host","0.0.0.0","--port","8090","--http","h11"]
