from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.account import Account as DBAccount
from app.schemas.account import Account, AccountCreate, AccountUpdate

router = APIRouter()

@router.post("/", response_model=Account)
def create_account(account: AccountCreate, db: Session = Depends(get_db)):
    db_account = DBAccount(**account.model_dump())
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

@router.get("/", response_model=List[Account])
def read_accounts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    accounts = db.query(DBAccount).offset(skip).limit(limit).all()
    return accounts

@router.put("/{account_id}", response_model=Account)
def update_account(account_id: int, account: AccountUpdate, db: Session = Depends(get_db)):
    db_account = db.query(DBAccount).filter(DBAccount.id == account_id).first()
    if db_account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    for key, value in account.model_dump(exclude_unset=True).items():
        setattr(db_account, key, value)
    db.commit()
    db.refresh(db_account)
    return db_account

@router.delete("/{account_id}", response_model=Account)
def delete_account(account_id: int, db: Session = Depends(get_db)):
    db_account = db.query(DBAccount).filter(DBAccount.id == account_id).first()
    if db_account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    db.delete(db_account)
    db.commit()
    return db_account
