from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from . import models, schemas, crud, auth
from .database import engine, SessionLocal, Base
from .config import ACCESS_TOKEN_EXPIRE_MINUTES

Base.metadata.create_all(bind=engine)

app = FastAPI(title="HR Management API with Auth")

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username, "role": user.role}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=schemas.UserOut)
async def read_users_me(current_user: models.User = Depends(auth.get_current_active_user)):
    return current_user

# Employee endpoints with admin role required
@app.get("/employees", response_model=list[schemas.EmployeeOut])
def read_employees(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(auth.admin_required)):
    return crud.get_employees(db, skip=skip, limit=limit)

@app.get("/employees/{employee_id}", response_model=schemas.EmployeeOut)
def read_employee(employee_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    db_employee = crud.get_employee(db, employee_id)
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    # If user is employee, restrict to own record
    if current_user.role == "employee" and current_user.username != db_employee.email:
        raise HTTPException(status_code=403, detail="Not authorized to view this employee")
    return db_employee

@app.post("/employees", response_model=schemas.EmployeeOut)
def create_employee(employee: schemas.EmployeeCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.admin_required)):
    return crud.create_employee(db, employee)

@app.put("/employees/{employee_id}", response_model=schemas.EmployeeOut)
def update_employee(employee_id: int, employee: schemas.EmployeeUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.admin_required)):
    db_employee = crud.update_employee(db, employee_id, employee)
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return db_employee

@app.delete("/employees/{employee_id}", response_model=schemas.EmployeeOut)
def delete_employee(employee_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.admin_required)):
    db_employee = crud.delete_employee(db, employee_id)
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return db_employee
