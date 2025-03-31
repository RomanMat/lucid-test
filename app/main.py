from fastapi import FastAPI
from app.routes import router as api_router

# Initialize FastAPI application
app = FastAPI(title="FastAPI MVC App")

# Include API routes from the routes module
app.include_router(api_router)
