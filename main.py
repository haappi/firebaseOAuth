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
from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import RedirectResponse

from database import AiohttpSingleton
from routes import router as oauth_router

app = FastAPI()
load_dotenv()
app.include_router(oauth_router)


@app.get("/school/oauth/login")
async def login_google(request: Request):
    return RedirectResponse(
        url=f"https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={os.getenv('GOOGLE_CLIENT_ID')}&redirect_uri={request.url.scheme}://{request.url.netloc}/school/oauth/auth&scope=openid%20profile%20email&access_type=offline",
        status_code=301)


@app.get("/school/oauth/auth")
async def auth_google(code: str, request: Request):
    token_url = "https://accounts.google.com/o/oauth2/token"
    data = {
        "code": code,
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "redirect_uri": f"{request.url.scheme}://{request.url.netloc}/school/oauth/auth",
        "grant_type": "authorization_code",
    }

    client = await AiohttpSingleton.get_instance()

    response = await client.post(token_url, data=data)
    response_json = await response.json()
    return response_json
    access_token = response_json.get("access_token")
    user_info = await client.get("https://www.googleapis.com/oauth2/v1/userinfo",
                                 headers={"Authorization": f"Bearer {access_token}"})
    user_info_json = await user_info.json()
    return user_info_json


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
