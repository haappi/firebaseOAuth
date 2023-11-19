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

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response

from POPO.User import User
from database import AiohttpSingleton
from utils import encrypt_secret, base_url

load_dotenv()

router = APIRouter()


@router.get("/login")
async def login_google(request: Request):
    return RedirectResponse(
        url=f"https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={os.getenv('GOOGLE_CLIENT_ID')}&redirect_uri={base_url(request)}/school/oauth/auth&scope=openid%20profile%20email&access_type=offline",
        status_code=301,
    )


@router.get("/auth")
async def auth_google(code: str, request: Request, response: Response):
    token_url = "https://accounts.google.com/o/oauth2/token"
    data = {
        "code": code,
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "redirect_uri": f"{base_url(request)}/school/oauth/auth",
        "grant_type": "authorization_code",
    }
    client = await AiohttpSingleton.get_instance()

    auth_token = await client.post(token_url, data=data)
    auth_token_json = await auth_token.json()
    access_token = auth_token_json.get("access_token")
    user_info = await client.get(
        "https://www.googleapis.com/oauth2/v1/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    user_info_json = await user_info.json()
    print(user_info_json)
    if "hd" not in user_info_json:
        user_info_json["hd"] = user_info_json["email"].split("@")[-1]
    if user_info_json["hd"] not in os.getenv("ALLOWED_DOMAINS"):
        return HTTPException(
            status_code=403, detail="Your domain is not allowed to access this site."
        )

    user = User(
        user_id=user_info_json["id"],
        email=user_info_json["email"],
        name=user_info_json["name"],
        secrets=[],
        limit=1,
    )
    await user.save()

    response.set_cookie(
        "refresh_token",
        encrypt_secret(auth_token_json.get("refresh_token")),
        httponly=True,
        secure=True,
    )
    response.set_cookie(
        "jwt",
        encrypt_secret(auth_token_json.get("id_token")),
        httponly=True,
        secure=True,
    )
    return RedirectResponse(url=f"{base_url(request)}/school/dashboard", status_code=307)
