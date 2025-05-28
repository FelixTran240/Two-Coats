from src import config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

connection_url = config.get_settings().POSTGRES_URI
engine = create_engine(connection_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
