import os

from models.base import Base
import models.import_all as _models  # must load models before session  # noqa: F401

print("IMPORT ALL LOADED")
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SERVER ='D403-013'
DATABASE ='smart_Encomy'
DRIVER = 'ODBC Driver 17 for SQL Server'

connection_string = os.environ.get("SPENDWISE_DATABASE_URL") or (
    f"mssql+pyodbc://@{SERVER}/{DATABASE}"
    f"?driver={DRIVER.replace(' ', '+')}"
    f"&trusted_connection=yes"
)

engine_options = {"echo": os.environ.get("SPENDWISE_SQL_ECHO", "0") == "1"}
if connection_string.startswith("sqlite"):
    engine_options["connect_args"] = {"check_same_thread": False}

engine = create_engine(connection_string, **engine_options)
"""
Base.metadata.create_all(bind=engine)
"""


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

