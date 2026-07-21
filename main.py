from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import requests
import os

app = FastAPI()

CLIENT_ID = "DISCORD_APPLICATION_ID"
CLIENT_SECRET = "DISCORD_CLIENT_SECRET"

REDIRECT_URI = "https://senin-site.onrender.com/callback"


@app.get("/")
def home():
    return """
    <h1>Discord Widget Auth</h1>
    <a href="/login">Discord ile giriş yap</a>
    """


@app.get("/login")
def login():
    url = (
        "https://discord.com/oauth2/authorize"
        f"?client_id={CLIENT_ID}"
        "&response_type=code"
        f"&redirect_uri={REDIRECT_URI}"
        "&scope=identify"
    )

    return HTMLResponse(f'<a href="{url}">Discord ile giriş</a>')


@app.get("/callback")
def callback(code: str):

    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    token = requests.post(
        "https://discord.com/api/oauth2/token",
        data=data,
        headers=headers
    ).json()

    access_token = token["access_token"]

    user = requests.get(
        "https://discord.com/api/users/@me",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    ).json()

    return user