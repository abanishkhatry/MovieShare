from fastapi import FastAPI
from app.routes import routes
from app.database import engine
from app import models
from app.routes import post

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

# Include the existing router (probably for /signup, /login etc.)
app.include_router(routes.router)

# Include the post router
app.include_router(post.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the MovieShare API!"}