from sqlalchemy import Column, Integer, String
class Process(Base):
    __tablename__ = "processes"

    id = Column(Integer, String, primary_key=True, index=True)
    # Ajoutez d'autres champs selon vos besoins

Base.metadata.create_all(bind=engine)