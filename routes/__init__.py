from fastapi import APIRouter

from routes.redirect import router as redirect_router

router = APIRouter()

router.include_router(redirect_router)
