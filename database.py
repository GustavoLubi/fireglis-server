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



class Member(Base):

    __tablename__ = "members"

    id = Column(
        Integer,
        primary_key=True
    )

    server_id = Column(
        Integer
    )

    username = Column(
        String
    )



Base.metadata.create_all(engine)



class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    channel_id = Column(Integer)
    username = Column(String)
    text = Column(String)
