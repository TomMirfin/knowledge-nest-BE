from fastapi import FastAPI
from routes.app import router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "https://skillshare-app.onrender.com/",
    "http://localhost/",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
