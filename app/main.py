from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from sqlalchemy import text
from app.core.database import Base, engine
from app.modules.user.models.users import User
from app.modules.authentication.models.users_auth_token import UserAuthToken
from app.routes import register_routes

Base.metadata.create_all(bind=engine)

app = FastAPI()

register_routes(app)

@app.get("/")
async def read_root():
    return {"message": "FastAPI service platform is running!"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8889, reload=False)