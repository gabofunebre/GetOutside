import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Construcción de la URL de conexión desde variables de entorno
DB_URL = (
    f"postgresql://{os.getenv('DB_USER')}:"
    f"{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}:"
    f"{os.getenv('DB_PORT')}/"
    f"{os.getenv('DB_NAME')}"
)

# Motor de base de datos
engine = create_engine(DB_URL, echo=True, future=True)

# Sesión local para operaciones en cada request
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Clase base para tus modelos ORM
Base = declarative_base()
