from database import Message # Yukarıdaki importların arasına Message'ı da ekle

# -------------------------
# MESSAGE SEND
# -------------------------
@app.post("/message/send")
def send_message(channel_id: int, username: str, text: str):
    db = Session()
    msg = Message(channel_id=channel_id, username=username, text=text)
    db.add(msg)
    db.commit()
    return {"ok": True}

# -------------------------
# MESSAGE LIST
# -------------------------
@app.get("/messages/{channel_id}")
def get_messages(channel_id: int):
    db = Session()
    data = db.query(Message).filter(Message.channel_id == channel_id).all()
    return [
        {
            "username": x.username,
            "text": x.text
        }
        for x in data
    ]
