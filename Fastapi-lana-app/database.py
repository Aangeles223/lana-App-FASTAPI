from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ⚠️ Reemplaza 'root', 'tu_contraseña' y 'localhost' según tu configuración:
DATABASE_URL = "mysql+mysqlconnector://root:Master12$@localhost/lana_app"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
