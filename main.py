from fastapi import FastAPI
from authentication import authentication

app = FastAPI()

app.include_router(authentication.router)