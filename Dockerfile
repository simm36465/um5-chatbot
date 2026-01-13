# Dockerfile pour le Chatbot UM5 - Railway
FROM python:3.10-slim

# Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Installer git (nécessaire pour Git LFS)
RUN apt-get update && apt-get install -y \
    git \
    git-lfs \
    && rm -rf /var/lib/apt/lists/*

# Répertoire de travail
WORKDIR /app

# Copier requirements et installer
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copier l'application
COPY app.py .
COPY static/ ./static/

# ✅ CORRECTION : Copier depuis output/ (vos vrais chemins)
COPY output/ ./output/

# ✅ Port dynamique pour Railway (utilise $PORT)
EXPOSE 8000

# ✅ CORRECTION : Utiliser variable d'environnement PORT
CMD uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}