from typing import List

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Header, UploadFile, File
from fastapi.responses import JSONResponse
from httpx import AsyncClient
import jwt
import os
import logging
from config import logging_config

# Chargez les variables d'environnement
load_dotenv()

# Utilisez le logger dans votre application
logger = logging.getLogger(__name__)

app = FastAPI()

# La clé secrète utilisée pour signer les tokens JWT
JWT_SECRET = os.getenv('JWT_SECRET')

# Les adresses des autres microservices
AUTH_SERVICE_URL = "http://authentification:8001"
OCR_SERVICE_URL = "http://traitement_image:8002"
STATS_SERVICE_URL = "http://statistiques:8003"


@app.post("api/auth/register/")
async def register(username: str, password: str):
    async with AsyncClient() as client:
        logger.info(f"Création de l'utilisateur {username}")
        response = await client.post(f"{AUTH_SERVICE_URL}/users",
                                     json={"username": username, "password": password})
        if response.status_code != 200:
            logger.error(f"Erreur lors de la création de l'utilisateur {username}: {response.json()}")
            raise HTTPException(status_code=400, detail="Nom d'utilisateur déjà utilisé")
        access_token = response.json()['access_token']
        logger.info(f"Utilisateur {username} créé avec succès")
    return {"access_token": access_token}


@app.post("api/auth/login/")
async def login(username: str, password: str):
    logger.info(f"Authentification de l'utilisateur {username}")
    async with AsyncClient() as client:
        response = await client.post(f"{AUTH_SERVICE_URL}/token",
                                     json={"username": username, "password": password})
        if response.status_code != 200:
            logger.error(f"Erreur lors de l'authentification de l'utilisateur {username}: {response.json()}")
            raise HTTPException(status_code=401, detail="Nom d'utilisateur ou mot de passe invalide")
        access_token = response.json()['access_token']
        logger.info(f"Utilisateur {username} authentifié avec succès")
    return {"access_token": access_token}


@app.get("api/auth/me/")
async def read_users_me(authorization: str = Header(None)):
    async with AsyncClient() as client:
        headers = {"Authorization": authorization}
        response = await client.get(f"{AUTH_SERVICE_URL}/users/me/", headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=401, detail="Authentification invalide")
    return response.json()


@app.post("api/traitement_image/traite")
async def process_image(files: List[UploadFile] = File(...), authorization: str = Header(None)):
    # Vérification de l'authentification de l'utilisateur
    try:
        logger.info(f"Vérification de l'authentification de l'utilisateur")
        payload = jwt.decode(authorization, JWT_SECRET, algorithms=["HS256"])
        username = payload['sub']
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de l'authentification de l'utilisateur: {e}")
        raise HTTPException(status_code=401, detail="Authentification invalide")
    logger.info(f"Utilisateur {username} authentifié avec succès")
    # Envoi de la requête au microservice de traitement d'image
    async with AsyncClient() as client:
        headers = {"Authorization": authorization}
        response = await client.post(f"{OCR_SERVICE_URL}/process_image/", headers=headers, files=files)
        if response.status_code != 200:
            logger.error(f"Erreur lors du traitement de l'image: {response.json()}")
            raise HTTPException(status_code=response.status_code, detail=response.text)
        result = response.json()
        logger.info(f"Image traitée avec succès")

    return JSONResponse(content=result)


@app.get("api/stats/")
async def get_stats(authorization: str = Header(None)):
    # Vérification de l'authentification de l'utilisateur
    try:
        payload = jwt.decode(authorization, JWT_SECRET, algorithms=["HS256"])
        username = payload['sub']
    except:
        raise HTTPException(status_code=401, detail="Authentification invalide")

    # Envoi de la requête au microservice de statistiques
    async with AsyncClient() as client:
        headers = {"Authorization": authorization}
        response = await client.get(f"{STATS_SERVICE_URL}/stats/", headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        result = response.json()

    return JSONResponse(content=result)


if __name__ == "__main__":
    import uvicorn

    host, port = "localhost", 8000
    uvicorn.run(app,
                host=host,
                port=port,
                log_level="info",
                reload=True)
