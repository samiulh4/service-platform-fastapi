from fastapi import FastAPI, APIRouter

from app.modules.authentication.routes.router import router as authentication_router 

def register_routes(app : FastAPI):

    api_router = APIRouter(prefix="/api")

    api_router.include_router(authentication_router, prefix="", tags=["Authentication"])

    app.include_router(api_router)
