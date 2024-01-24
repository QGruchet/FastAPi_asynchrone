import json
import random

import uvicorn as uvicorn
from fastapi import FastAPI, BackgroundTasks, Request, Response, HTTPException
from fastapi.responses import JSONResponse
from fastapi.responses import RedirectResponse
import pika
import httpx
import requests

app = FastAPI()


@app.get("/envoye_commande")
def envoye_commande():
    # Lecture du contenu du fichier JSON
    with open('order.json', 'r') as order:
        contenu_json = order.read()

    id_session = random.randint(1, 500)

    data = json.loads(contenu_json)
    data["commande_id"] = id_session
    print(data)

    url = "http://127.0.0.1:8001/recevoir_commande/"

    with httpx.Client() as client:
        response = client.post(url, json=data)

    if response.status_code == 200:
        print("message client: Commande envoyée")
    else:
        print("j'en sais rien")


@app.post("/confirmation_commande/")
async def confirmation_commande(data: dict):
    print("message client: " + "Commande confirmée")
    print(data)


@app.get("/recevoir_devis")
async def recevoir_devis():
    return {"message": "Devis reçu"}


@app.post("/confirmation_devis")
async def confirmation_commande():
    # Logique de confirmation de commande asynchrone
    return {"message": "Devis confirmée"}


if __name__ == '__main__':
    uvicorn.run(app, port=8002)
