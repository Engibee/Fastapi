from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel

# SQLAlchemy setup
SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://root:vyre@localhost:3306/pythonsql"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class UserCreate(BaseModel):
    user: str
    password: str
    email: str
    verification_code: str
    email_checked: bool

class User(UserCreate):
    class Config:
        orm_mode = True

class UserDB(Base):
    __tablename__ = 'users'
    user = Column(String(255), primary_key=True, nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    email = Column(String(255), unique=True)
    verification_code = Column(String(255))
    email_checked = Column(Boolean, default=False)

Base.metadata.create_all(bind=engine)

app = FastAPI(debug=True)

@app.post("/users/", response_model=User)
def create_user(user: UserCreate):
    db = SessionLocal()
    db_user = UserDB(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.get("/users/{user}", response_model=User)
def get_user(user: str):
    db = SessionLocal()
    db_user = db.query(UserDB).filter(UserDB.user == user).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.put("/update/{username}/{entry_type}/{new_entry}", response_model=User)
def update_user(username: str,entry_type: str,new_entry: str, user: UserCreate):
    db = SessionLocal()
    db_user = db.query(UserDB).filter(UserDB.user == username).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if hasattr(db_user, entry_type):
        setattr(db_user, entry_type, new_entry)
    else:
        raise HTTPException(status_code=404, detail="Entry type not valid")

    db.commit()
    db.refresh(db_user)
    return db_user


@app.delete("/users/{email}")
def delete_user(email: str):
    db = SessionLocal()
    db_user = db.query(UserDB).filter(UserDB.email == email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return {"message": "User deleted successfully"}

#uvicorn main:app --reload