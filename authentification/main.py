from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.database import get_db
from dependencies.dependencies import authenticate_user, create_access_token, get_current_user, create_user
from schemas.schemas import Token, UserCreate, User
import logging
from config import logging_config

# Utilisez le logger dans votre application
logger = logging.getLogger(__name__)
app = FastAPI()


# Créez les tables de la base de données
@app.on_event("startup")
async def startup():
    logger.info("Création des tables de la base de données")
    from database.database import engine
    from models.models import Base
    Base.metadata.create_all(bind=engine)
    logger.info("Tables de la base de données créées avec succès")


@app.post("/users", response_model=User)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = authenticate_user(db, user.username, user.password)
    if db_user:
        logger.error(f"Username {user.username} already registered")
        raise HTTPException(status_code=400, detail="Username already registered")
    logger.info(f"User {user.username} created")
    return create_user(db=db, user=user)


@app.post("/token", response_model=Token)
def login_for_access_token(form_data: UserCreate, db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        logger.error(f"Incorrect username or password for user {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.username}
    )
    logger.info(f"User {form_data.username} logged in")
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me")
def read_users_me(current_user: User = Depends(get_current_user)):
    logger.info(f"User {current_user.username} logged in")
    return current_user


if __name__ == "__main__":
    logger.info("Starting the application")
    import uvicorn

    host, port = "localhost", 8001
    uvicorn.run("main:app",
                host=host,
                port=port,
                reload=True,
                log_level="debug")

    logger.info(f"Application started at http://{host}:{port}")
