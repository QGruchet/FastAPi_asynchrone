from fastapi import FastAPI, BackgroundTasks

app = FastAPI()


def order_to_queue(order_data):
    # Code pour se connecter à RabbitMQ/Kafka et envoyer le message
    pass


@app.post("/passer_commande")
async def passer_commande(order_details: dict, background_tasks: BackgroundTasks):
    background_tasks.add_task(order_to_queue, order_details)
    return {"message": "Commande soumise avec succès"}


@app.post("/confirmation_commande")
async def confirmation_commande():
    # Logique de confirmation de commande asynchrone
    # ...
    return {"message": "Commande confirmée"}


@app.post("/recevoir_devis")
async def recevoir_devis():
    return {"message": "Devis reçu"}


@app.post("/confirmation_devis")
async def confirmation_commande():
    # Logique de confirmation de commande asynchrone
    return {"message": "Devis confirmée"}
