from datetime import datetime

from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

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
    user_id = Column(Integer, nullable=False)
    status = Column(String(255), default=None)
    created_at = Column(DateTime, default=None)
    updated_at = Column(DateTime, default=None)
    infoChecked = Column(Boolean, default=False)
    infoChecked_at = Column(DateTime, default=None)
    quoteCreated = Column(Boolean, default=False),
    quoteCreated_at = Column(DateTime, default=None)
    quoteConfirmation_at = Column(DateTime, default=None)
    deliverySend = Column(Boolean, nullable=False, default=False)
    deliverySend_at = Column(DateTime, default=None)
    deliveryConfirmed = Column(Boolean, nullable=False, default=False)
    deliveryConfirmed_at = Column(DateTime, default=None)


@app.post("/recevoir_commande")
async def recevoir_commande(details: dict, session_id: int):
    # Vérifier si l'enregistrement existe
    instance = session.query(Orders).filter_by(order_no=session_id).first()

    data = Orders(order_no=session_id,
                  user_id=dict['user_id'],
                  status="Order received",
                  created_at=datetime.now(),
                  updated_at=datetime.now()
                  )

    session.add(data)
    session.commit()


@app.post("/verifier_commande")
async def verifier_commande():
    # Logique de vérification de commande asynchrone
    # ...
    return {"message": "Commande vérifiée"}


@app.post("/generer_devis")
async def generer_devis():
    # Logique de génération de devis asynchrone
    return {"message": "Devis généré"}


@app.post("/confirmer_realisation")
async def confirmer_realisation():
    # Logique de confirmation de réalisation asynchrone
    return {"message": "Réalisation confirmée"}
