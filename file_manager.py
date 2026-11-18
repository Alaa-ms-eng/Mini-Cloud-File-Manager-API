from fastapi import FastAPI, Body, Depends, HTTPException
from pydantic import BaseModel, Field, EmailStr, HttpUrl
from sqlalchemy.orm import Session
from database import User, get_db  

app = FastAPI()

database = []

class Owner(BaseModel):
    name: str
    email: EmailStr

class FileModel(BaseModel):
    id: int
    fileName: str
    size: int = Field(..., gt=0)
    url: HttpUrl
    owner: Owner


@app.post("/register")
async def register_user(owner: Owner, db: Session = Depends(get_db)):

    db_user = db.query(User).filter(User.email == owner.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email is already registered!")
    

    new_user = User(name=owner.name, email=owner.email)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "user added successfully", "user": {"id": new_user.id, "name": new_user.name, "email": new_user.email}}


@app.post("/files")
async def creat_file(file:FileModel,db: Session = Depends(get_db)):
    db_file = FileModel(
        id=file.id,
        fileName=file.fileName,
        size=file.size,
        url=file.url,
        owner=file.owner
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return{"message":"File added successfully","file":db_file}

@app.get('/files/{file_id}')
async def get_file(file_id:int,db: Session = Depends(get_db)):
    db_file = db.query(FileModel).filter(FileModel.id == file_id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
    return db_file

@app.get("/files")
async def search_files(owner_name: str=None,db: Session = Depends(get_db)):
    if owner_name:
        filtered_files = db.query(FileModel).filter(FileModel.owner.name == owner_name).all()
        return filtered_files
    
    return db.query(FileModel).all()
