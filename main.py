from fastapi import FastAPI
from database import (
    Session,
    User,
    Server,
    Channel,
    Friend,
    Invite
)

import bcrypt
import random
import string


app = FastAPI(
    title="FireGlis Server"
)



# --------------------
# REGISTER
# --------------------

@app.post("/register")
def register(username:str, password:str):

    db = Session()


    exists = db.query(User).filter(
        User.username == username
    ).first()


    if exists:
        return {
            "ok":False,
            "msg":"Kullanıcı zaten var"
        }



    hashed = bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt()
    ).decode()



    user = User(
        username=username,
        password=hashed
    )


    db.add(user)
    db.commit()


    return {
        "ok":True
    }




# --------------------
# LOGIN
# --------------------

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




# --------------------
# SERVER CREATE
# --------------------

@app.post("/server/create")
def create_server(name:str,owner:str):

    db=Session()


    server=Server(
        name=name,
        owner=owner
    )


    db.add(server)
    db.commit()
    db.refresh(server)



    # otomatik genel kanal

    channel=Channel(
        server_id=server.id,
        name="genel"
    )


    db.add(channel)
    db.commit()



    return {
        "ok":True,
        "server_id":server.id
    }





# --------------------
# SERVER LIST
# --------------------

@app.get("/servers/{username}")
def get_servers(username:str):

    db=Session()


    servers=db.query(Server).filter(
        Server.owner==username
    ).all()



    return [

        {
            "id":x.id,
            "name":x.name
        }

        for x in servers

    ]






# --------------------
# CHANNEL CREATE
# --------------------

@app.post("/channel/create")
def create_channel(server_id:int,name:str):

    db=Session()


    c=Channel(
        server_id=server_id,
        name=name
    )


    db.add(c)
    db.commit()


    return {
        "ok":True
    }





# --------------------
# CHANNEL LIST
# --------------------

@app.get("/channels/{server_id}")
def channels(server_id:int):

    db=Session()


    data=db.query(Channel).filter(
        Channel.server_id==server_id
    ).all()


    return [

        {
            "id":x.id,
            "name":x.name
        }

        for x in data

    ]






# --------------------
# CHANNEL DELETE
# --------------------

@app.delete("/channel/delete/{id}")
def delete_channel(id:int):

    db=Session()


    c=db.query(Channel).filter(
        Channel.id==id
    ).first()


    if c:

        db.delete(c)
        db.commit()


    return {
        "ok":True
    }






# --------------------
# INVITE CREATE
# --------------------

@app.post("/invite/create")
def create_invite(server_id:int):

    db=Session()


    code="".join(
        random.choice(
            string.ascii_letters+
            string.digits
        )
        for i in range(8)
    )


    inv=Invite(
        server_id=server_id,
        code=code
    )


    db.add(inv)
    db.commit()



    return {

        "ok":True,

        "invite":
        "fireglis.gg/"+code

    }







# --------------------
# INVITE LIST
# --------------------

@app.get("/invite/{server_id}")
def invites(server_id:int):

    db=Session()


    data=db.query(Invite).filter(
        Invite.server_id==server_id
    ).all()



    return [

        x.code

        for x in data

    ]






# --------------------
# FRIEND REQUEST
# --------------------

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
