import json
import logging
import threading
import random
import uvicorn as uvicorn

from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import HTMLResponse

import httpx

import asyncio
import aio_pika

from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime


app = FastAPI()

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

Base = declarative_base()

Base.metadata.create_all(bind=engine)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = Session()


# Configuration de la table orders de la base de données
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
    quoteCheck = Column(Boolean, default=False)
    quoteCheck_at = Column(DateTime, default=None)
    quoteConfirmation_at = Column(DateTime, default=None)
    deliverySend = Column(Boolean, nullable=False, default=False)
    deliverySend_at = Column(DateTime, default=None)
    deliveryConfirmed = Column(Boolean, nullable=False, default=False)
    deliveryConfirmed_at = Column(DateTime, default=None)
    orderEnd = Column(Boolean, nullable=False, default=False)


# Configuration de la table orders_details de la base de données
class OrdersDetails(Base):
    __tablename__ = 'orders_details'

    commande_id = Column(Integer, primary_key=True)
    address = Column(String(256), nullable=None)
    serveur_id = Column(Integer, nullable=None)
    estimation_duree = Column(Integer, nullable=None)
    TVA = Column(Float, nullable=None)
    prix = Column(Integer, nullable=None)
    main_d_oeuvre = Column(Integer, nullable=None)
    prix_HT = Column(Integer, nullable=None)
    prix_TTC = Column(Float, nullable=None)


# Fonction pour recevoir une commande
@app.post("/recevoir_commande/")
async def recevoir_commande(data: dict):

    data["commande_id"] = random.randint(1, 50000)

    # Nouveau tuple dans la table orders
    new_order = Orders(
        order_no=data["commande_id"],
        user_name=data["nom_client"],
        status="Order Received",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    session.add(new_order)
    session.commit()

    # Nouveau tuple dans la table orders_details
    new_order_details = OrdersDetails(
        commande_id=data["commande_id"],
        address=data["address"],
        serveur_id=data["server_id"],
    )
    session.add(new_order_details)
    session.commit()

    print(f' [x] Commande n°{data["commande_id"]} envoyée à la file d\'attente "command_queue"')
    await send_message_to_queue('command_queue', data)

    return {"message": "Commande reçue et envoyée à la file d'attente"}


# Fonction pour vérifier une commande
async def verifier_commande(data: dict):
    for valeur in data.values():
        if not isinstance(valeur, (str, int)) or data["server_id"] > 10000:
            raise ValueError("Le type de la valeur {} est {} au lieu de str ou int".format(valeur, type(valeur)))

    # Update du tuple dans la table orders
    order = session.query(Orders).filter(Orders.order_no == data["commande_id"]).first()
    order.status = "Order Checked"
    order.updated_at = datetime.now()
    order.infoChecked = True
    order.infoChecked_at = datetime.now()

    session.commit()

    print(f' [x] Commande n°{data["commande_id"]} envoyée à la file d\'attente command_queue_conf')
    await send_message_to_queue('command_queue_conf', data)

    return {"message": "Commande vérifiée et envoyée à la file d'attente"}


# Fonction pour envoyer la confirmation de la commande au client
@app.post("/confirmer_commande")
async def confirmer_commande(data: dict):

    print(f' [x] Commande n°{data["commande_id"]} envoyée à la file d\'attente command_queue_devis')
    await send_message_to_queue('command_queue_devis', data)

    url = "http://127.0.0.1:8002/confirmation_commande/"
    with httpx.Client() as client:
        response = client.post(url, json=data)

    if response.status_code == 200:
        pass


# Fonction pour générer un devis
@app.post("/generer_devis", response_class=HTMLResponse)
async def generer_devis(data: dict):
    data['estimation_duree_semaines'] = random.randint(1, 15)
    data['TVA'] = 0.20
    data['prix'] = random.randint(300, 5000)
    data['Main_doeuvre'] = random.randint(100, 500)

    data['Prix_HT'] = data['prix'] + data['Main_doeuvre']
    data['Prix_TTC'] = data['Prix_HT'] + data['Prix_HT'] * data['TVA']

    # Update du tuple dans la table orders
    order = session.query(Orders).filter(Orders.order_no == data["commande_id"]).first()
    order.status = "Quote Created"
    order.updated_at = datetime.now()
    order.quoteCreated = True
    order.quoteCreated_at = datetime.now()

    session.commit()

    print(f' [x] Devis n°{data["commande_id"]} envoyé à la file d\'attente verif_devis_queue')
    await send_message_to_queue('verif_devis_queue', data)


# Fonction pour vérifier un devis
@app.post("verif_devis")
async def verif_devis(data: dict):
    while True:
        print(f'Veuillez vérifier le devis n°{data["commande_id"]} : \n {data}')
        ask_modif = input("Voulez-vous modifier le devis? (oui/non): ")
        ask_modif = ask_modif.lower()
        if ask_modif == 'oui':
            champs_modif = input("Quel champ voulez-vous modifier? (prix, main_doeuvre, estimation_duree_semaines): ")
            if champs_modif.lower() == 'prix':
                data['prix'] = input("Entrez le nouveau prix: ")
            elif champs_modif.lower() == 'main_doeuvre':
                data['Main_doeuvre'] = input("Entrez le nouveau prix de la main d'oeuvre: ")
            elif champs_modif.lower() == 'estimation_duree_semaines':
                data['estimattion_durée_semaines_'] = input("Entrez la nouvelle estimation de durée en semaines: ")
            else:
                print("Champ invalide")
            data = data
        elif ask_modif == 'non':
            break

    # Update du tuple dans la table orders
    order = session.query(Orders).filter(Orders.order_no == data["commande_id"]).first()
    order.status = "Quote Checked"
    order.updated_at = datetime.now()
    order.quoteCheck = True
    order.quoteCheck_at = datetime.now()

    session.commit()

    # Update du tuple dans la table orders_details
    order_details = session.query(OrdersDetails).filter(OrdersDetails.commande_id == data["commande_id"]).first()
    order_details.estimation_duree = data['estimation_duree_semaines']
    order_details.TVA = data['TVA']
    order_details.prix = data['prix']
    order_details.main_d_oeuvre = data['Main_doeuvre']
    order_details.prix_HT = data['Prix_HT']
    order_details.prix_TTC = data['Prix_TTC']

    session.commit()

    print(f' [x] Devis n°{data["commande_id"]} envoyé à la file d\'attente envoie_devis_queue')
    await send_message_to_queue('envoie_devis_queue', data)


# Fonction pour envoyer le devis au client
@app.post("/envoie_devis")
async def envoie_devis(data: dict):
    url = "http://127.0.0.1:8002/recevoir_devis/"
    with httpx.Client() as client:
        response = client.post(url, json=data, timeout=100)
    if response.status_code == 200:
        pass


# Fonction pour recevoir la confirmation du devis et faire la réalisation
@app.post("/faire_reparation")
async def faire_reparation(data: dict):
    order = session.query(Orders).filter(Orders.order_no == data["commande_id"]).first()

    if "message_client" in data:
        print(f' [x] Devis n°{data["commande_id"]} refusé !')
        order.status = "Quote Refused"
        order.updated_at = datetime.now()
        order.orderEnd = True
        session.commit()
    else:
        # Update du tuple dans la table orders
        order.status = "Quote Confirmed"
        order.updated_at = datetime.now()
        order.quoteConfirmation_at = datetime.now()

        print(f' [x] Devis n°{data["commande_id"]} envoyé à la file d\'attente delivery_queue')
        await send_message_to_queue('delivery_queue', data)
        return {"message": "Confirmation de devis reçue"}


# Fonction pour envoyer la réalisation de la commande au client
@app.post("/envoie_delivery_confirmation")
async def envoie_realisation(data: dict):

    # Update du tuple dans la table orders
    order = session.query(Orders).filter(Orders.order_no == data["commande_id"]).first()
    order.status = "Delivery Send"
    order.updated_at = datetime.now()
    order.deliverySend = True
    order.deliverySend_at = datetime.now()

    session.commit()

    url = "http://127.0.0.1:8002/recevoir_realisation/"
    with httpx.Client() as client:
        response = client.post(url, json=data, timeout=100)
    if response.status_code == 200:
        pass


# Fonction pour recevoir la confirmation du client de la réalisation
@app.post("/confirmer_realisation")
async def confirmer_realisation(data: dict):
    order = session.query(Orders).filter(Orders.order_no == data["commande_id"]).first()

    if "message_client" in data:
        print(f' [x] Réalisation n°{data["commande_id"]} non conforme !')
        order.status = "Delivery Refused"
        order.updated_at = datetime.now()
        order.orderEnd = True

        session.commit()
    else:
        # Update du tuple dans la table orders
        order.status = "Delivery Confirmed"
        order.updated_at = datetime.now()
        order.deliveryConfirmed = True
        order.deliveryConfirmed_at = datetime.now()
        order.orderEnd = True

        session.commit()

        print(f'Fin de la commande n°{data["commande_id"]} !')


# Fonction pour envoyer un message à une file d'attente
async def send_message_to_queue(queue_name, data):
    connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")

    async with connection:
        channel = await connection.channel()

        queue = await channel.declare_queue(queue_name)

        message = aio_pika.Message(body=json.dumps(data).encode())

        await channel.default_exchange.publish(message, routing_key=queue_name)


# Fonction pour démarrer le consommateur RabbitMQ et définir les queues
async def start_rabbitmq_consumer():
    connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")

    async with connection:
        channel = await connection.channel()

        # Déclaration des files d'attente
        queues_names = ['command_queue', 'command_queue_conf', 'command_queue_devis', 'verif_devis_queue',
                        'envoie_devis_queue', 'delivery_queue']
        queues = [await channel.declare_queue(queue_name) for queue_name in queues_names]

        async def consumer_callback_verif(message: aio_pika.IncomingMessage):
            async with message.process():
                data = json.loads(message.body.decode('utf-8'))
                await verifier_commande(data)

        async def consumer_callback_conf(message: aio_pika.IncomingMessage):
            async with message.process():
                data = json.loads(message.body.decode('utf-8'))
                await confirmer_commande(data)

        async def consumer_callback_gen_devis(message: aio_pika.IncomingMessage):
            async with message.process():
                data = json.loads(message.body.decode('utf-8'))
                await generer_devis(data)

        async def consumer_callback_verif_devis(message: aio_pika.IncomingMessage):
            async with message.process():
                data = json.loads(message.body.decode('utf-8'))
                await verif_devis(data)

        async def consumer_callback_envoie_devis(message: aio_pika.IncomingMessage):
            async with message.process():
                data = json.loads(message.body.decode('utf-8'))
                await envoie_devis(data)

        async def consumer_callback_delivery_queue(message: aio_pika.IncomingMessage):
            async with message.process():
                data = json.loads(message.body.decode('utf-8'))
                await envoie_realisation(data)

        # Configuration des consommateurs
        await queues[0].consume(consumer_callback_verif)
        await queues[1].consume(consumer_callback_conf)
        await queues[2].consume(consumer_callback_gen_devis)
        await queues[3].consume(consumer_callback_verif_devis)
        await queues[4].consume(consumer_callback_envoie_devis)
        await queues[5].consume(consumer_callback_delivery_queue)

        print(' [*] En attente de commandes...')
        await asyncio.Future()

if __name__ == '__main__':
    logging.config.dictConfig({
        "version": 1,
        "disable_existing_loggers": True,
    })
    consumer_thread = threading.Thread(target=lambda: asyncio.run(start_rabbitmq_consumer()))
    consumer_thread.start()
    uvicorn.run(app, port=8001)
