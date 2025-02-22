from fastapi import APIRouter
from app.api.dartutil import dartapi

api_router = APIRouter()

api_router.include_router(dartapi.router, prefix="/dart", tags=["dart"])
