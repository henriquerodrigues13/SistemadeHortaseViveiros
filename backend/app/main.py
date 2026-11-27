from fastapi.middleware.cors import CORSMiddleware
from core.config import Settings
from fastapi import FastAPI
from core.exceptions import *

app = FastAPI(title="Hortas e Viveiros Comunitários - API")
registrar_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=Settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)