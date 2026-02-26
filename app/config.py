import os
from dotenv import load_dotenv

from app.models.enums import TicketStatus

load_dotenv()

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "postgres")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

VALID_TRANSITIONS = {
    TicketStatus.new: {TicketStatus.in_progress, TicketStatus.resolved, TicketStatus.closed},
    TicketStatus.in_progress: {TicketStatus.waiting, TicketStatus.resolved, TicketStatus.closed},
    TicketStatus.waiting: {TicketStatus.in_progress, TicketStatus.resolved, TicketStatus.closed},
    TicketStatus.resolved: {TicketStatus.closed},
    TicketStatus.closed: set(),
}