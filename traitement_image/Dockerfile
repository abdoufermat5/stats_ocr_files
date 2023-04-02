# Utilisez une image de base avec Python 3.9
FROM python:3.9-slim

# label
LABEL version="1.0"
LABEL description="Dockerfile for the traitement_image"
LABEL name="traitement_image"

# Définissez le répertoire de travail
WORKDIR /app

# Copiez les fichiers de requirements (si vous en avez) dans le conteneur
COPY requirements.txt .

# Installez les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copiez le reste des fichiers de l'application dans le conteneur
COPY . /app

# Exposez le port pour le microservice
EXPOSE 8002

# Démarrez l'application FastAPI avec uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
