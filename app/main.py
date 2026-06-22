from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routers import search
from app.database import pool


@asynccontextmanager
async def lifespan(app: FastAPI):
    pool.open()
    yield
    pool.close()
app = FastAPI(lifespan=lifespan)


app.include_router(search.router)
# app.include_router(get_token.router)
