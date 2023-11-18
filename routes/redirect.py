import uuid
from typing import Callable

from fastapi import APIRouter, Depends, HTTPException
from fastapi.routing import APIRoute
from uuid import UUID
from starlette.requests import Request

from POPO.Secrets import Secrets
from utils import insert_key, get_keys_from_uuid

router = APIRouter()

database = {
    "some_uuid": {"secret_key": "some_secret_key", "client_id": "some_client_id"},
    # Add more UUIDs and their corresponding keys and client IDs
}


async def get_key_and_client_id(uuid: UUID = Depends()):
    if str(uuid) in database:
        return database[str(uuid)]
    else:
        raise HTTPException(status_code=404, detail="Redirect URI not found")


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
async def redirect_to_school_oauth(uuid: UUID = Depends(get_key_and_client_id)):
    # secret_key = key_and_client_id["secret_key"]
    # client_id = key_and_client_id["client_id"]
    # return {"uuid": str(uuid), "secret_key": secret_key, "client_id": client_id}
    return {"uuid": str(uuid)}


