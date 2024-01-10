from fastapi import FastAPI

app = FastAPI()

@app.post("/passer_commande")
async def passer_commande():
    # Logique de soumission de commande asynchrone
    # ...
    return {"message": "Commande soumise avec succès"}

@app.post("/confirmation_commande")
async def confirmation_commande():
    # Logique de confirmation de commande asynchrone
    # ...
    return {"message": "Commande confirmée"}
