from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import models, schemas, database, auth
from typing import Optional
from sqlalchemy import or_



router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)

@router.post("/", response_model=schemas.PostOut)
def create_post(
    post: schemas.PostCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    new_post = models.Post(**post.dict(), owner_id=current_user.id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

# this returns all the posts even if they don't belong to you, like in the explore page of Insta 
@router.get("/", response_model=list[schemas.PostOut])
def get_posts(
    search: Optional[str] = None,
    sort: Optional[str] = "newest",
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(database.get_db),    
    ):
    query = db.query(models.Post)
    # Apply filter if search is provided
    if search:
        # or_ allows filtering based on either condition
        query = query.filter(
            or_(
                models.Post.title.ilike(f"%{search}%"),
                models.Post.content.ilike(f"%{search}%")
            )
        )
    # By default, returns posts in descending order , i.e. from latest ---> oldest    
    if sort == "oldest":
        query = query.order_by(models.Post.created_at.asc())
    else:
        query = query.order_by(models.Post.created_at.desc())    
    
    query = query.offset(offset).limit(limit) 
    return query.all()

# This function checks if a requested post exists or not. 
def get_post_or_404(post_id: int, db: Session):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found.")
    return post

# This function allow a user to update a post only if they are the owner
@router.put("/{post_id}", response_model=schemas.PostOut)
def update_post(
    post_id: int,
    updated_post: schemas.PostCreate,        # the incoming data from the client — title and content.
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    post = get_post_or_404(post_id, db)

    if post.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not authorized to update this post.")

    post.title = updated_post.title
    post.content = updated_post.content

    # updating these changes in the database
    db.commit()
    db.refresh(post)

    return post

# This function allows user to delete only their own posts, and return proper errors for others.
@router.delete("/{post_id}", status_code=204)
def delete_post(
    post_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    post = get_post_or_404(post_id, db)

    if post.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not authorized to delete this post.")
    
    # making this update in the database
    db.delete(post)
    db.commit()
    return

# This helps to return all the post owned by the user.
@router.get("/me", response_model=list[schemas.PostOut])
def get_my_posts(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return db.query(models.Post).filter(models.Post.owner_id == current_user.id).all()
