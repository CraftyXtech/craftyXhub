

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
import os

router = APIRouter(prefix="/auth", tags=["Authentication"])


# class Token(BaseModel):
#     access_token: str
#     token_type: str

# @router.post('/register', status_code=status.HTTP_201_CREATED, response_model=UserResponse)
# def register_user(request:UserCreate, db:Session = Depends(get_db_session)):
#     return index.create(request, db)


# class LoginRequest(BaseModel):
#     email: str
#     password: str


# @router.post('/user-login', response_model=Token)
# async def login_user(request: LoginRequest, db: AsyncSession = Depends(get_db_session)):
#     statement = select(User).where(User.email == request.email)
#     result = await db.exec(statement)
#     user = result.first()

#     if not user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid credentials")

#     if not user.verify_password(request.password):
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid credentials")

#     access_token_expires = timedelta(minutes=int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')))
#     access_token = create_access_token(
#         data={"sub": user.email}, expires_delta=access_token_expires
#     )
#     return Token(access_token=access_token, token_type="bearer")

