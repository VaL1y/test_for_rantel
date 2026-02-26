from fastapi import FastAPI
from app.db.postgres import engine, get_db
from app.db.redis import redis_client
from app.api.v1.operator import router as operator_router
from app.api.v1.client import router as client_router
from app.api.v1.ticket import router as ticket_router
from app.api.v1.message import router as message_router


app = FastAPI(title="TS")


app.include_router(operator_router)
app.include_router(message_router)
app.include_router(client_router)
app.include_router(ticket_router)


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
