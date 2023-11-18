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
from uuid import UUID

from dotenv import load_dotenv
from pydantic import BaseModel

from ppo.utils import get_mongo_instance, encrypt_secret, decrypt_secret

load_dotenv()


class Secrets(BaseModel):
    client_id: str
    client_secret: str
    firebase_secret: dict[str, str]
    auto_firebase: bool
    owner: str
    uuid: str | None

    def model_dump(self, *args, **kwargs):
        kwargs.pop("by_alias", None)
        return super().model_dump(*args, **kwargs, by_alias=True)

    async def delete(self):
        mongo = await get_mongo_instance()
        db = mongo[os.getenv("MONGO_DB_NAME")]
        collection = db["secrets"]
        await collection.delete_one({"uuid": self.uuid})

    async def update(self):
        mongo = await get_mongo_instance()
        db = mongo[os.getenv("MONGO_DB_NAME")]
        collection = db["secrets"]
        document = self.model_dump()
        await collection.update_one(
            {"uuid": self.uuid}, {"$set": document}, upsert=True
        )

    @staticmethod
    async def get_secrets_for_user(user_id: str) -> typing.List["Secrets"]:
        mongo = await get_mongo_instance()
        db = mongo[os.getenv("MONGO_DB_NAME")]
        collection = db["secrets"]
        documents = collection.find({"owner": user_id})
        secrets = [Secrets(**document) async for document in documents if document]
        # secrets = [await i.decrypt() for i in secrets]
        return secrets

    @staticmethod
    async def get_secret_from_uuid(uuid: UUID, decrypt=False) -> "Secrets" or None:
        mongo = await get_mongo_instance()
        db = mongo[os.getenv("MONGO_DB_NAME")]
        collection = db["secrets"]
        document = await collection.find_one({"uuid": str(uuid)})
        if not document:
            return None

        if decrypt:
            for key, value in document.items():
                if "client_secret" in key:
                    document[key] = decrypt_secret(value)

            for key, value in document["firebase_secret"].items():
                document["firebase_secret"][key] = decrypt_secret(value)

        return Secrets(**document)

    async def decrypt(self):
        document = self.model_dump()
        for key, value in document.items():
            if "client_secret" in key:
                document[key] = decrypt_secret(value)

        for key, value in document["firebase_secret"].items():
            document["firebase_secret"][key] = decrypt_secret(value)

        return Secrets(**document)

    @staticmethod
    async def insert(uuid: UUID, secret: "Secrets"):
        mongo = await get_mongo_instance()
        db = mongo[os.getenv("MONGO_DB_NAME")]
        collection = db["secrets"]
        secret.uuid = str(uuid)
        document = secret.model_dump()
        for key, value in document.items():
            if "client_secret" in key:
                document[key] = encrypt_secret(value)
        for key, value in document["firebase_secret"].items():
            document["firebase_secret"][key] = encrypt_secret(value)

        document["uuid"] = str(uuid)

        await collection.insert_one(document)

        return secret
