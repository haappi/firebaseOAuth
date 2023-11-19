"""
    Copyright (C) 2023  haappi

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import os
import traceback
import typing
from urllib.parse import urlparse

import pymongo
from cryptography.fernet import Fernet, InvalidToken
from dotenv import load_dotenv
from fastapi import HTTPException
from google.auth import jwt
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response

from database import MongoSingleton, AiohttpSingleton

load_dotenv()

cipher_suite = Fernet(os.getenv("ENCRYPTION_KEY"))

if typing.TYPE_CHECKING:
    pass

print(os.environ)

async def get_mongo_instance() -> pymongo.MongoClient:
    return await MongoSingleton.get_instance()


def base_url(request: Request) -> str:
    return f"{os.getenv('PROD')}://{request.headers.get('host')}"


def encrypt_secret(secret: str) -> str:
    if not secret:
        return ""
    return cipher_suite.encrypt(secret.encode("utf-8")).decode("utf-8")


def decrypt_secret(secret: str) -> str:
    if not secret:
        return ""
    try:
        return cipher_suite.decrypt(secret.encode("utf-8")).decode("utf-8")
    except InvalidToken:
        raise HTTPException(status_code=500, detail="Invalid encryption key")


def parse_url(url: str) -> str:
    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"


async def fetch_google_creds():
    session = await AiohttpSingleton.get_instance()
    response = await session.get(
        "https://www.googleapis.com/oauth2/v1/certs",
    )
    response_json = await response.json()
    return response_json


async def verify_google_jwt(token, client_id):
    try:
        decoded_token = jwt.decode(
            token,
            await fetch_google_creds(),
            audience=client_id,
            clock_skew_in_seconds=30,
        )
        return decoded_token
    except Exception as e:
        traceback.print_tb(e.__traceback__)
        raise HTTPException(status_code=401, detail="Invalid token")


async def refresh_users_token(request: Request, refresh_token: str, response: Response):
    token_url = "https://accounts.google.com/o/oauth2/token"
    data = {
        "refresh_token": refresh_token,
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "grant_type": "refresh_token",
    }
    client = await AiohttpSingleton.get_instance()

    refresh_response = await client.post(token_url, data=data)

    if refresh_response.status != 200:
        return RedirectResponse(url=f"{base_url(request)}/school/oauth/login", status_code=307)

    refresh_response_json = await refresh_response.json()

    response.set_cookie(
        "refresh_token", encrypt_secret(refresh_token), httponly=True, secure=True
    )
    response.set_cookie(
        "jwt",
        encrypt_secret(refresh_response_json.get("id_token")),
        httponly=True,
        secure=True,
    )

    return refresh_response_json
