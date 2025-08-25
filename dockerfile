FROM python:3.10-slim

# Установка зависимостей для pygame и X11
RUN apt-get update && apt-get install -y \
    python3-dev \
    build-essential \
    libx11-6 \
    libxext6 \
    libxrender1 \
    libxrandr2 \
    libxcursor1 \
    libxi6 \
    libgl1-mesa-glx \
    libglib2.0-0 \
    x11-apps \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir pygame

ENV DISPLAY=:0

CMD ["python", "gui.py"]
