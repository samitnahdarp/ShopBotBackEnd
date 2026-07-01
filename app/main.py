from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routers import auth, search,first
from app.database import pool
from app.workers.session_cleaner import cleanup_sessions
from app.schemas.database_schema import create_schema
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    pool.open()
    create_schema();
    scheduler.add_job(cleanup_sessions, 'interval', minutes=30) 
    scheduler.start()
    yield
    scheduler.shutdown()
    pool.close()

app = FastAPI(lifespan=lifespan)


app.include_router(search.router)
app.include_router(first.index)
app.include_router(auth.auth)
