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
from typing import Any

from bson import ObjectId
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from utils import get_mongo_instance

load_dotenv()


class User(BaseModel):
    user_id: str
    email: str
    name: str
    secrets: list[str]
    limit: int

    admin: bool = False

    def model_dump(self, *args, **kwargs):
        return super().model_dump(*args, **kwargs, by_alias=True)

    async def save(self):
        mongo = await get_mongo_instance()
        db = mongo[os.getenv("MONGO_DB_NAME")]
        collection = db["users"]
        document = self.model_dump()

        await collection.update_one({"user_id": self.user_id}, {"$set": document}, upsert=True)

    @staticmethod
    async def retrieve_user(user_id: str) -> "User" or None:
        mongo = await get_mongo_instance()
        db = mongo[os.getenv("MONGO_DB_NAME")]
        collection = db["users"]
        document = await collection.find_one({"user_id": user_id})
        if not document:
            return None

        return User(**document)

    @staticmethod
    async def get_all_users() -> list["User"]:
        mongo = await get_mongo_instance()
        db = mongo[os.getenv("MONGO_DB_NAME")]
        collection = db["users"]
        documents = collection.find({})
        return [User(**document) for document in documents if document]