import os
import redis
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.schemas import UserCreate, UserResponse, PostCreate, PostResponse
from app.dependencies import get_db
from app.controllers import signup_user, login_user, add_post, delete_post, get_posts
from app.auth import get_current_user
import json

router = APIRouter()

# Initialize Redis client using environment variables
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=0,
    decode_responses=True
)

@router.post("/signup", response_model=UserResponse)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    """
    Registers a new user and returns their details.
    """
    try:
        new_user = signup_user(db, user)
        return new_user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
def login(user: UserCreate, db: Session = Depends(get_db)):
    """
    Authenticates a user and returns a token.
    """
    try:
        token = login_user(db, user)
        return {"token": token}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.post("/addpost", response_model=PostResponse)
def add_post_route(post: PostCreate, token: str = Header(...), db: Session = Depends(get_db)):
    """
    Creates a new post for the authenticated user.
    Validates the payload size to be under 1MB.
    """
    # Although Pydantic validates the field length, add an extra check for encoded size.
    if len(post.text.encode('utf-8')) > 1 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Payload exceeds 1MB")
    user = get_current_user(token, db)
    new_post = add_post(db, user.id.value, post)
    return new_post

@router.get("/getposts", response_model=list[PostResponse])
async def get_posts_route(token: str = Header(...), db: Session = Depends(get_db)):
    """
    Retrieves all posts for the authenticated user.
    Caches results for 5 minutes.
    """
    user = get_current_user(token, db)
    cache_key = f"posts:{user.id}"
    cached = await redis_client.get(cache_key)
    if cached:
        # Deserialize cached JSON string using json.loads for safety.
        return json.loads(cached.decode('utf-8') if isinstance(cached, bytes) else cached)
    posts = get_posts(db, user.id.value)
    await redis_client.setex(cache_key, 300, str(posts))  # Cache for 5 minutes
    return posts

@router.delete("/deletepost/{post_id}")
def delete_post_route(post_id: int, token: str = Header(...), db: Session = Depends(get_db)):
    """
    Deletes a post specified by post_id for the authenticated user.
    Also invalidates the cached posts.
    """
    user = get_current_user(token, db)
    try:
        delete_post(db, user.id.value, post_id)
        redis_client.delete(f"posts:{user.id}")  # Invalidate cache
        return {"message": "Post deleted"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
