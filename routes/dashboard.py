import os

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, Cookie
from google.auth.exceptions import InvalidValue
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response

from POPO.User import User
from utils import verify_google_jwt, decrypt_secret, refresh_users_token

load_dotenv()

router = APIRouter()


async def get_current_user(response: Response, request: Request, jwt: str = Cookie(None)):
    if not jwt:
        return RedirectResponse(url=f"/school/oauth/login", status_code=307)

    try:
        jwt = await verify_google_jwt(decrypt_secret(jwt), os.getenv("GOOGLE_CLIENT_ID"))
    except InvalidValue:
        await refresh_users_token(request, decrypt_secret(request.cookies.get("refresh_token")), response)

    return jwt


@router.get("/dashboard")
async def test(response: Response, request: Request, current_user: str | RedirectResponse = Depends(get_current_user)):
    if isinstance(current_user, RedirectResponse):
        return current_user
    print(current_user)
    # Your route logic here
    user = await User.get_user(current_user['email'])
    return {"message": "You are authenticated!"}

