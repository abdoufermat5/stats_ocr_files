from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.orm import Session
import jwt
from jwt import PyJWTError
from passlib.context import CryptContext
from database.database import get_db
from models.models import User
from schemas.schemas import UserCreate
import os
from dotenv import load_dotenv
import logging
from config import logging_config

logger = logging.getLogger(__name__)

env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path=env_path)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def verify_password(plain_password, hashed_password):
    logger.info("Vérification du mot de passe")
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    logger.info("Hashage du mot de passe")
    return pwd_context.hash(password)


def create_db_user(db: Session, user: UserCreate):
    logger.info("Création de l'utilisateur")
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    try:
        db.commit()
        logger.info(f"User {user.username} created")
    except Exception as e:
        logger.error(f"Error lors de la création de l'utilisateur {user.username}")
        logger.error(e)
        db.rollback()
        raise HTTPException(status_code=400, detail="Username already registered")

    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, username: str, password: str):
    logger.info("Authentification de l'utilisateur")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        logger.error(f"L'utilisateur {username} n'existe pas")
        return None
    if not verify_password(password, user.hashed_password):
        logger.error(f"Mot de passe incorrect pour l'utilisateur {username}")
        return None
    return user


def create_access_token(*, data: dict, expires_delta: timedelta = None):
    logger.info("Création du token d'accès")
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    logger.info("Token d'accès créé")
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        logger.info("Récupération de l'utilisateur")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            logger.error("Token invalide")
            raise credentials_exception
    except PyJWTError:
        logger.error("Token invalide")
        raise credentials_exception
    user = db.query(User).filter(User.username == username).first()
    logger.info(f"Utilisateur {username} récupéré")
    if user is None:
        logger.error("Token invalide")
        raise credentials_exception
    logger.info("Token valide et utilisateur récupéré")
    return user
