from fastapi import FastAPI

from src.routers import experiments



app = FastAPI()
app.include_router(experiments.router)