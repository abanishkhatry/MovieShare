from sqlalchemy import Column, String, Integer, DateTime, Text,  ForeignKey
from sqlalchemy.sql import func
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
    created_at = Column(DateTime(timezone=True), server_default=func.now())
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
    #  Links this post to the user who created it
    owner_id = Column(Integer, ForeignKey("users.id"))
    """
    relationship("User") : Connects this Post to its associated "User" object. 
    back_populates = "posts": This refers back to the User model and get the posts
    So, post.owner will help us get the owner of the post, and user.posts will help us to get all posts made by the user
    """
    owner = relationship("User", back_populates="posts")