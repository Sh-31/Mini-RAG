from fastapi import FastAPI
from routes import base, data
from motor.motor_asyncio import AsyncIOMotorClient
from helpers import get_settings

app = FastAPI()

@app.on_event("startup")
async def startup_db_client():
    settings = get_settings()
    app.mongodb = AsyncIOMotorClient(settings.MONGODB_URL)
    app.db = app.mongodb[settings.MONGODB_DATABASE]

@app.on_event("shutdown")
async def shutdown_db_client():
    await app.mongodb.close()

app.include_router(base.base_router)
app.include_router(data.data_router)

if __name__ == "__main__":
    
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)