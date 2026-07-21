import sqlite3
import uuid

DB_NAME = "fireglis.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Kullanıcılar Tablosu
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT
        )
    """)
    
    # Sunucular Tablosu (color kolonu eklendi)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS servers (
            id TEXT PRIMARY KEY,
            name TEXT,
            owner TEXT,
            color TEXT
        )
    """)
    
    # Kanallar Tablosu
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS channels (
            id TEXT PRIMARY KEY,
            server_id TEXT,
            name TEXT,
            FOREIGN KEY(server_id) REFERENCES servers(id)
        )
    """)
    
    # Davet Kodları Tablosu
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invites (
            code TEXT PRIMARY KEY,
            server_id TEXT,
            FOREIGN KEY(server_id) REFERENCES servers(id)
        )
    """)
    
    # Sunucu Üyeleri Tablosu (Kullanıcıların katıldığı sunucular)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS server_members (
            server_id TEXT,
            username TEXT,
            PRIMARY KEY(server_id, username)
        )
    """)
    
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
    
    # Sunucuyu ekle
    cursor.execute("INSERT INTO servers (id, name, owner, color) VALUES (?, ?, ?, ?)", (server_id, name, owner, color))
    # Sunucuyu kuran kişiyi otomatik üye yap
    cursor.execute("INSERT INTO server_members (server_id, username) VALUES (?, ?)", (server_id, owner))
    
    # Sunucuya otomatik olarak bir "genel" yazı kanalı aç
    channel_id = str(uuid.uuid4())
    cursor.execute("INSERT INTO channels (id, server_id, name) VALUES (?, ?, ?)", (channel_id, server_id, "genel"))
    
    conn.commit()
    conn.close()
    return server_id

def get_user_servers(username):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.id, s.name, s.owner, s.color 
        FROM servers s
        JOIN server_members sm ON s.id = sm.server_id
        WHERE sm.username = ?
    """, (username,))
    servers = [dict(row) for row in cursor.fetchall()]
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
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, server_id, name FROM channels WHERE server_id = ?", (server_id,))
    channels = [dict(row) for row in cursor.fetchall()]
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
    code = str(uuid.uuid4())[:8] # 8 karakterli kısa kod
    cursor.execute("INSERT INTO invites (code, server_id) VALUES (?, ?)", (code, server_id))
    conn.commit()
    conn.close()
    return f"fireglis.gg/{code}"

def join_server(code, username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Davet kodunu sorgula
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
        pass # Zaten üyeyse hata verme
    
    # Katılınan sunucu bilgilerini çek
    cursor.execute("SELECT name FROM servers WHERE id = ?", (server_id,))
    server_name = cursor.fetchone()[0]
    conn.close()
    
    return {"server_id": server_id, "server_name": server_name}

# İlk çalıştırmada veritabanını hazırla
init_db()
