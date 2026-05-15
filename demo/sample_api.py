"""Sample FastAPI application for demonstrating APIFlow pipeline.

This file contains a simple REST API with multiple endpoints covering
CRUD operations, authentication, pagination, and file uploads.

Usage:
    pip install fastapi uvicorn
    uvicorn demo.sample_api:app --reload
"""

from typing import Optional, List
from pydantic import BaseModel, EmailStr
from fastapi import FastAPI, HTTPException, Depends, Query, UploadFile, File, Header

app = FastAPI(title="Demo User API", version="1.0.0", description="Sample API for APIFlow demo")

# --- Data Models ---

class UserCreate(BaseModel):
    name: str
    email: str
    age: Optional[int] = None
    role: str = "user"


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    age: Optional[int] = None
    role: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    age: Optional[int]
    role: str


class PaginatedResponse(BaseModel):
    items: List[UserResponse]
    total: int
    page: int
    page_size: int


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None


# --- Fake Database ---

fake_db = {
    1: {"id": 1, "name": "Alice", "email": "alice@example.com", "age": 30, "role": "admin"},
    2: {"id": 2, "name": "Bob", "email": "bob@example.com", "age": 25, "role": "user"},
    3: {"id": 3, "name": "Charlie", "email": "charlie@example.com", "age": 35, "role": "user"},
}
next_id = 4


def get_current_user(authorization: str = Header(None)):
    """Simple auth dependency -- just checks header exists."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    return {"token": authorization}


# --- Endpoints ---

@app.get("/api/users", response_model=PaginatedResponse, tags=["users"])
def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    role: Optional[str] = Query(None, description="Filter by role"),
):
    """List all users with pagination and optional role filter."""
    users = list(fake_db.values())
    if role:
        users = [u for u in users if u["role"] == role]
    total = len(users)
    start = (page - 1) * page_size
    items = users[start : start + page_size]
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size)


@app.get("/api/users/{user_id}", response_model=UserResponse, tags=["users"])
def get_user(user_id: int):
    """Get a single user by ID."""
    if user_id not in fake_db:
        raise HTTPException(status_code=404, detail="User not found")
    return fake_db[user_id]


@app.post("/api/users", response_model=UserResponse, status_code=201, tags=["users"])
def create_user(user: UserCreate, current_user=Depends(get_current_user)):
    """Create a new user. Requires authentication."""
    global next_id
    new_user = {"id": next_id, **user.dict()}
    fake_db[next_id] = new_user
    next_id += 1
    return new_user


@app.put("/api/users/{user_id}", response_model=UserResponse, tags=["users"])
def update_user(user_id: int, updates: UserUpdate, current_user=Depends(get_current_user)):
    """Update an existing user. Requires authentication."""
    if user_id not in fake_db:
        raise HTTPException(status_code=404, detail="User not found")
    user = fake_db[user_id]
    update_data = updates.dict(exclude_unset=True)
    user.update(update_data)
    return user


@app.delete("/api/users/{user_id}", status_code=204, tags=["users"])
def delete_user(user_id: int, current_user=Depends(get_current_user)):
    """Delete a user. Requires authentication."""
    if user_id not in fake_db:
        raise HTTPException(status_code=404, detail="User not found")
    del fake_db[user_id]
    return None


@app.post("/api/users/{user_id}/avatar", tags=["users"])
async def upload_avatar(user_id: int, file: UploadFile = File(...), current_user=Depends(get_current_user)):
    """Upload avatar image for a user. Requires authentication."""
    if user_id not in fake_db:
        raise HTTPException(status_code=404, detail="User not found")
    content = await file.read()
    return {
        "message": "Avatar uploaded successfully",
        "filename": file.filename,
        "size": len(content),
    }


@app.get("/api/health", tags=["system"])
def health_check():
    """Health check endpoint (no auth required)."""
    return {"status": "ok", "version": "1.0.0"}
