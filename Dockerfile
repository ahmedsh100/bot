FROM python:3.11-slim

RUN apt-get update && apt-get install -y ffmpeg

WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt

CMD ["python", "main.py"]
