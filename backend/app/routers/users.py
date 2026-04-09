from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from app.database import get_db
from app.models.user import User

router = APIRouter(prefix="/users", tags=["users"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserRegisterRequest(BaseModel):
    username: str
    email: str
    password: str


class UserLoginRequest(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True


@router.post("/register", response_model=UserResponse)
async def register_user(
    req: UserRegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Register a new user."""
    # Check if username already exists
    existing_username = await db.execute(
        select(User).where(User.username == req.username)
    )
    if existing_username.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username already exists")

    # Check if email already exists
    existing_email = await db.execute(
        select(User).where(User.email == req.email)
    )
    if existing_email.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already exists")

    # Hash password and create user
    hashed_password = pwd_context.hash(req.password)
    new_user = User(
        username=req.username,
        email=req.email,
        password_hash=hashed_password,
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return UserResponse(
        id=new_user.id,
        username=new_user.username,
        email=new_user.email,
    )


@router.post("/login", response_model=UserResponse)
async def login_user(
    req: UserLoginRequest,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Login an existing user."""
    # Find user by username
    result = await db.execute(
        select(User).where(User.username == req.username)
    )
    user = result.scalar_one_or_none()

    if not user or not pwd_context.verify(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
    )

