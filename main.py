from fastapi import FastAPI
from authentication import users, login

app = FastAPI()

app.include_router(users.router)
app.include_router(login.router)