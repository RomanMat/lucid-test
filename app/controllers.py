from sqlalchemy.orm import Session
from app.models import User, Post
from app.schemas import UserCreate, PostCreate
from app.auth import hash_password, verify_password, create_token

def signup_user(db: Session, user_data: UserCreate) -> User:
    """
    Registers a new user.
    Raises an exception if the email is already registered.
    """
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise Exception("Email already registered")
    new_user = User(email=user_data.email, password=hash_password(user_data.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def login_user(db: Session, user_data: UserCreate) -> str:
    """
    Authenticates the user.
    Returns a token if credentials are valid, otherwise raises an exception.
    """
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user or not verify_password(user_data.password, user.password.value):
        raise Exception("Invalid credentials")
    return create_token(user.id.value)

def add_post(db: Session, user_id: int, post_data: PostCreate) -> Post:
    """
    Creates a new post associated with the given user.
    """
    new_post = Post(text=post_data.text, owner_id=user_id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

def delete_post(db: Session, user_id: int, post_id: int) -> None:
    """
    Deletes a post with the given post_id if it belongs to the user.
    Raises an exception if the post is not found.
    """
    post = db.query(Post).filter(Post.id == post_id, Post.owner_id == user_id).first()
    if not post:
        raise Exception("Post not found")
    db.delete(post)
    db.commit()

def get_posts(db: Session, user_id: int) -> list[Post]:
    """
    Retrieves all posts for the given user.
    """
    posts = db.query(Post).filter(Post.owner_id == user_id).all()
    return posts
