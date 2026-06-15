from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from authentication import users, login
from data import expenses


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(users.router)
app.include_router(login.router)