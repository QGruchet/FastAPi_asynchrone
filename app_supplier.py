import json
import threading
import pika
import uvicorn as uvicorn
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import HTMLResponse

import random
import httpx


app = FastAPI()


connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
publish_channel = connection.channel()
publish_channel.queue_declare(queue='command_queue')
publish_channel.queue_declare(queue='command_queue_conf')
publish_channel.queue_declare(queue='command_queue_devis')
publish_channel.queue_declare(queue='verif_devis_queue')
publish_channel.queue_declare(queue='envoie_devis_queue')


@app.post("/recevoir_commande/")
async def recevoir_commande(data: dict, backgroundtask: BackgroundTasks):

    publish_channel.basic_publish(exchange='',
                          routing_key='command_queue',
                          body=json.dumps(data))

    print(" [x] Message envoyé à la file d'attente 'command_queue'")
    return {"message": "Commande reçue et envoyée à la file d'attente"}


def verifier_commande(data: dict):
    for valeur in data.values():
        if not isinstance(valeur, (str, int)) or data["server_id"] > 10000:
            raise ValueError("Le type de la valeur {} est {} au lieu de str ou int".format(valeur, type(valeur)))
    print("message serveur: " + "Commande verifié")

    publish_channel.basic_publish(exchange='',
                          routing_key='command_queue_conf',
                          body=json.dumps(data))

    print(" [x] Message envoyé à la file d'attente 'command_queue_conf'")
    return {"message": "Commande vérifiée et envoyée à la file d'attente"}

@app.post("/confirmer_commande")
def confirmer_commande(data: dict):

    publish_channel.basic_publish(exchange='',
                          routing_key='command_queue_devis',
                          body=json.dumps(data))

    print(" [x] Message envoyé à la file d'attente 'command_queue_devis'")

    url = "http://127.0.0.1:8002/confirmation_commande/"
    with httpx.Client() as client:
        response = client.post(url, json=data)

    if response.status_code == 200:
        pass

    return {"message": "Commande envoyée à la file d'attente"}


@app.post("/generer_devis", response_class=HTMLResponse)
def generer_devis(data: dict):

    data['estimation_duree_semaines'] = random.randint(1, 5)
    data['TVA'] = 0.20
    data['prix'] = random.randint(300, 5000)
    data['Main_doeuvre'] = random.randint(100, 500)

    data['Prix_HT'] = data['prix'] + data['Main_doeuvre']
    data['Prix_TTC'] = data['Prix_HT'] + data['Prix_HT'] * data['TVA']
    print("message serveur: " + "Devis généré")
    print(data)

    publish_channel.basic_publish(exchange='',
                          routing_key='verif_devis_queue',
                          body=json.dumps(data))

    print(" [x] Message envoyé à la file d'attente 'verif_devis_queue'")


@app.post("verif_devis")
def verif_devis(data: dict):
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

    publish_channel.basic_publish(exchange='',
                          routing_key='envoie_devis_queue',
                          body=json.dumps(data))

    print(" [x] Message envoyé à la file d'attente 'envoie_devis_queue'")


@app.post("/envoie_devis")
def envoie_devis(data: dict):

    url = "http://127.0.0.1:8002/recevoir_devis/"
    with httpx.Client() as client:
        response = client.post(url, json=data, timeout=100)
    if response.status_code == 200:
        pass


@app.post("/confirmer_devis")
async def confirmer_devis(data: dict):
    print("Devis confirmé: ", data)
    return {"message": "Confirmation de devis reçue"}


def start_rabbitmq_consumer():
    consumer_connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    consumer_channel = consumer_connection.channel()
    consumer_channel.queue_declare(queue='command_queue')
    consumer_channel.queue_declare(queue='command_queue_conf')
    consumer_channel.queue_declare(queue='command_queue_devis')
    consumer_channel.queue_declare(queue='verif_devis_queue')
    consumer_channel.queue_declare(queue='envoie_devis_queue')

    def consumer_callback_verif(ch, method, properties, body):
        print(" [x] Received %r" % body)
        verifier_commande(json.loads(body.decode('utf-8')))

    def consumer_callback_conf(ch, method, properties, body):
        print(" [x] Received %r" % body)
        confirmer_commande(json.loads(body.decode('utf-8')))

    def consumer_callback_gen_devis(ch, method, properties, body):
        print(" [x] Received %r" % body)
        generer_devis(json.loads(body.decode('utf-8')))

    def consumer_callback_verif_devis(ch, method, properties, body):
        print(" [x] Received %r" % body)
        verif_devis(json.loads(body.decode('utf-8')))

    def consumer_callback_envoie_devis(ch, method, properties, body):
        print(" [x] Received %r" % body)
        envoie_devis(json.loads(body.decode('utf-8')))

    consumer_channel.basic_consume(queue='command_queue',
                                   on_message_callback=consumer_callback_verif,
                                   auto_ack=True)

    consumer_channel.basic_consume(queue='command_queue_conf',
                                   on_message_callback=consumer_callback_conf,
                                   auto_ack=True)

    consumer_channel.basic_consume(queue='command_queue_devis',
                                   on_message_callback=consumer_callback_gen_devis,
                                   auto_ack=True)

    consumer_channel.basic_consume(queue='verif_devis_queue',
                                   on_message_callback=consumer_callback_verif_devis,
                                   auto_ack=True)

    consumer_channel.basic_consume(queue='envoie_devis_queue',
                                   on_message_callback=consumer_callback_envoie_devis,
                                   auto_ack=True)

    print(' [*] En attente de commandes...')
    consumer_channel.start_consuming()


@app.on_event("startup")
async def startup_event():
    thread = threading.Thread(target=start_rabbitmq_consumer)
    thread.start()

if __name__ == '__main__':
    uvicorn.run(app, port=8001)
