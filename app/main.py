from fastapi import FastAPI
from app.db.postgres import engine
from app.db.redis import redis_client


app = FastAPI(title="TS")


@app.on_event("startup")
async def startup():
    # Проверка подключения к Redis
    await redis_client.ping()

    # Проверка подключения к Postgres
    async with engine.begin() as conn:
        await conn.run_sync(lambda _: None)


@app.get("/health")
async def health():
    return {"status": "ok"}