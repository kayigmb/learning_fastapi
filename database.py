from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from logger import logger
from utils.config import settings

engine = create_engine(settings.DB_URL, echo=True)

sessionLocal = sessionmaker(bind=engine)


def getdb():
    logger.info("DB session created")
    with sessionLocal() as session:
        yield session


db = Annotated[sessionLocal, Depends(getdb)]
