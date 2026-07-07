from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from backend.database import get_db, User
from backend.core.schemas import UserOut
from backend.core.security import get_current_user, hash_password

router = APIRouter(prefix="/profile", tags=["Profile"])


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    password: Optional[str] = None


@router.get("/", response_model=UserOut)
def get_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/", response_model=UserOut)
def update_profile(payload: ProfileUpdate,
                   db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    if payload.full_name:
        current_user.full_name = payload.full_name
    if payload.password:
        if len(payload.password) < 6:
            raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
        current_user.hashed_password = hash_password(payload.password)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.delete("/", status_code=204)
def delete_account(db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    db.delete(current_user)
    db.commit()
