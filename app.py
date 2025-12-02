from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)

# Secret key for sessions (change this in real apps)
app.secret_key = "mysecretkey"

# SQLite configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ----------------- DATABASE MODELS -----------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    posts = db.relationship("Post", backref="author", lazy=True)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)


# ----------------- ROUTES -----------------

@app.route("/")
def index():
    posts = Post.query.order_by(Post.date_created.desc()).all()
    return render_template("index.html", posts=posts)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        # check if user exists
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing_user:
            flash("Username or email already exists", "danger")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)

        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            session["username"] = user.username
            flash("Logged in successfully!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password", "danger")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        flash("Please log in to access the dashboard.", "warning")
        return redirect(url_for("login"))

    user_posts = Post.query.filter_by(user_id=session["user_id"]).order_by(
        Post.date_created.desc()
    )
    return render_template("dashboard.html", posts=user_posts)


@app.route("/create", methods=["GET", "POST"])
def create_post():
    if "user_id" not in session:
        flash("Please log in to create a post.", "warning")
        return redirect(url_for("login"))

    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]

        new_post = Post(
            title=title,
            content=content,
            user_id=session["user_id"]
        )
        db.session.add(new_post)
        db.session.commit()

        flash("Post created successfully!", "success")
        return redirect(url_for("dashboard"))

    return render_template("create_post.html")


@app.route("/edit/<int:post_id>", methods=["GET", "POST"])
def edit_post(post_id):
    if "user_id" not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for("login"))

    post = Post.query.get_or_404(post_id)

    if post.user_id != session["user_id"]:
        flash("You are not allowed to edit this post.", "danger")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        post.title = request.form["title"]
        post.content = request.form["content"]
        db.session.commit()

        flash("Post updated successfully!", "success")
        return redirect(url_for("dashboard"))

    return render_template("edit_post.html", post=post)


@app.route("/delete/<int:post_id>", methods=["POST"])
def delete_post(post_id):
    if "user_id" not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for("login"))

    post = Post.query.get_or_404(post_id)

    if post.user_id != session["user_id"]:
        flash("You are not allowed to delete this post.", "danger")
        return redirect(url_for("dashboard"))

    db.session.delete(post)
    db.session.commit()

    flash("Post deleted successfully!", "info")
    return redirect(url_for("dashboard"))


# ----------------- CREATE DB -----------------
if __name__ == "__main__":
    if not os.path.exists("blog.db"):
        with app.app_context():
            db.create_all()
    app.run(debug=True)
