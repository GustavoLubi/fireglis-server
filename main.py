from fastapi import FastAPI
from database import (
    Session,
    User,
    Server,
    Channel,
    Friend,
    Invite,
    Member
)

import bcrypt
import random
import string


app = FastAPI(
    title="FireGlis Server"
)



# -------------------------
# REGISTER
# -------------------------

@app.post("/register")
def register(username:str, password:str):

    db = Session()


    user = db.query(User).filter(
        User.username == username
    ).first()


    if user:
        return {
            "ok":False,
            "msg":"Kullanıcı mevcut"
        }



    hashed = bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt()
    ).decode()



    new = User(
        username=username,
        password=hashed
    )


    db.add(new)
    db.commit()


    return {
        "ok":True
    }





# -------------------------
# LOGIN
# -------------------------

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





# -------------------------
# SERVER CREATE
# -------------------------

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



    channel=Channel(
        server_id=server.id,
        name="genel"
    )


    db.add(channel)



    member=Member(
        server_id=server.id,
        username=owner
    )


    db.add(member)

    db.commit()



    return {
        "ok":True,
        "server_id":server.id
    }





# -------------------------
# SERVER LIST
# -------------------------

@app.get("/servers/{username}")
def servers(username:str):

    db=Session()


    data=db.query(Member).filter(
        Member.username==username
    ).all()



    result=[]


    for m in data:

        s=db.query(Server).filter(
            Server.id==m.server_id
        ).first()


        if s:

            result.append(
                {
                    "id":s.id,
                    "name":s.name
                }
            )


    return result






# -------------------------
# CHANNEL LIST
# -------------------------

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





# -------------------------
# CHANNEL CREATE
# -------------------------

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





# -------------------------
# CHANNEL DELETE
# -------------------------

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





# -------------------------
# INVITE CREATE
# -------------------------

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



    invite=Invite(
        server_id=server_id,
        code=code
    )


    db.add(invite)
    db.commit()



    return {

        "ok":True,

        "invite":
        "fireglis.gg/"+code

    }





# -------------------------
# JOIN SERVER
# -------------------------

@app.post("/server/join")
def join_server(code:str,username:str):

    db=Session()



    code=code.replace(
        "fireglis.gg/",
        ""
    )



    invite=db.query(Invite).filter(
        Invite.code==code
    ).first()



    if not invite:

        return {
            "ok":False,
            "msg":"Davet yok"
        }




    exists=db.query(Member).filter(
        Member.server_id==invite.server_id,
        Member.username==username
    ).first()



    if not exists:

        member=Member(
            server_id=invite.server_id,
            username=username
        )

        db.add(member)
        db.commit()



    server=db.query(Server).filter(
        Server.id==invite.server_id
    ).first()



    return {

        "ok":True,

        "server_id":server.id,

        "server_name":server.name

    }





# -------------------------
# FRIEND
# -------------------------

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
