from fastapi import APIRouter, HTTPException, Depends, status, File, UploadFile 
from passlib.context import CryptContext
from sqlalchemy.orm import Session 
from uuid import uuid4
import os
from .. import models, auth, database, schemas

# Creates a new router that can be included in your main app
router = APIRouter()
# Sets up bcrypt (industry-standard) as your password hashing algorithm
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = auth.hash_password(user.password)
    new_user = models.User(
        username=user.username,
        email=user.email,
        password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"msg": "User registered successfully!"}


@router.post("/login")
# OAuth2PasswordRequestForm takes in username and password from the form. Here, username holds the email.
def login_user(form_data: schemas.UserLogin, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.email).first()
    print(user.password)
    
    if not user:
        raise HTTPException(status_code=400, detail="Invalid email")

    if not auth.verify_password(form_data.password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    
    access_token_expires = 30
    access_token = auth.create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me")
def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    return {
        "username": current_user.username,
        "email": current_user.email,
        "created_at": current_user.created_at
    }

@router.get("/dashboard")
# Depends(get_current_user) extracts and verifies the JWT token
def dashboard(current_user: models.User = Depends(auth.get_current_user)):
    return {
        "message": f"Welcome to your dashboard, {current_user.username}!",
        "email": current_user.email,
        "joined": current_user.created_at
    }

@router.get("/me/profile", response_model=schemas.UserProfileOut)
def get_my_profile(
    current_user: models.User = Depends(auth.get_current_user)
):
    return current_user

@router.patch("/me/profile", response_model = schemas.UserProfileOut)
def update_my_profile(
    update_data: schemas.UserProfileUpdate, 
    db: Session = Depends(database.get_db), 
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    If user wants to update their bio and favourite_genre, then update_data will hold that 
    new schema. Then, we first covert that schema to a dic so that we can iterate through them 
    as key value pairs. Here, field will be bio and favourite_genre and value will hold their 
    respective values in each iteration. 
    """

    for field, value in update_data.dict(exclude_unset= True).items():
        # equivalent to current_user.field = value, so it modifies the User Model 
        # Eg: current_user.bio = "Thriller addict"
        setattr(current_user, field, value)    

    db.commit()
    db.refresh(current_user)
    return current_user

@router.post("/me/avatar", status_code = 200)
def upload_avatar(
    file: UploadFile = File(...), 
    db: Session = Depends(database.get_db), 
    current_user : models.User = Depends(auth.get_current_user)
): 
 # checking for it the upload is a type of image i.e. image/jpeg, image/png
 if not file.content_type.startswith("image/"):
    raise HTTPException(status_code=400, detail="File must be an image.")
 # this is extracting the image extension like png, jpg, jpeg
 file_ext = os.path.splitext(file.filename)[1]  
 # giving a new file name to that image
 filename = f"avatar_{uuid4().hex}{file_ext}" 
 # placing that img with new name into the avatars folder. 
 file_path = os.path.join("../images/avatars", filename)

 """
    Now saving the file into the path we defined earlier, 
    Since its not a plain text file, we use wb -> write binary mode

    Here we are referring to a new file in that path as f and then 
    we are reading the binary data of the file/image uploaded by the 
    user. i.e. file.file.read() 

    Then we are writing that binary code into that new file and saving it. 
    So, f will now hold the image uploaded by user , in our defined file path
 """
 with open(file_path, "wb") as f: 
    f.write(file.file.read())
     # Store URL path in database (relative for now)
     
 current_user.avatar_url = f"/{file_path}"
 db.commit()
 db.refresh(current_user)

 return {"message": "Avatar uploaded!", "avatar_url": current_user.avatar_url}



@router.get("/api/status")
def status():
 return {"status": "Backend is running"}

