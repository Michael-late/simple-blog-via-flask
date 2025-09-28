from datetime import date
from flask import Flask, abort, render_template, redirect, url_for, flash
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
# from flask_gravatar import Gravatar
from model import db,BlogPost,User, Comment
from functools import wraps
# Import your forms from the forms.py
from forms import CreatePostForm, RegisterForm, LoginForm, CommentForm
from hashlib import md5
# import random
import os 
from dotenv import load_dotenv
load_dotenv()

def gravatar_url(email, size=100, rating='g', force_default=False):
    available_defaults = ["retro", "monsterid", "wavatar", "identicon", "robohash"]
    hash_value = md5(email.lower().encode('utf-8')).hexdigest()
    default = available_defaults[int(hash_value, 16) % len(available_defaults)]
    return f"https://www.gravatar.com/avatar/{hash_value}?s={size}&d={default}&r={rating}&f={force_default}"

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("secret_key")
ckeditor = CKEditor(app)
Bootstrap5(app)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DB_URI")
app.jinja_env.filters['gravatar'] = gravatar_url
db.init_app(app)
with app.app_context():
    db.create_all()
    
# TODO: Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User,user_id)

def admin_only(func):
    @wraps(func)
    def wrapper(*args,**kwargs):
        if current_user.id != 1:
            return abort(403)
        return func(*args,**kwargs)
    return wrapper
        

# TODO: Use Werkzeug to hash the user's password when creating a new user.
@app.route('/register',methods=["GET","POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        new_user = form.register_db()
        db.session.add(new_user)
        db.session.commit()
        flash("Login Please")
        return redirect(url_for('login'))
    return render_template("register.html",form=form)


# TODO: Retrieve a user from the database based on their email. 
@app.route('/login',methods=["GET","POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = form.validate_user()
        if user:
            login_user(user)
            return redirect(url_for("get_all_posts"))
    return render_template("login.html",form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route('/')
def get_all_posts():
    result = db.session.execute(db.select(BlogPost))
    posts = result.scalars().all()
    return render_template("index.html", all_posts=posts)

# TODO: Allow logged-in users to comment on posts
@app.route("/post/<int:post_id>", methods=["GET","POST"])
def show_post(post_id):
    comment_form = CommentForm()
    if comment_form.validate_on_submit():
        if current_user.is_authenticated :
            commenting = Comment(
                text = comment_form.comment.data,
                author = current_user,
                parent_post = db.session.execute(db.select(BlogPost).where(BlogPost.id==post_id)).scalar()
            )
            db.session.add(commenting)
            db.session.commit()
        else:
            flash("Login Before Commenting")
            return redirect(url_for('login'))
    requested_post = db.get_or_404(BlogPost, post_id)
    all_comment = db.session.execute(db.select(Comment).where(Comment.post_id==post_id)).scalars().all()
    return render_template("post.html", post=requested_post, comment_form=comment_form, comments=all_comment,gravatar_url=gravatar_url)


# TODO: Use a decorator so only an admin user can create a new post
@app.route("/new-post", methods=["GET", "POST"])
@admin_only
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = form.post_db(current_user=current_user  )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)


# TODO: Use a decorator so only an admin user can edit a post
@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_only
def edit_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = current_user
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))
    return render_template("make-post.html", form=edit_form, is_edit=True)


# TODO: Use a decorator so only an admin user can delete a post
@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    post_to_delete = db.get_or_404(BlogPost, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True, port=5002)
