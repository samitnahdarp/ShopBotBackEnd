from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routers import auth, search,profile
from app.database import pool
from app.workers.session_cleaner import cleanup_sessions
from app.schemas.database_schema import create_schema
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.workers.product_cleaner import cleanup_products
from app.workers.price_tracker import price_collector

scheduler = AsyncIOScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    pool.open()
    create_schema();
    scheduler.add_job(cleanup_sessions, 'interval', minutes=30) 
    scheduler.add_job(cleanup_products, 'interval', hours=3)
    scheduler.add_job(price_collector, 'interval', hours=5)
    scheduler.start()
    yield
    scheduler.shutdown()
    pool.close()
app = FastAPI(lifespan=lifespan)


app.include_router(search.router)
app.include_router(auth.auth)
app.include_router(profile.profile)
