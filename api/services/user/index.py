from sqlalchemy.orm import Session
from schemas.auth import  UserCreate
from fastapi import HTTPException, status
from passlib.context import CryptContext
from models.user import  User

password_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Hash():
    def bcrypt(password:str)->str:
        return password_ctx.hash(password)

    def verify(password, hashed_password) -> bool:
        return password_ctx.verify(password, hashed_password)

def create(request:UserCreate, db:Session):
    hashed_password = Hash.bcrypt(password=request.password)
    new_user = User(name=request.name, email=request.email, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def fetch_user(user_id, db):
    user = db.query(User).filter(User.id==user_id ).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return user