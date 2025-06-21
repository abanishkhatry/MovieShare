from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
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

"""
This helps to make our image files accessible over the web through your FastAPI app.
app.mount(...) tells FastAPI that make static folders from a certain folder to be accessible 
at a specific URL path. 
/uploads: serves as a URL prefix
StaticFiles(directory="server/app/images"): tells FastAPI where on your server the actual files are stored. 
name = "uploads": This gives a name to this mounted static route. You don’t really use this unless you're doing 
reverse routing or want to reference this route elsewhere in FastAPI.

So, now : 
http://localhost:8000/uploads/avatars/avatar_123.png -> server/app/images/avatars/avatar_123.png

"""
app.mount("/uploads", StaticFiles(directory="server/app/images"), name="uploads")

@app.get("/")
def read_root():
    return {"message": "Welcome to the MovieShare API!"}