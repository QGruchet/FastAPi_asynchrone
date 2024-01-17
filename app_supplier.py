import json
from datetime import datetime
from pydantic import BaseModel


import pika
import uvicorn as uvicorn
from fastapi import FastAPI, BackgroundTasks, Body
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import requests
import httpx

app = FastAPI()

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

Base = declarative_base()

Base.metadata.create_all(bind=engine)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = Session()


class Orders(Base):
    __tablename__ = 'orders'

    order_no = Column(Integer, primary_key=True)
    user_name = Column(String(256), nullable=False)
    status = Column(String(255), default=None)
    created_at = Column(DateTime, default=None)
    updated_at = Column(DateTime, default=None)
    infoChecked = Column(Boolean, default=False)
    infoChecked_at = Column(DateTime, default=None)
    quoteCreated = Column(Boolean, default=False)
    quoteCreated_at = Column(DateTime, default=None)
    quoteConfirmation_at = Column(DateTime, default=None)
    deliverySend = Column(Boolean, nullable=False, default=False)
    deliverySend_at = Column(DateTime, default=None)
    deliveryConfirmed = Column(Boolean, nullable=False, default=False)
    deliveryConfirmed_at = Column(DateTime, default=None)


@app.post("/recevoir_commande/")
async def recevoir_commande(data: dict, backgroundtask: BackgroundTasks):
    print(data)
    backgroundtask.add_task(verifier_commande, data, backgroundtask)
    print('message from recevoir_commande : '+ 'Commande reçu avec succès')


def verifier_commande(data: dict, backgroundtask: BackgroundTasks):
    data["commande_id"] = data["commande_id"] + 1
    print(data)
    backgroundtask.add_task(confirmer_commande, data)
    return {'message from verifier commande': 'Commande vérifié avec succès !'}

@app.get("/confirmer_commande")
def confirmer_commande(data: dict):
    data["commande_id"] = data["commande_id"] + 1
    url = "http://127.0.0.1:8002/confirmation_commande/"
    print(data)
    with httpx.Client() as client:
        response = client.post(url, json=data)

    if response.status_code == 200:
        pass

# @app.post("/generer_devis")
# async def generer_devis():
#     # Logique de génération de devis asynchrone
#     return {"message": "Devis généré"}
#
#
# @app.post("/confirmer_realisation")
# async def confirmer_realisation():
#     # Logique de confirmation de réalisation asynchrone
#     return {"message": "Réalisation confirmée"}


if __name__ == '__main__':
    uvicorn.run(app, port=8001)
