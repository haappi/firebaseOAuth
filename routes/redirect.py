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

from typing import Callable
from uuid import UUID

import firebase_admin
from fastapi import APIRouter, Depends, HTTPException
from fastapi.routing import APIRoute
from firebase_admin import credentials, auth
from firebase_admin.auth import UserNotFoundError
from firebase_admin.exceptions import FirebaseError
from starlette.requests import Request
from starlette.responses import RedirectResponse

from POPO.Secrets import Secrets
from database import AiohttpSingleton
from utils import get_keys_from_uuid, parse_url

router = APIRouter()


async def get_keys(uuid: UUID) -> Secrets:
    data = await get_keys_from_uuid(uuid, decrypt=True)
    if not data:
        raise HTTPException(status_code=404, detail="Redirect URI not found")
    return data


def extract_uuid_from_path(request: Request):
    path = request.url.path
    try:
        return UUID(path.split("/")[-1])
    except ValueError:
        raise HTTPException(status_code=404, detail="Malformed UUID")


class CustomRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request):
            request.state.uuid = extract_uuid_from_path(request)
            return await original_route_handler(request)

        return custom_route_handler


router.route_class = CustomRoute


@router.get("/school/oauth/redirect/{uuid}")
async def redirect_to_school_oauth(
    request: Request, code: str, data: Secrets = Depends(get_keys)
):
    return await handle_oauth(
        code=code,
        client_id=data.client_id,
        client_secret=data.client_secret,
        redirect_uri=parse_url(str(request.url)),
        firebase_client_secret=data.firebase_client_secret,
    )


@router.get("/school/oauth/refresh/{uuid}/{refresh_token}")
async def refresh_users_token(
    request: Request, refresh_token: str, data: Secrets = Depends(get_keys)
):
    token_url = "https://accounts.google.com/o/oauth2/token"
    data = {
        "refresh_token": refresh_token,
        "client_id": data.client_id,
        "client_secret": data.client_secret,
        "grant_type": "refresh_token",
    }
    client = await AiohttpSingleton.get_instance()

    response = await client.post(token_url, data=data)
    response_json = await response.json()

    access_token = response_json.get("access_token")
    user_info = await client.get(
        "https://www.googleapis.com/oauth2/v1/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    user_info_json = await user_info.json()

    return_string = "exp://"

    for key, value in user_info_json.items():
        return_string += f"?{key}={value}&"

    return_string = return_string[:-1]

    return RedirectResponse(url=return_string, status_code=301)


def generate_firebase_login_token(firebase_secret: dict, user: str, **kwargs) -> str:
    is_email = "@" in user
    cred = credentials.Certificate(firebase_secret)
    app = firebase_admin.initialize_app(cred)
    try:
        if is_email:
            user = auth.get_user_by_email(user, app=app)
        else:  # uid
            user = auth.get_user(user, app=app)
    except (ValueError, UserNotFoundError, FirebaseError):
        user = auth.create_user(
            email=kwargs.get("email"),
            email_verified=kwargs.get("verified_email"),
            disabled=False,
            display_name=kwargs.get("name"),
            app=app,
        )

    return auth.create_custom_token(user.uid).decode("utf-8")


async def handle_oauth(**kwargs):
    token_url = "https://accounts.google.com/o/oauth2/token"
    data = {
        "code": kwargs.get("code"),
        "client_id": kwargs.get("client_id"),
        "client_secret": kwargs.get("client_secret"),
        "redirect_uri": kwargs.get("redirect_uri"),
        "grant_type": "authorization_code",
    }
    client = await AiohttpSingleton.get_instance()

    response = await client.post(token_url, data=data)
    response_json = await response.json()

    access_token = response_json.get("access_token")
    user_info = await client.get(
        "https://www.googleapis.com/oauth2/v1/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    user_info_json = await user_info.json()

    return_string = "exp://"

    for key, value in user_info_json.items():
        return_string += f"?{key}={value}&"

    return_string += f"firebase_token={generate_firebase_login_token(kwargs.get('firebase_client_secret'), user_info_json.get('email'), **user_info_json)}&"

    return_string = return_string[:-1]

    return RedirectResponse(url=return_string, status_code=301)
