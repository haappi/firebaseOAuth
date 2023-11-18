import pprint
from typing import Callable
from urllib.parse import urlparse
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.routing import APIRoute
from starlette.requests import Request
from starlette.responses import RedirectResponse

from POPO.Secrets import Secrets
from database import AiohttpSingleton
from utils import get_keys_from_uuid

router = APIRouter()


async def get_keys(uuid: UUID) -> Secrets:
    data = await get_keys_from_uuid(uuid)
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
async def redirect_to_school_oauth(request: Request, code: str, data: Secrets = Depends(get_keys)):
    return await handle_oauth(
        code=code,
        client_id=data.client_id,
        client_secret=data.client_secret,
        redirect_uri=parse_url(str(request.url)),
        firebase_client_secret=data.firebase_client_secret
    )


def parse_url(url: str) -> str:
    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"


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
    pprint.pp(response_json)

    access_token = response_json.get("access_token")
    user_info = await client.get("https://www.googleapis.com/oauth2/v1/userinfo",
                                 headers={"Authorization": f"Bearer {access_token}"})
    user_info_json = await user_info.json()
    pprint.pp(user_info_json)

    return_string = "exp://"

    for key, value in user_info_json.items():
        return_string += f"?{key}={value}&"

    return_string = return_string[:-1]

    return RedirectResponse(url=return_string, status_code=301)
