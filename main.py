from fastapi import FastAPI
from Authentication import users

app = FastAPI()

app.include_router(users.router)