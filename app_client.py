import json
import random

import uvicorn as uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import httpx


app = FastAPI()

# Configurez CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Autorise toutes les origines
    allow_credentials=True,
    allow_methods=["*"],  # Autorise toutes les méthodes
    allow_headers=["*"],  # Autorise tous les headers
)


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
        print("message client: Erreur lors de l'envoi de la commande")


@app.post("/confirmation_commande/")
async def confirmation_commande():
    print("message client: " + "Commande confirmée")


@app.post("/recevoir_devis/")
async def recevoir_devis(data: dict):
    print("message client: " + "Devis reçu")
    print(data)
    conf_devis = input("Voulez-vous confirmer le devis ? (oui/non) : ")
    if conf_devis == "oui":
        confirmer_devis_au_serveur(data)
    else:
        print("Devis refusé")

def confirmer_devis_au_serveur(devis):
    url = "http://127.0.0.1:8001/confirmer_devis"
    with httpx.Client() as client:
        response = client.post(url, json=devis, timeout=None)
        if response.status_code == 200:
            print("Devis confirmé avec succès")
        else:
            print("Erreur lors de la confirmation du devis")


@app.post("/confirmation_devis")
async def confirmation_commande():
    # Logique de confirmation de commande asynchrone
    return {"message": "Devis confirmée"}


if __name__ == '__main__':
    uvicorn.run(app, port=8002)
