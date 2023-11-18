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

from fastapi import APIRouter

from ppo.routes.dashboard import router as dashboard_router
from ppo.routes.onboarding import router as onboarding_router
from ppo.routes.redirect_handler import router as redirect_router

router = APIRouter(prefix="/school/oauth")

router.include_router(redirect_router)
router.include_router(dashboard_router)
router.include_router(onboarding_router)
