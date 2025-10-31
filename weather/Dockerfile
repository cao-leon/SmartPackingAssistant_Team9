FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir fastapi uvicorn python-dateutil pydantic
COPY weather/ .
ENV WEATHER_DATA_PATH=/data/weather_dummy.json
EXPOSE 8090
CMD ["uvicorn","weather_mock:app","--host","0.0.0.0","--port","8090"]
