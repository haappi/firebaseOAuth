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
from fastapi import FastAPI, Cookie
from google.auth.exceptions import InvalidValue
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response

from database import AiohttpSingleton
from routes import router as oauth_router
from utils import verify_google_jwt, encrypt_secret, decrypt_secret, refresh_users_token

app = FastAPI()
load_dotenv()
app.include_router(oauth_router)


@app.get("/test")
async def test(response: Response, request: Request, jwt: str | None = Cookie(None)):
    if not jwt:
        return RedirectResponse(url=f"/school/oauth/login", status_code=307)
    try:
        await verify_google_jwt(decrypt_secret(jwt), os.getenv("GOOGLE_CLIENT_ID"))
    except InvalidValue:
        if not request.cookies.get('refresh_token'):
            return RedirectResponse(url=f"/school/oauth/login", status_code=307)
        await refresh_users_token(request, decrypt_secret(request.cookies.get('refresh_token')), response)


@app.get("/school/oauth/login")
async def login_google(request: Request):
    return RedirectResponse(
        url=f"https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={os.getenv('GOOGLE_CLIENT_ID')}&redirect_uri={request.url.scheme}://{request.url.netloc}/school/oauth/auth&scope=openid%20profile%20email&access_type=offline",
        status_code=307,
    )


@app.get("/school/oauth/auth")
async def auth_google(code: str, request: Request, response: Response):
    token_url = "https://accounts.google.com/o/oauth2/token"
    data = {
        "code": code,
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "redirect_uri": f"{request.url.scheme}://{request.url.netloc}/school/oauth/auth",
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

    response.set_cookie("refresh_token", encrypt_secret(auth_token_json.get('refresh_token')), httponly=True, secure=True)
    response.set_cookie("jwt", encrypt_secret(auth_token_json.get('id_token')), httponly=True, secure=True)
    return user_info_json


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
