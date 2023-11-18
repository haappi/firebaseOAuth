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
