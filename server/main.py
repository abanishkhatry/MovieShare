from fastapi import FastAPI
from app.routes import router
from app.database import engine
from app import models

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the MovieShare API!"}