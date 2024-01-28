import json
import threading
import pika
import uvicorn as uvicorn
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import HTMLResponse

import random
import httpx

import asyncio
import aio_pika

app = FastAPI()


@app.post("/recevoir_commande/")
async def recevoir_commande(data: dict):

    await send_message_to_queue('command_queue', data)

    print(" [x] Message envoyé à la file d'attente 'command_queue'")
    return {"message": "Commande reçue et envoyée à la file d'attente"}


async def verifier_commande(data: dict):
    for valeur in data.values():
        if not isinstance(valeur, (str, int)) or data["server_id"] > 10000:
            raise ValueError("Le type de la valeur {} est {} au lieu de str ou int".format(valeur, type(valeur)))
    print("message serveur: " + "Commande verifié")

    await  send_message_to_queue('command_queue_conf', data)

    print(" [x] Message envoyé à la file d'attente 'command_queue_conf'")
    return {"message": "Commande vérifiée et envoyée à la file d'attente"}


@app.post("/confirmer_commande")
async def confirmer_commande(data: dict):

    await send_message_to_queue('command_queue_devis', data)

    print(" [x] Message envoyé à la file d'attente 'command_queue_devis'")

    url = "http://127.0.0.1:8002/confirmation_commande/"
    with httpx.Client() as client:
        response = client.post(url, json=data)

    if response.status_code == 200:
        pass

    return {"message": "Commande envoyée à la file d'attente"}


@app.post("/generer_devis", response_class=HTMLResponse)
async def generer_devis(data: dict):
    data['estimation_duree_semaines'] = random.randint(1, 5)
    data['TVA'] = 0.20
    data['prix'] = random.randint(300, 5000)
    data['Main_doeuvre'] = random.randint(100, 500)

    data['Prix_HT'] = data['prix'] + data['Main_doeuvre']
    data['Prix_TTC'] = data['Prix_HT'] + data['Prix_HT'] * data['TVA']
    print("message serveur: " + "Devis généré")
    print(data)

    await send_message_to_queue('verif_devis_queue', data)

    print(" [x] Message envoyé à la file d'attente 'verif_devis_queue'")


@app.post("verif_devis")
async def verif_devis(data: dict):
    while True:
        print(data)
        ask_modif = input("Voulez-vous modifier le devis? (oui/non): ")
        ask_modif = ask_modif.lower()
        if ask_modif == 'oui':
            champs_modif = input("Quel champ voulez-vous modifier? (prix, main_doeuvre, estimation_duree_semaines): ")
            if champs_modif.lower() == 'prix':
                data['prix'] = input("Entrez le nouveau prix: ")
            elif champs_modif.lower() == 'main_doeuvre':
                data['Main_doeuvre'] = input("Entrez le nouveau prix de la main d'oeuvre: ")
            elif champs_modif.lower() == 'estimation_durée_semaines':
                data['estimattion_durée_semaines_'] = input("Entrez la nouvelle estimation de durée en semaines: ")
            else:
                print("Champ invalide")
            data = data
        elif ask_modif == 'non':
            break

    await send_message_to_queue('envoie_devis_queue', data)

    print(" [x] Message envoyé à la file d'attente 'envoie_devis_queue'")


@app.post("/envoie_devis")
async def envoie_devis(data: dict):
    url = "http://127.0.0.1:8002/recevoir_devis/"
    with httpx.Client() as client:
        response = client.post(url, json=data, timeout=100)
    if response.status_code == 200:
        pass


@app.post("/confirmer_devis")
async def confirmer_devis(data: dict):
    print("Devis confirmé: ", data)
    return {"message": "Confirmation de devis reçue"}


async def send_message_to_queue(queue_name, data):
    connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")

    async with connection:
        channel = await connection.channel()

        queue = await channel.declare_queue(queue_name)

        message = aio_pika.Message(body=json.dumps(data).encode())

        await channel.default_exchange.publish(message, routing_key=queue_name)

async def start_rabbitmq_consumer():
    connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")

    async with connection:
        channel = await connection.channel()

        # Déclaration des files d'attente
        queues_names = ['command_queue', 'command_queue_conf', 'command_queue_devis', 'verif_devis_queue',
                        'envoie_devis_queue']
        queues = [await channel.declare_queue(queue_name) for queue_name in queues_names]

        async def consumer_callback_verif(message: aio_pika.IncomingMessage):
            async with message.process():
                data = json.loads(message.body.decode('utf-8'))
                print(" [x] Received %r" % data)
                await verifier_commande(data)

        async def consumer_callback_conf(message: aio_pika.IncomingMessage):
            async with message.process():
                data = json.loads(message.body.decode('utf-8'))
                print(" [x] Received %r" % data)
                await confirmer_commande(data)

        async def consumer_callback_gen_devis(message: aio_pika.IncomingMessage):
            async with message.process():
                data = json.loads(message.body.decode('utf-8'))
                print(" [x] Received %r" % data)
                await generer_devis(data)

        async def consumer_callback_verif_devis(message: aio_pika.IncomingMessage):
            async with message.process():
                data = json.loads(message.body.decode('utf-8'))
                print(" [x] Received %r" % data)
                await verif_devis(data)

        async def consumer_callback_envoie_devis(message: aio_pika.IncomingMessage):
            async with message.process():
                data = json.loads(message.body.decode('utf-8'))
                print(" [x] Received %r" % data)
                await envoie_devis(data)

        # Configuration des consommateurs
        await queues[0].consume(consumer_callback_verif)
        await queues[1].consume(consumer_callback_conf)
        await queues[2].consume(consumer_callback_gen_devis)
        await queues[3].consume(consumer_callback_verif_devis)
        await queues[4].consume(consumer_callback_envoie_devis)

        print(' [*] En attente de commandes...')
        await asyncio.Future()

if __name__ == '__main__':
    consumer_thread = threading.Thread(target=lambda: asyncio.run(start_rabbitmq_consumer()))
    consumer_thread.start()
    uvicorn.run(app, port=8001)
