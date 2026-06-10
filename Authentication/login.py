from fastapi import APIRouter
from argon2 import PasswordHasher

router = APIRouter(
    prefix = '/login',
    tags = ['Login']
)

passwordHasher = PasswordHasher()

