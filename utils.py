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
import typing
from urllib.parse import urlparse
from uuid import UUID

import pymongo
from aiocache import cached
from cryptography.fernet import Fernet, InvalidToken
from dotenv import load_dotenv
from fastapi import HTTPException

from database import MongoSingleton

load_dotenv()

cipher_suite = Fernet(os.getenv("ENCRYPTION_KEY"))

if typing.TYPE_CHECKING:
    from POPO.Secrets import Secrets

load_dotenv()


async def get_mongo_instance() -> pymongo.MongoClient:
    return await MongoSingleton.get_instance()


@cached(ttl=60)
async def get_keys_from_uuid(uuid: UUID, decrypt=False) -> "Secrets" or None:
    from POPO.Secrets import Secrets

    mongo = await get_mongo_instance()
    db = mongo[os.getenv("MONGO_DB_NAME")]
    collection = db["secrets"]
    document = await collection.find_one({"uuid": str(uuid)})
    if not document:
        return None

    if decrypt:
        for key, value in document.items():
            if "client" in key:
                document[key] = await decrypt_secret(value)

        for key, value in document["firebase_secret"].items():
            document["firebase_secret"][key] = await decrypt_secret(value)

    return Secrets(**document)


async def insert_key(uuid: UUID, secret: "Secrets"):
    mongo = await get_mongo_instance()
    db = mongo[os.getenv("MONGO_DB_NAME")]
    collection = db["secrets"]
    document = secret.model_dump()
    for key, value in document.items():
        if "client" in key:
            document[key] = await encrypt_secret(value)
    for key, value in document["firebase_secret"].items():
        document["firebase_secret"][key] = await encrypt_secret(value)
    document["uuid"] = str(uuid)
    await collection.insert_one(document)


async def encrypt_secret(secret: str) -> str:
    return cipher_suite.encrypt(secret.encode("utf-8")).decode("utf-8")


async def decrypt_secret(secret: str) -> str:
    try:
        return cipher_suite.decrypt(secret.encode("utf-8")).decode("utf-8")
    except InvalidToken:
        raise HTTPException(status_code=500, detail="Invalid encryption key")


def parse_url(url: str) -> str:
    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
