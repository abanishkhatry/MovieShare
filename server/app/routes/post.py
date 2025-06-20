from fastapi import APIRouter, Depends, HTTPException, status, Path
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
    # selects all the posts that have public visibility
    query = query.filter(models.Post.visibility == "public")
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

    all_posts = query.all()

    # Build response manually with like counts
    response = []
    for post in all_posts:
        response.append({
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "created_at": post.created_at,
            "owner_id": post.owner_id,
            "like_count": len(post.likes), 
            "visibility" : post.visibility
        })

    return response

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
    all_my_posts = db.query(models.Post).filter(models.Post.owner_id == current_user.id).all()

    # Build response manually with like counts
    response = []
    for post in all_my_posts:
        response.append({
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "created_at": post.created_at,
            "owner_id": post.owner_id,
            "like_count": len(post.likes), 
            "visibility" : post.visibility
        })

    return response



# This helps to state the status of a post liked/unliked by an user. 
@router.post("/{post_id}/like")
def toggle_like_post(
    post_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Make sure the post exists
    post = get_post_or_404(post_id, db)

    # Check if the like already exists
    existing_like = db.query(models.PostLike).filter_by(
        user_id=current_user.id,
        post_id=post_id
    ).first()

    if existing_like:
        # User already liked it → unlike (remove)
        db.delete(existing_like)
        db.commit()
        return {"message": "Post unliked."}
    else:
        # User hasn't liked it yet → like it
        new_like = models.PostLike(user_id=current_user.id, post_id=post_id)
        db.add(new_like)
        # Only notify if liker ≠ post owner
        if current_user.id != post.owner_id:
            notification = models.Notification(
            user_id=post.owner_id,
            post_id=post_id,
            type="like"
         )
            db.add(notification)
        db.commit()
        return {"message": "Post liked."}

# function that helps to create comments on a post
@router.post("/{post_id}/comments", response_model=schemas.CommentOut)
def create_comment(
        post_id: int,
        # make sure the comment body has content
        comment: schemas.CommentCreate,
        db: Session = Depends(database.get_db),
        current_user: models.User = Depends(auth.get_current_user)
): 
    # ensures the post exists 
    post = get_post_or_404(post_id, db)
    
    new_comment = models.Comment(
        content=comment.content, 
        post_id=post_id, 
        user_id=current_user.id
    )
    # Track this new object. It’s ready to be inserted into the database.
    db.add(new_comment)

    # Only notify if commenter ≠ post owner
    if current_user.id != post.owner_id:
        notification = models.Notification(
        user_id=post.owner_id,
        post_id=post_id,
        type="comment"
    )
        db.add(notification)

    # actually changes the database by adding the new_comment
    db.commit()
    # Reloads the object from the database to get all up-to-date values , like id and created_at
    db.refresh(new_comment)

    return new_comment

# response_model returns the result as list of comments. 
@router.get("/{post_id}/comments", response_model= list[schemas.CommentOut])
def get_comments_for_post(
        post_id : int , 
        db: Session = Depends(database.get_db)
): 
    get_post_or_404(post_id, db)
    # sorting all the comments in that post in ascending order
    comments = db.query(models.Comment).filter(models.Comment.post_id == post_id).order_by(models.Comment.created_at.asc()).all()
    return comments

# returns notifications for a post to the owner
@router.get("/notifications", response_model=list[schemas.NotificationOut])
def get_notifications(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    notifications = (
        db.query(models.Notification)
        .filter(models.Notification.user_id == current_user.id)
        .order_by(models.Notification.created_at.desc())
        .all()
    )
    return notifications


# gives the status of whether a notification has been seen or not. 
@router.patch("/notifications/{notification_id}", response_model=schemas.NotificationOut)
def mark_notification_as_seen(
    # function of FastAPI, that helps to extract parameters from a path.
    # here , int gives hint to Path for what type of parameter to extract from the path. 
    # so if the path is notifications/5/ , Path will extract 5 and pass it as notification_id's value
    # here description is just of help document the process, to make it easy to read and understand.
    notification_id: int = Path(..., description="ID of the notification to mark as seen"),
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    notification = db.query(models.Notification).filter_by(id=notification_id).first()

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found.")

    if notification.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not have permission to modify this notification.")

    notification.seen = True
    db.commit()
    db.refresh(notification)

    return notification

# function for the bookmark button to show if that post has been bookmarked or not. 
@router.post("/{post_id}/bookmark")
def toggle_bookmark_post (
    post_id : int, 
    db : Session = Depends(database.get_db), 
    current_user : models.User = Depends(auth.get_current_user)
): 
    post = get_post_or_404(post_id, db)

    # Checking if the user has already bookmarked this post
    existing_bookmark = db.query(models.PostBookmark).filter_by(
        user_id = current_user.id, 
        post_id = post_id
    ).first()
    
    # if post already bookmarked , then removing it from the bookmark
    if existing_bookmark: 
        db.delete(existing_bookmark)
        db.commit()
        return {"message": "Post removed from Bookmarks."}
    
    else: 
        new_bookmark = models.PostBookmark(
            user_id = current_user.id, 
            post_id = post_id
        )
        # Here, as new_bookmark is an instance of models.PostBookmark and PostBookmark is related to tablename - "post_bookmarks"
        # SQLAlchemy will know that these changes should be added to that table in the database. 
        db.add(new_bookmark)
        db.commit()

        # Here, we are not using db.refresh(new_bookmark), because here we are not dealing with DB-generated fiels
        # like id, created_at while returning , which may not be automatically updated by SQLAlchemy for which we 
        # have to refresh. Since, here we are returning a message not the new_bookmark object, we don't have to refresh
        return {"message" : "Post bookmarked"}
    
# returnig all the posts bookmarked by the user.      
@router.get("/bookmarks", response_model= list[schemas.PostOut]) 
def get_bookmarked_posts(
    db : Session = Depends(database.get_db),
    current_user : models.User = Depends(auth.get_current_user)
) :
    bookmarks = (
        # temporarily creates a table bet Post and PostBookmark where their post_id are same.
        db.query(models.Post)
        .join(models.PostBookmark, models.Post.id == models.PostBookmark.post_id)
        # then from that temporary table , if filters based on matching of the user_id
        .filter(models.PostBookmark.user_id == current_user.id)
        # this sorts the result from newest to oldest, as its based on the time they were created
        .order_by(models.Post.created_at.desc())
        .all()
    )
    return bookmarks

# helps to know if the post is booked marked or not. 
@router.get("/posts/{post_id}/is_bookedmarked")
def is_post_bookmarked(
    post_id: int, 
    db: Session = Depends(database.get_db), 
    current_user: models.User = Depends(auth.get_current_user)
):
    exists = db.query(models.PostBookmark).filter_by(
        user_id=current_user.id, 
        post_id=post_id
    ).first()

    return {"bookmarked": bool(exists)}