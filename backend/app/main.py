from fastapi import FastAPI

from core.exceptions import *

app = FastAPI(title="Hortas e Viveiros Comunitários - API")
registrar_handlers(app)