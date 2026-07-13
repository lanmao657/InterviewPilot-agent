from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import decode_token
from app.models import User
from app.services.embedding import EmbeddingService
from app.services.guest_cleanup import delete_guest_user_data, is_guest_expired
from app.services.retrieval import RetrievalService

settings = get_settings()
bearer_scheme = HTTPBearer()


def get_current_user(cred=Depends(bearer_scheme), db: Session = Depends(get_db)) -> User:
    try:
        user_id = int(decode_token(cred.credentials, "access"))
    except (ValueError, TypeError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="登录已失效")
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在")
    if is_guest_expired(user, settings.guest_retention_hours):
        delete_guest_user_data(db, [user.id])
        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="游客会话已过期，请重新登录")
    return user


def get_retrieval_service(db: Session = Depends(get_db)) -> RetrievalService:
    return RetrievalService(EmbeddingService(), db)
