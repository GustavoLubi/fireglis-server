import os
import uuid
import sqlite3
from fastapi import FastAPI, HTTPException, Query
import uvicorn

# ----------------------------------------------------------------
# VERİTABANI KATMANI (DOĞRUDAN main.py İÇİNE GÖMÜLDÜ)
# ----------------------------------------------------------------
DB_NAME = "fireglis.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS servers (id TEXT PRIMARY KEY, name TEXT, owner TEXT, color TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS channels (id TEXT PRIMARY KEY, server_id TEXT, name TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS invites (code TEXT PRIMARY KEY, server_id TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS server_members (server_id TEXT, username TEXT, PRIMARY KEY(server_id, username))")
    conn.commit()
    conn.close()

def add_user(username, password):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_user(username, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

def create_server(name, owner, color="#5865f2"):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    server_id = str(uuid.uuid4())
    cursor.execute("INSERT INTO servers (id, name, owner, color) VALUES (?, ?, ?, ?)", (server_id, name, owner, color))
    cursor.execute("INSERT INTO server_members (server_id, username) VALUES (?, ?)", (server_id, owner))
    channel_id = str(uuid.uuid4())
    cursor.execute("INSERT INTO channels (id, server_id, name) VALUES (?, ?, ?)", (channel_id, server_id, "genel"))
    conn.commit()
    conn.close()
    return server_id

def get_user_servers(username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.id, s.name, s.owner, s.color 
        FROM servers s
        JOIN server_members sm ON s.id = sm.server_id
        WHERE sm.username = ?
    """, (username,))
    rows = cursor.fetchall()
    servers = []
    for row in rows:
        servers.append({
            "id": row[0],
            "name": row[1],
            "owner": row[2],
            "color": row[3] if row[3] else "#5865f2"
        })
    conn.close()
    return servers

def create_channel(server_id, name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    channel_id = str(uuid.uuid4())
    cursor.execute("INSERT INTO channels (id, server_id, name) VALUES (?, ?, ?)", (channel_id, server_id, name))
    conn.commit()
    conn.close()
    return channel_id

def get_channels(server_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, server_id, name FROM channels WHERE server_id = ?", (server_id,))
    rows = cursor.fetchall()
    channels = []
    for row in rows:
        channels.append({"id": row[0], "server_id": row[1], "name": row[2]})
    conn.close()
    return channels

def delete_channel(channel_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM channels WHERE id = ?", (channel_id,))
    conn.commit()
    conn.close()

def create_invite(server_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    code = str(uuid.uuid4())[:8]
    cursor.execute("INSERT INTO invites (code, server_id) VALUES (?, ?)", (code, server_id))
    conn.commit()
    conn.close()
    return f"fireglis.gg/{code}"

def join_server(code, username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT server_id FROM invites WHERE code = ?", (code,))
    res = cursor.fetchone()
    if not res:
        conn.close()
        return None
    server_id = res[0]
    try:
        cursor.execute("INSERT INTO server_members (server_id, username) VALUES (?, ?)", (server_id, username))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    cursor.execute("SELECT name FROM servers WHERE id = ?", (server_id,))
    server_name = cursor.fetchone()[0]
    conn.close()
    return {"server_id": server_id, "server_name": server_name}

# ----------------------------------------------------------------
# API KATMANI (FASTAPI)
# ----------------------------------------------------------------
app = FastAPI(title="FireGlis Backend - Monolith")

@app.on_event("startup")
def startup_event():
    init_db()

@app.post("/register")
def register_endpoint(username: str = Query(...), password: str = Query(...)):
    success = add_user(username, password)
    if not success:
        raise HTTPException(status_code=400, detail="Bu kullanıcı adı zaten alınmış.")
    return {"ok": True, "message": "Kayıt başarılı."}

@app.post("/login")
def login_endpoint(username: str = Query(...), password: str = Query(...)):
    user = get_user(username, password)
    if not user:
        raise HTTPException(status_code=401, detail="Hatalı kullanıcı adı veya şifre.")
    return {"ok": True, "username": username}

@app.post("/server/create")
def create_server_endpoint(name: str = Query(...), owner: str = Query(...), color: str = Query("#5865f2")):
    try:
        sid = create_server(name, owner, color)
        return {"ok": True, "server_id": sid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/servers/{username}")
def get_servers_endpoint(username: str):
    try:
        return get_user_servers(username)
    except:
        return []

@app.post("/channel/create")
def create_channel_endpoint(server_id: str = Query(...), name: str = Query(...)):
    cid = create_channel(server_id, name)
    return {"ok": True, "channel_id": cid}

@app.get("/channels/{server_id}")
def get_channels_endpoint(server_id: str):
    try:
        return get_channels(server_id)
    except:
        return []

@app.delete("/channel/delete/{channel_id}")
def delete_channel_endpoint(channel_id: str):
    delete_channel(channel_id)
    return {"ok": True}

@app.post("/invite/create")
def create_invite_endpoint(server_id: str = Query(...)):
    invite_code = create_invite(server_id)
    return {"ok": True, "invite": invite_code}

@app.post("/server/join")
def join_server_endpoint(code: str = Query(...), username: str = Query(...)):
    res = join_server(code, username)
    if not res:
        raise HTTPException(status_code=404, detail="Geçersiz davet kodu.")
    return {"ok": True, "server_id": res["server_id"], "server_name": res["server_name"]}

if __name__ == "__main__":
    # RAILWAY DINAMIK PORT AYARI
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
