from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, ForeignKey



# CREATE DATABASE
class Base(DeclarativeBase):
    pass
db = SQLAlchemy(model_class=Base)

# CONFIGURE TABLES
# TODO: Create a User table for all your registered users. 
class User(UserMixin,db.Model):
    __tablename__ = "User"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    post : Mapped[list["BlogPost"]] = relationship('BlogPost',back_populates="author")
    comment : Mapped[list["Comment"]] = relationship('Comment',back_populates="author")

class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped["User"] = relationship("User", back_populates="post")
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("User.id"))
    
    comments : Mapped[list["Comment"]] = relationship('Comment',back_populates="parent_post")
    
class Comment(db.Model):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("blog_posts.id"), nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("User.id"), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationships
    author: Mapped["User"] = relationship("User", back_populates="comment")
    parent_post: Mapped["BlogPost"] = relationship("BlogPost", back_populates="comments")
