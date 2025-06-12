from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = 'postgresql://localhost/postgres'
engine = create_engine(DATABASE_URL)

Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()


class NickName(Base):
    __tablename__ = "nicknames"

    id = Column(Integer, primary_key=True)
    name = Column(String)


Base.metadata.create_all(engine)