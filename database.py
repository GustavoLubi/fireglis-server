from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker


DATABASE_URL = "sqlite:///fireglis.db"


engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False
    }
)


Session = sessionmaker(
    bind=engine
)


Base = declarative_base()



# Kullanıcılar

class User(Base):

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True
    )

    username = Column(
        String,
        unique=True
    )

    password = Column(
        String
    )



# Sunucular

class Server(Base):

    __tablename__ = "servers"

    id = Column(
        Integer,
        primary_key=True
    )

    name = Column(
        String
    )

    owner = Column(
        String
    )



# Kanallar

class Channel(Base):

    __tablename__ = "channels"

    id = Column(
        Integer,
        primary_key=True
    )

    server_id = Column(
        Integer
    )

    name = Column(
        String
    )



# Arkadaşlar

class Friend(Base):

    __tablename__ = "friends"

    id = Column(
        Integer,
        primary_key=True
    )

    sender = Column(
        String
    )

    receiver = Column(
        String
    )

    status = Column(
        String,
        default="pending"
    )



# Davetler

class Invite(Base):

    __tablename__ = "invites"

    id = Column(
        Integer,
        primary_key=True
    )

    server_id = Column(
        Integer
    )

    code = Column(
        String,
        unique=True
    )



Base.metadata.create_all(
    engine
)
