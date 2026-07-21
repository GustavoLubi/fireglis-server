from fastapi import FastAPI, HTTPException, Query
import database as db

app = FastAPI(title="FireGlis Backend")

@app.post("/register")
def register(username: str = Query(...), password: str = Query(...)):
    success = db.add_user(username, password)
    if not success:
        raise HTTPException(status_code=400, detail="Bu kullanıcı adı zaten alınmış.")
    return {"ok": True, "message": "Kayıt başarılı."}

@app.post("/login")
def login(username: str = Query(...), password: str = Query(...)):
    user = db.get_user(username, password)
    if not user:
        raise HTTPException(status_code=401, detail="Hatalı kullanıcı adı veya şifre.")
    return {"ok": True, "username": username}

# CLIENT İLE %100 UYUMLU SUNUCU OLUŞTURMA ENDPOINT'I
@app.post("/server/create")
def create_server(
    name: str = Query(...), 
    owner: str = Query(...), 
    color: str = Query("#5865f2")
):
    try:
        sid = db.create_server(name, owner, color)
        return {"ok": True, "server_id": sid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sunucu veritabanına kaydedilemedi: {str(e)}")

@app.get("/servers/{username}")
def get_servers(username: str):
    return db.get_user_servers(username)

@app.post("/channel/create")
def create_channel(server_id: str = Query(...), name: str = Query(...)):
    cid = db.create_channel(server_id, name)
    return {"ok": True, "channel_id": cid}

@app.get("/channels/{server_id}")
def get_channels(server_id: str):
    return db.get_channels(server_id)

@app.delete("/channel/delete/{channel_id}")
def delete_channel(channel_id: str):
    db.delete_channel(channel_id)
    return {"ok": True}

@app.post("/invite/create")
def create_invite(server_id: str = Query(...)):
    invite_code = db.create_invite(server_id)
    return {"ok": True, "invite": invite_code}

@app.post("/server/join")
def join_server(code: str = Query(...), username: str = Query(...)):
    res = db.join_server(code, username)
    if not res:
        raise HTTPException(status_code=404, detail="Geçersiz davet kodu.")
    return {"ok": True, "server_id": res["server_id"], "server_name": res["server_name"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
