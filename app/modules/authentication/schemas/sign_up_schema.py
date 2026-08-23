from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date

class SignUpRequest(BaseModel):
    name : str
    identity : str
    email : EmailStr
    mobile : str
    birthday: Optional[date] = None
    password : str

class SignUpResponse(BaseModel):
    access_token : str
    token_type : str = "bearer"
    refresh_token : Optional[str] = None