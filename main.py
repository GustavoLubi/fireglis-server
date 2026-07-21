from fastapi import FastAPI, HTTPException, Query
import database as db

app = FastAPI(title="FireGlis Backend")

@app.on_event("startup")
def startup_event():
    # Sunucu her açıldığında veritabanı tablosunun tam oturduğundan emin oluyoruz
    db.init_db()

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

@app.post("/server/create")
def create_server(name: str = Query(...), owner: str = Query(...), color: str = Query("#5865f2")):
    try:
        sid = db.create_server(name, owner, color)
        return {"ok": True, "server_id": sid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# TAM KORUMALI SERVER LİSTELEME ENDPOINT'I
@app.get("/servers/{username}")
def get_servers(username: str):
    try:
        raw_servers = db.get_user_servers(username)
        cleaned_servers = []
        
        # Eğer gelen veri düzgün işlenmediyse bile istemciye kesinlikle 'id' anahtarı gönderiyoruz
        for s in raw_servers:
            if isinstance(s, dict):
                cleaned_servers.append({
                    "id": s.get("id", "yok"),
                    "name": s.get("name", "Bilinmeyen Sunucu"),
                    "owner": s.get("owner", "yok"),
                    "color": s.get("color", "#5865f2")
                })
            else:
                # Veritabanı eski haliyle tuple döndürdüyse koruma katmanı:
                cleaned_servers.append({
                    "id": s[0] if len(s) > 0 else "yok",
                    "name": s[1] if len(s) > 1 else "Eski Sunucu",
                    "owner": s[2] if len(s) > 2 else "yok",
                    "color": s[3] if len(s) > 3 else "#5865f2"
                })
        return cleaned_servers
    except Exception as e:
        # Sunucu tamamen patlasa bile boş liste dön, istemci (GUI) çökmesin!
        return []

@app.post("/channel/create")
def create_channel(server_id: str = Query(...), name: str = Query(...)):
    cid = db.create_channel(server_id, name)
    return {"ok": True, "channel_id": cid}

@app.get("/channels/{server_id}")
def get_channels(server_id: str):
    try:
        return db.get_channels(server_id)
    except:
        return []

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
