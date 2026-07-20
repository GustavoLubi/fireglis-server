from fastapi import FastAPI
from sqlalchemy import Column, Integer, String
from database import Base, engine, Session

import bcrypt
import random
import string


app = FastAPI(
    title="FireGlis Server"
)



class User(Base):

    __tablename__="users"

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

    __tablename__="servers"

    id = Column(
        Integer,
        primary_key=True
    )

    name = Column(
        String
    )

    invite = Column(
        String,
        unique=True
    )

    owner = Column(
        String
    )



class Friend(Base):

    __tablename__="friends"

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


Base.metadata.create_all(engine)



@app.post("/register")
def register(username:str,password:str):

    db = Session()


    if db.query(User).filter(
        User.username==username
    ).first():

        return {
            "ok":False,
            "msg":"Var"
        }


    pw = bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt()
    ).decode()


    user = User(
        username=username,
        password=pw
    )


    db.add(user)
    db.commit()


    return {
        "ok":True
    }





@app.post("/login")
def login(username:str,password:str):

    db=Session()


    user=db.query(User).filter(
        User.username==username
    ).first()


    if not user:
        return {
            "ok":False
        }


    if bcrypt.checkpw(
        password.encode(),
        user.password.encode()
    ):

        return {
            "ok":True,
            "username":username
        }


    return {
        "ok":False
    }





@app.post("/server/create")
def create_server(name:str,owner:str):

    db=Session()


    code="".join(
        random.choice(
            string.ascii_letters+
            string.digits
        )
        for i in range(8)
    )


    s=Server(
        name=name,
        owner=owner,
        invite=code
    )


    db.add(s)
    db.commit()


    return {
        "ok":True,
        "invite":
        "fireglis.gg/"+code
    }





@app.get("/servers/{username}")
def servers(username:str):

    db=Session()


    data=db.query(Server).filter(
        Server.owner==username
    ).all()


    return [
        {
            "name":x.name,
            "invite":x.invite
        }

        for x in data
    ]





@app.post("/friend/request")
def friend_request(sender:str,receiver:str):

    db=Session()


    f=Friend(
        sender=sender,
        receiver=receiver
    )


    db.add(f)
    db.commit()


    return {
        "ok":True
    }



@app.get("/friends/{username}")
def friends(username:str):

    db=Session()


    data=db.query(Friend).filter(
        (Friend.sender==username) |
        (Friend.receiver==username)
    ).all()


    result=[]


    for x in data:

        if x.sender==username:
            result.append(x.receiver)
        else:
            result.append(x.sender)


    return result