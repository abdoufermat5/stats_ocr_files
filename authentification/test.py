from sqlalchemy import create_engine
from sqlalchemy import text

DATABASE_URL = "postgresql://abdou:password123@localhost:5434/auth_db"
engine = create_engine(DATABASE_URL)

if __name__ == "__main__":
    # Test de la connexion à la base de données
    with engine.connect() as connection:
        from models.models import Base
        Base.metadata.create_all(bind=engine)
        result = connection.execute(text("SELECT 1"))
        print(result.fetchone())