from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import create_token, decode_token, hash_password, verify_password
from app.deps import get_current_user
from app.models import User
from app.schemas import RefreshRequest, TokenPair, UserCreate, UserLogin, UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


def _token_pair(user: User) -> TokenPair:
    settings = get_settings()
    access = create_token(str(user.id), "access", timedelta(minutes=settings.access_token_minutes))
    refresh = create_token(str(user.id), "refresh", timedelta(days=settings.refresh_token_days))
    return TokenPair(access_token=access, refresh_token=refresh, user=UserRead.model_validate(user))


@router.post("/register", response_model=TokenPair)
def register(payload: UserCreate, db: Session = Depends(get_db)) -> TokenPair:
    existing = db.scalar(select(User).where(User.username == payload.username))
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="用户名已注册")
    email = payload.email.lower() if payload.email else None
    if email and db.scalar(select(User).where(User.email == email)):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="邮箱已注册")
    user = User(username=payload.username, email=email, name=payload.username, hashed_password=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return _token_pair(user)


@router.post("/login", response_model=TokenPair)
def login(payload: UserLogin, db: Session = Depends(get_db)) -> TokenPair:
    user_filter = User.email == payload.username if "@" in payload.username else User.username == payload.username
    user = db.scalar(select(User).where(user_filter))
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
    return _token_pair(user)


@router.post("/refresh", response_model=TokenPair)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)) -> TokenPair:
    try:
        user_id = int(decode_token(payload.refresh_token, "refresh"))
    except (ValueError, TypeError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="刷新令牌无效")
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在")
    return _token_pair(user)


@router.get("/me", response_model=UserRead)
def me(user: User = Depends(get_current_user)) -> User:
    return user
