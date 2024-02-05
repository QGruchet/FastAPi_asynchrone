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


# Fonction pour envoyer une commande
@app.get("/envoye_commande/{name_order}")
def envoye_commande(name_order: str):
    # Lecture du contenu du fichier JSON
    with open(f'{name_order}.json', 'r') as order:
        contenu_json = order.read()

    id_session = random.randint(1, 50000)

    data = json.loads(contenu_json)
    data["commande_id"] = id_session

    url = "http://127.0.0.1:8001/recevoir_commande/"

    with httpx.Client() as client:
        response = client.post(url, json=data)

    if response.status_code == 200:
        print(f'Commande n°{id_session} envoyée !')

    else:
        print("message client: Erreur lors de l'envoi de la commande")


# Fonction pour recevoir la confirmation de la commande
@app.post("/confirmation_commande/")
def confirmation_commande(data: dict):
    print(f'Commande n°{data["commande_id"]} confirmée !')
    return {"message": "Commande confirmée"}


# Fonction pour recevoir le devis
@app.post("/recevoir_devis/")
async def recevoir_devis(data: dict):
    print(f'Devis n°{data["commande_id"]} reçue !')
    conf_devis = input(f'Voulez-vous confirmer le devis suivant (n°{data["commande_id"]}) ? (oui/non) : \n {data} \n')
    if conf_devis == "oui":
        confirmer_devis_au_serveur(data)
    else:
        print(f'Devis n°{data["commande_id"]} refusé !')
        refus = {"message_client": "Devis refusé", "commande_id": data["commande_id"]}
        confirmer_devis_au_serveur(refus)


# Fonction pour confirmer le devis au fournisseur
def confirmer_devis_au_serveur(devis):
    url = "http://127.0.0.1:8001/faire_reparation"
    with httpx.Client() as client:
        response = client.post(url, json=devis, timeout=None)
        if response.status_code == 200:
            print(f'Devis n°{devis["commande_id"]} renvoyé !')
        else:
            print(f'Erreur lors de la confirmation du devis n°{devis["commande_id"]}')


# Fonction pour recevoir la réalisation de la commande
@app.post("/recevoir_realisation/")
async def recevoir_realisation(data: dict):
    print(f'Travaux n°{data["commande_id"]} effectué !')
    conf_real = input("Les travaux ont-ils été effectués ? (oui/non) : \n")
    if conf_real == "oui":
        confirmer_realisation_au_serveur(data)
    else:
        print(f'Réalisation n°{data["commande_id"]} non conforme !')
        refus = {"message_client": "Réalisation non conforme", "commande_id": data["commande_id"]}
        confirmer_realisation_au_serveur(refus)


# Fonction pour confirmer la réalisation au fournisseur
def confirmer_realisation_au_serveur(devis):
    url = "http://127.0.0.1:8001/confirmer_realisation"
    with httpx.Client() as client:
        response = client.post(url, json=devis, timeout=None)
        if response.status_code == 200:
            print(f'Fin de la commande : n°{devis["commande_id"]} !')
        else:
            print(f'Erreur lors de la confirmation de la realisation n°{devis["commande_id"]}')


if __name__ == '__main__':
    uvicorn.run(app, port=8002)
