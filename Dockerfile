# Dockerfile pour le Chatbot UM5
FROM python:3.10-slim

# Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Répertoire de travail
WORKDIR /app

# Copier requirements et installer
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copier l'application
COPY app.py .
COPY static/ ./static/

# Copier les modèles et données (à télécharger depuis Kaggle)
COPY models/ ./models/
COPY data/ ./data/

# Exposer le port
EXPOSE 8000

# Commande de démarrage
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
