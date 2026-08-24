from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date, datetime

class SignUpRequest(BaseModel):
    name : str
    identity : str
    email : EmailStr
    mobile : str
    gender : Optional[str] = None
    birthday: Optional[date] = None
    password : str

class SignUpResponse(BaseModel):
    access_token : str
    token_type : str = "bearer"
    refresh_token : Optional[str] = None

class SignInRequest(BaseModel):
    identity : str
    password : str

class SignInResponse(BaseModel):
    access_token : str
    token_type : str = "bearer"
    refresh_token : Optional[str] = None

class UserResponse(BaseModel):
    id : int
    user_identity : str
    user_type : str
    user_email : str
    user_mobile : Optional[str] = None
    user_full_name : str
    user_gender : Optional[str] = None
    user_birthday : Optional[date] = None
    user_company_id : Optional[int] = None
    user_office_id : Optional[int] = None
    user_desk_id : Optional[int] = None
    user_photo : Optional[str] = None
    user_signature : Optional[str] = None
    user_status : bool
    created_at : Optional[datetime] = None
    updated_at : Optional[datetime] = None

    class Config:
        from_attributes = True
