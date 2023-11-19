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
from dotenv import load_dotenv
from fastapi import FastAPI
from starlette.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.cors import CORSMiddleware

from routes import router as oauth_router

app = FastAPI()

app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*.quack.boo", "localhost"])
origins = [
    "https://*.quack.boo",
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(oauth_router)

if __name__ == "__main__":
    load_dotenv()
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
