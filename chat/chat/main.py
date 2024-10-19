from fastapi import FastAPI
from .auth import auth_router
from .db import Base, engine

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(auth_router, prefix="/api")
