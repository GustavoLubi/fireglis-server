import os
from sanic import Sanic, response
import database as db

app = Sanic("FireGlis_Backend")

@app.before_server_start
async def setup_db(app, loop):
    db.init_db()

@app.post("/register")
async def register(request):
    # Hem URL parametresinden hem de form verisinden okuma garantisi
    username = request.args.get("username") or request.form.get("username")
    password = request.args.get("password") or request.form.get("password")
    
    if not username or not password:
        return response.json({"ok": False, "error": "Eksik bilgi"}, status=400)
        
    success = db.add_user(username, password)
    if not success:
        return response.json({"ok": False, "error": "Kullanıcı adı alınmış."}, status=400)
    return response.json({"ok": True, "message": "Kayıt başarılı."})

@app.post("/login")
async def login(request):
    username = request.args.get("username") or request.form.get("username")
    password = request.args.get("password") or request.form.get("password")
    
    user = db.get_user(username, password)
    if not user:
        return response.json({"ok": False, "error": "Hatalı giriş."}, status=401)
    return response.json({"ok": True, "username": username})

@app.post("/server/create")
async def create_server(request):
    name = request.args.get("name") or request.form.get("name")
    owner = request.args.get("owner") or request.form.get("owner")
    color = request.args.get("color") or request.form.get("color") or "#5865f2"
    
    try:
        sid = db.create_server(name, owner, color)
        return response.json({"ok": True, "server_id": sid})
    except Exception as e:
        return response.json({"ok": False, "error": str(e)}, status=500)

@app.get("/servers/<username>")
async def get_servers(request, username: str):
    try:
        raw_servers = db.get_user_servers(username)
        cleaned_servers = []
        for s in raw_servers:
            if isinstance(s, dict):
                cleaned_servers.append({
                    "id": s.get("id", "yok"),
                    "name": s.get("name", "Bilinmeyen Sunucu"),
                    "owner": s.get("owner", "yok"),
                    "color": s.get("color", "#5865f2")
                })
            else:
                cleaned_servers.append({
                    "id": s[0] if len(s) > 0 else "yok",
                    "name": s[1] if len(s) > 1 else "Eski Sunucu",
                    "owner": s[2] if len(s) > 2 else "yok",
                    "color": s[3] if len(s) > 3 else "#5865f2"
                })
        return response.json(cleaned_servers)
    except:
        return response.json([])

@app.post("/channel/create")
async def create_channel(request):
    server_id = request.args.get("server_id") or request.form.get("server_id")
    name = request.args.get("name") or request.form.get("name")
    cid = db.create_channel(server_id, name)
    return response.json({"ok": True, "channel_id": cid})

@app.get("/channels/<server_id>")
async def get_channels(request, server_id: str):
    try:
        return response.json(db.get_channels(server_id))
    except:
        return response.json([])

@app.delete("/channel/delete/<channel_id>")
async def delete_channel(request, channel_id: str):
    db.delete_channel(channel_id)
    return response.json({"ok": True})

@app.post("/invite/create")
async def create_invite(request):
    server_id = request.args.get("server_id") or request.form.get("server_id")
    invite_code = db.create_invite(server_id)
    return response.json({"ok": True, "invite": invite_code})

@app.post("/server/join")
async def join_server(request):
    code = request.args.get("code") or request.form.get("code")
    username = request.args.get("username") or request.form.get("username")
    res = db.join_server(code, username)
    if not res:
        return response.json({"ok": False, "error": "Geçersiz davet kodu."}, status=404)
    return response.json({"ok": True, "server_id": res["server_id"], "server_name": res["server_name"]})

if __name__ == "__main__":
    # CRITICAL RAILWAY PORT BINDING
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
