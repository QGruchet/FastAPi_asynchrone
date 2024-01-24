from fastapi import FastAPI, Form
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import uvicorn

app = FastAPI()
"""
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

Base = declarative_base()


class Process(Base):
    __tablename__ = "processes"

    id = Column(Integer, primary_key=True, index=True)


Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

"""
@app.get("/")
def read_root():
    return {"message": "Hello "}

if __name__ == '__main__':
    uvicorn.run(app, port=8000)

