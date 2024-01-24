import json
import threading
import pika
import uvicorn as uvicorn
from fastapi import FastAPI, BackgroundTasks, Body

import httpx

app = FastAPI()

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='command_queue')
channel.queue_declare(queue='command_queue_conf')
channel.queue_declare(queue='command_queue_devis')


@app.post("/recevoir_commande/")
async def recevoir_commande(data: dict, backgroundtask: BackgroundTasks):

    channel.basic_publish(exchange='',
                          routing_key='command_queue',
                          body=json.dumps(data))

    print(" [x] Message envoyé à la file d'attente 'command_queue'")
    return {"message": "Commande reçue et envoyée à la file d'attente"}


def verifier_commande(data: dict):
    for valeur in data.values():
        if not isinstance(valeur, (str, int)) or data["server_id"] > 10000:
            raise ValueError("Le type de la valeur {} est {} au lieu de str ou int".format(valeur, type(valeur)))
    print("message serveur: " + "Commande verifié")
    channel.basic_publish(exchange='',
                          routing_key='command_queue_conf',
                          body=json.dumps(data))
    print(" [x] Message envoyé à la file d'attente 'command_queue_conf'")


@app.post("/confirmer_commande")
def confirmer_commande(data: dict):

    channel.basic_publish(exchange='',
                          routing_key='command_queue_devis',
                          body=json.dumps(data))

    print(" [x] Message envoyé à la file d'attente 'command_queue_devis'")

    url = "http://127.0.0.1:8002/confirmation_commande/"
    with httpx.Client() as client:
        response = client.post(url, json=data)

    if response.status_code == 200:
        pass

    return {"message": "Commande envoyée à la file d'attente"}


def generer_devis(data: dict):
    print("message serveur: " + "Devis généré")


def start_rabbitmq_consumer():
    consumer_connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    consumer_channel = consumer_connection.channel()
    consumer_channel.queue_declare(queue='command_queue')
    consumer_channel.queue_declare(queue='command_queue_conf')
    consumer_channel.queue_declare(queue='command_queue_devis')

    def consumer_callback_verif(ch, method, properties, body):
        print(" [x] Received %r" % body)
        verifier_commande(json.loads(body.decode('utf-8')))

    def consumer_callback_conf(ch, method, properties, body):
        print(" [x] Received %r" % body)
        confirmer_commande(json.loads(body.decode('utf-8')))

    def consumer_callback_devis(ch, method, properties, body):
        print(" [x] Received %r" % body)
        generer_devis(json.loads(body.decode('utf-8')))

    consumer_channel.basic_consume(queue='command_queue',
                                   on_message_callback=consumer_callback_verif,
                                   auto_ack=True)

    consumer_channel.basic_consume(queue='command_queue_conf',
                                   on_message_callback=consumer_callback_conf,
                                   auto_ack=True)

    consumer_channel.basic_consume(queue='command_queue_devis',
                                   on_message_callback=consumer_callback_devis,
                                   auto_ack=True)

    print(' [*] En attente de commandes...')
    consumer_channel.start_consuming()


@app.on_event("startup")
async def startup_event():
    thread = threading.Thread(target=start_rabbitmq_consumer)
    thread.start()

if __name__ == '__main__':
    uvicorn.run(app, port=8001)
