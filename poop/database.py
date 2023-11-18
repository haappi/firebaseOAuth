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

import aiohttp
import motor.motor_asyncio
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")


class MongoSingleton:
    _instance: typing.Optional[motor.motor_asyncio.AsyncIOMotorClient] = None

    def __new__(cls):
        raise NotImplementedError("Cannot instantiate a singleton class.")

    @classmethod
    async def get_instance(cls) -> motor.motor_asyncio.AsyncIOMotorClient:
        if not cls._instance:
            cls._instance = await cls._connect_to_mongo()
        return cls._instance

    @staticmethod
    async def _connect_to_mongo() -> motor.motor_asyncio.AsyncIOMotorClient:
        return motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)

    @classmethod
    async def close_mongo_connection(cls):
        if cls._instance:
            await cls._instance.close()
            cls._instance = None


class AiohttpSingleton:
    _instance: typing.Optional[aiohttp.ClientSession] = None

    def __new__(cls):
        raise NotImplementedError("Cannot instantiate a singleton class.")

    @classmethod
    async def get_instance(cls) -> aiohttp.ClientSession:
        if not cls._instance:
            cls._instance = await cls._connect_to_aiohttp()
        return cls._instance

    @staticmethod
    async def _connect_to_aiohttp() -> aiohttp.ClientSession:
        return aiohttp.ClientSession()

    @classmethod
    async def close_aiohttp_connection(cls):
        if cls._instance:
            await cls._instance.close()
            cls._instance = None
