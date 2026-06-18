from fastapi import FastAPI
from app.routers import search, status
from app.schema import create_schema

create_schema()

app = FastAPI()




app.include_router(search.router)
app.include_router(status.router)