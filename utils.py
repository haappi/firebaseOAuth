import os
import typing
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
async def get_keys_from_uuid(uuid: UUID) -> "Secrets" or None:
    from POPO.Secrets import Secrets
    mongo = await get_mongo_instance()
    db = mongo[os.getenv("MONGO_DB_NAME")]
    collection = db["secrets"]
    document = await collection.find_one({"uuid": str(uuid)})
    if not document:
        return None
    for key, value in document.items():
        if "client" in key:
            document[key] = await decrypt_secret(value)
    return Secrets(**document)


async def insert_key(uuid: UUID, secret: "Secrets"):
    mongo = await get_mongo_instance()
    db = mongo[os.getenv("MONGO_DB_NAME")]
    collection = db["secrets"]
    document = secret.model_dump()
    for key, value in document.items():
        if "client" in key:
            document[key] = await encrypt_secret(value)
    document["uuid"] = str(uuid)
    await collection.insert_one(document)


async def encrypt_secret(secret: str) -> str:
    return cipher_suite.encrypt(secret.encode("utf-8")).decode("utf-8")


async def decrypt_secret(secret: str) -> str:
    try:
        return cipher_suite.decrypt(secret.encode("utf-8")).decode("utf-8")
    except InvalidToken:
        raise HTTPException(status_code=500, detail="Invalid encryption key")
