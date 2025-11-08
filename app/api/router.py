from fastapi import APIRouter

from app.api.routes import activities, buildings, organizations

api_router = APIRouter()
api_router.include_router(buildings.router)
api_router.include_router(activities.router)
api_router.include_router(organizations.router)
