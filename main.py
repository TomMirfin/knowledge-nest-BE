from fastapi import FastAPI
from routes.app import router

app = FastAPI()

app.include_router(router)
