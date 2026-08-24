from fastapi import FastAPI
from app.migrations import run_migrations
from app.routes import register_routes

run_migrations()

app = FastAPI()

register_routes(app)

@app.get("/")
async def read_root():
    return {"message": "FastAPI service platform is running!"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8889, reload=False)