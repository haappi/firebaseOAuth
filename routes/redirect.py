from typing import Callable
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.routing import APIRoute
from starlette.requests import Request

from utils import get_keys_from_uuid

router = APIRouter()


async def get_key_and_client_id(uuid: UUID):
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


@router.get("/redirect/{uuid}")
async def redirect_to_school_oauth(uuid: str = Depends(get_key_and_client_id)):
    # secret_key = key_and_client_id["secret_key"]
    # client_id = key_and_client_id["client_id"]
    # return {"uuid": str(uuid), "secret_key": secret_key, "client_id": client_id}
    return {"uuid": str(uuid)}
