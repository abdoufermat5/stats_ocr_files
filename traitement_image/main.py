from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import List
import pytesseract
from pytesseract import Output
from PIL import Image
import logging

from sqlalchemy.orm import Session

from config import logging_config
from database.database import get_db
from models.models import ImageResult

# Chargez les variables d'environnement
load_dotenv()

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


@app.post("/process_image/")
async def process_image(files: List[UploadFile] = File(...), db: Session = Depends(get_db)):
    result = []
    logger.info(f"Traitement de {len(files)} images")
    for file in files:
        try:
            logger.info(f"Traitement de l'image {file.filename}")
            # Ouvrir l'image
            image = Image.open(file.file)

            # Appliquer OCR à l'image
            ocr_data = pytesseract.image_to_data(image, output_type=Output.DICT, lang="fra+eng")

            # Ajouter les résultats à la liste
            result.append({
                "filename": file.filename,
                "ocr_data": ocr_data
            })
            logger.info(f"Image {file.filename} traitée avec succès")

            logger.info(f"Stockage de l'image {file.filename}")
            # Stocker les résultats dans la base de données
            image_result = ImageResult(filename=file.filename, ocr_data=ocr_data)
            try:
                db.add(image_result)
                db.commit()
                logger.info(f"Image {file.filename} stockée avec succès")
            except Exception as e:
                logger.error(f"Erreur lors du stockage de l'image {file.filename}: {str(e)}")
                raise HTTPException(status_code=400,
                                    detail=f"Erreur lors du stockage de l'image {file.filename}: {str(e)}")
            logger.info(f"Stockage de l'image {file.filename} terminé")
        except Exception as e:
            logger.error(f"Erreur lors du traitement de l'image {file.filename}: {str(e)}")
            raise HTTPException(status_code=400,
                                detail=f"Erreur lors du traitement de l'image {file.filename}: {str(e)}")
    logger.info(f"Traitement de {len(files)} images terminé")
    return JSONResponse(content=result)


if __name__ == "__main__":
    logger.info("OCR: Starting the application")
    import uvicorn

    host, port = "localhost", 8002
    uvicorn.run("main:app",
                host=host,
                port=port,
                reload=True,
                log_level="info")

    logger.info(f"OCR: Application started at http://{host}:{port}")
