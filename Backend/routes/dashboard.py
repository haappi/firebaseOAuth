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
import uuid
from uuid import UUID

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, Cookie, HTTPException
from google.auth.exceptions import InvalidValue
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response

from ppo.POPO.Secrets import Secrets
from ppo.POPO.User import User
from ppo.utils import decrypt_secret, verify_google_jwt, refresh_users_token

load_dotenv()

router = APIRouter()


async def get_current_user(
    response: Response, request: Request, jwt: str = Cookie(None)
):
    if not jwt:
        return RedirectResponse(url=f"/school/oauth/login", status_code=307)
    try:
        jwt: dict = await verify_google_jwt(
            decrypt_secret(jwt), os.getenv("GOOGLE_CLIENT_ID")
        )
    except InvalidValue:
        await refresh_users_token(
            request, decrypt_secret(request.cookies.get("refresh_token")), response
        )

    return await User.retrieve_user(jwt["sub"])


async def is_admin(current_user: User = Depends(get_current_user)):
    if not current_user.admin:
        raise HTTPException(status_code=403, detail="Forbidden")
    return current_user


@router.get("/dashboard")
async def dashboard_view(
    response: Response,
    request: Request,
    current_user: User | RedirectResponse = Depends(get_current_user),
):
    if isinstance(current_user, RedirectResponse):
        return current_user
    return {
        "user": current_user.model_dump(),
        "secrets": await Secrets.get_secrets_for_user(current_user.user_id),
    }


@router.get("/dashboard/{uuid}")
async def secret_view(
    response: Response,
    request: Request,
    uuid: str,
    current_user: User | RedirectResponse = Depends(get_current_user),
):
    if isinstance(current_user, RedirectResponse):
        return current_user
    try:
        uuid = UUID(uuid)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID")
    secret = await Secrets.get_secret_from_uuid(uuid)
    if not secret:
        raise HTTPException(status_code=404, detail="Secret not found")
    if secret.owner != current_user.user_id:
        if not current_user.admin:
            raise HTTPException(status_code=403, detail="Forbidden")
    return {"secret": secret.model_dump()}


@router.delete("/dashboard/{uuid}")
async def delete_secret(
    response: Response,
    request: Request,
    uuid: str,
    current_user: User | RedirectResponse = Depends(get_current_user),
):
    if isinstance(current_user, RedirectResponse):
        return current_user
    try:
        uuid = UUID(uuid)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID")
    secret = await Secrets.get_secret_from_uuid(uuid)
    if not secret:
        raise HTTPException(status_code=404, detail="Secret not found")
    if secret.owner != current_user.user_id:
        if not current_user.admin:
            raise HTTPException(status_code=403, detail="Forbidden")
    await secret.delete()
    return {"message": "Secret deleted"}


@router.post("/dashboard/create")
async def create_secret(
    response: Response,
    request: Request,
    current_user: User | RedirectResponse = Depends(get_current_user),
):
    if isinstance(current_user, RedirectResponse):
        return current_user
    if len(current_user.secrets) >= current_user.limit:
        raise HTTPException(status_code=403, detail="Max secrets reached")
    data = await request.json()
    if not data:
        raise HTTPException(status_code=400, detail="Invalid data")
    if not data.get("client_id") or not data.get("client_secret"):
        raise HTTPException(status_code=400, detail="Invalid data")
    if not data.get("firebase_secret") and not data.get("auto_firebase"):
        raise HTTPException(status_code=400, detail="Invalid data")
    if data.get("auto_firebase"):
        data["firebase_secret"] = await Secrets.generate_firebase_secret()
    secret = Secrets(**data)
    secret.owner = current_user.user_id
    secret = await Secrets.insert(uuid.uuid4(), secret)
    current_user.secrets.append(secret.uuid)
    return {"message": "Secret created", "secret": secret.model_dump()}


@router.get("/admin")
async def admin(
    response: Response,
    request: Request,
    current_user: User | RedirectResponse = Depends(is_admin),
):
    if isinstance(current_user, RedirectResponse):
        return current_user
    return {"all_users": await User.get_all_users()}


@router.get("/admin/{user_id}")
async def admin_profile_viewer(
    response: Response,
    request: Request,
    user_id: str,
    current_user: User | RedirectResponse = Depends(is_admin),
):
    if isinstance(current_user, RedirectResponse):
        return current_user
    user = await User.retrieve_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "user": user.model_dump(),
        "secrets": await Secrets.get_secrets_for_user(user.user_id),
    }


@router.delete("/admin/{user_id}")
async def admin_profile_viewer(
    response: Response,
    request: Request,
    user_id: str,
    current_user: User | RedirectResponse = Depends(is_admin),
):
    if isinstance(current_user, RedirectResponse):
        return current_user
    user = await User.retrieve_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    secrets = await Secrets.get_secrets_for_user(user.user_id)
    await user.delete()
    for secret in secrets:
        await secret.delete()
    return {"message": "User & Secrets deleted"}
