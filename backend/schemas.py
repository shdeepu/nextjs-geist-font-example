from datetime import date
from pydantic import BaseModel, EmailStr
from typing import Optional

# User schemas
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str
    role: str  # "admin" or "employee"

class UserOut(UserBase):
    id: int
    role: str

    class Config:
        orm_mode = True

# Employee schemas
class EmployeeBase(BaseModel):
    name: str
    email: EmailStr
    position: Optional[str] = None
    date_joined: Optional[date] = None
    department_id: Optional[int] = None

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeUpdate(EmployeeBase):
    pass

class EmployeeOut(EmployeeBase):
    id: int

    class Config:
        orm_mode = True

# Department schemas
class DepartmentBase(BaseModel):
    name: str

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentOut(DepartmentBase):
    id: int

    class Config:
        orm_mode = True

# Token schemas for authentication
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None
