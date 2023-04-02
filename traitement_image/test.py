from sqlalchemy import create_engine

DATABASE_URL = "postgres://abdou:password123@localhost:5433/traitement_db"
engine = create_engine(DATABASE_URL)

if __name__ == "__main__":
    # Test de la connexion à la base de données
    with engine.connect() as connection:
        result = connection.execute("SELECT 1")
        print(result.fetchone())