from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db, FamilyMember, User
from backend.core.schemas import FamilyMemberIn, FamilyMemberOut
from backend.core.security import get_current_user

router = APIRouter(prefix="/pedigree", tags=["Pedigree"])


@router.post("/", response_model=FamilyMemberOut, status_code=201)
def add_member(payload: FamilyMemberIn, db: Session = Depends(get_db),
               current_user: User = Depends(get_current_user)):
    member = FamilyMember(**payload.model_dump(), user_id=current_user.id)
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


@router.get("/", response_model=List[FamilyMemberOut])
def list_members(db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_user)):
    return db.query(FamilyMember).filter(FamilyMember.user_id == current_user.id).all()


@router.put("/{member_id}", response_model=FamilyMemberOut)
def update_member(member_id: int, payload: FamilyMemberIn,
                  db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user)):
    member = db.query(FamilyMember).filter(
        FamilyMember.id == member_id, FamilyMember.user_id == current_user.id
    ).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    for k, v in payload.model_dump().items():
        setattr(member, k, v)
    db.commit()
    db.refresh(member)
    return member


@router.delete("/{member_id}", status_code=204)
def delete_member(member_id: int, db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user)):
    member = db.query(FamilyMember).filter(
        FamilyMember.id == member_id, FamilyMember.user_id == current_user.id
    ).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    db.delete(member)
    db.commit()
