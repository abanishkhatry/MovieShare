from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime


"""
This defines a new model class called User
It inherits from Base, which is the SQLAlchemy declarative base (you’ve already defined this in database.py).
This means SQLAlchemy will treat User as a table in your PostgreSQL database.
"""
class User(Base):
    # setting actual name for the table in the database
    __tablename__ = "users"
    # Columns for the tables
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=datetime.utcnow)
    # links the user to all the posts made by him, by going to Post class. 
    posts = relationship("Post", back_populates="owner")


"""
This defines a new model class called Post
It inherits from Base, which is the SQLAlchemy declarative base (you’ve already defined this in database.py).
This means SQLAlchemy will treat Post as a table in your PostgreSQL database.
"""
class Post(Base): 
    # setting actual name for the table in the database
    __tablename__ = "posts"
    # Columns for the tables
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    visibility = Column(String, nullable=False, default="public")
    #  Links this post to the user who created it
    owner_id = Column(Integer, ForeignKey("users.id"))
    """
    relationship("User") : Connects this Post to its associated "User" object. 
    back_populates = "posts": This refers back to the User model and get the posts
    So, post.owner will help us get the owner of the post, and user.posts will help us to get all posts made by the user
    """
    owner = relationship("User", back_populates="posts")

# New table in the PostgreSQL database, that connects the user and the post, if its liked by the user
class PostLike(Base):
    _tablename_ = "post_likes"
    # both user and post _id create many-to-one relation with User and Post model repectively. 
    user_id = Column(Integer, ForeignKey("users.id"))
    post_id = Column(Integer, ForeignKey("posts.id"))
    # prevents duplicates,a user can only like a specific post once
    __table_args__ = (
        PrimaryKeyConstraint("user_id", "post_id"),
    )
    # This also adds a new property to the User Model, i.e. user.liked_posts which gives all 
    # the likes that user had made. 
    user = relationship("User", backref="liked_posts")

    # This also adds a new property to the Post Model, i.e. post.likes whihc is a list of all 
    # PostLike objects pointing to this post.
    post = relationship("Post", backref="likes")



class Comment(Base): 
    # name of the table in database
    _tablename_ = "comments"
    # comment's features
    id = Column (Integer, primary_key=True, index = True)
    content = Column (Text, nullable = False)
    created_at = Column (DateTime, default= datetime.utcnow)
    # connecting the comment to the post, and the user
    user_id = Column (Integer, ForeignKey("users.id"), nullable = False)
    post_id = Column (Integer, ForeignKey("posts.id"), nullable=False)
    
    """
    - sets up relation between the Comment model and the User, Post modal 
    - backref = "comments", gives access to : 
    1. comment.user : this gives the User object who wrote this comment
    2. user.comments : gives a list of all Comment object associated with this user. 
    So, backref creates the reverse property automatically.
    """
    user = relationship ("User" , backref= "comments")
    post = relationship ("Post", backref= "comments")



class Notification(Base): 
    _tablename_ = "notifications"

    id = Column(Integer, primary_key= True, index = True)
    # user id of the post owner who will receive the notification
    user_id = Column(Integer, ForeignKey  = "users.id", nullable= False)
    post_id = Column(Integer, ForeignKey  = "posts.id", nullable= False)
    # maybe like or comment
    type = Column(Integer, nullable= False)
    # whether the user has read the notification
    seen = Column(Boolean, default= False)
    created_at = Column(DateTime, default = datetime.utcnow)

    user = relationship("User", backref="notifications")
    post = relationship("Post", backref="notifications")
