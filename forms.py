from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, URL, Email
from flask_ckeditor import CKEditorField
from datetime import datetime
from model import db,BlogPost, User
from werkzeug.security import generate_password_hash,check_password_hash
from flask import flash

# WTForm for creating a blog post
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")
    
    def post_db(self,current_user):
        post = BlogPost(
            title=self.title.data,
            subtitle=self.subtitle.data,
            body=self.body.data,
            img_url=self.img_url.data,
            date=datetime.now().strftime("%B %d, %Y"),
            author=current_user
        )
        return post

# TODO: Create a RegisterForm to register new users
class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(),Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    submit = SubmitField("Submit")
    
    def register_db(self):
        user = User(
            email=self.email.data,
            password=generate_password_hash(self.password.data,method='pbkdf2:sha1', salt_length=8),
            name=self.name.data
            )
        return user        
        
# TODO: Create a LoginForm to login existing users
class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(),Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")
    
    def validate_user(self):
        user = db.session.execute(db.select(User).where(User.email==self.email.data)).scalar()
        if user:
            if check_password_hash(user.password,self.password.data):
                return user
            else:
                flash("Incorrect Password")
        else:
            flash("Email is not found")
    
    
# TODO: Create a CommentForm so users can leave comments below posts
class CommentForm(FlaskForm):
    comment = CKEditorField("Comment",validators=[DataRequired()])
    submit = SubmitField("Submit Comment")