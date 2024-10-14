from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import List

# Database configuration
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/postgres"  
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# SQLAlchemy model for Wardrobe Items
class WardrobeItems(Base):
    __tablename__ = "wardrobe_items"
    item_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    type = Column(String, nullable=False)
    season = Column(String)
    fabric = Column(String)
    color = Column(String)
    size = Column(String)
    tags = Column(String)
    image_url = Column(String)

# SQLAlchemy model for Users (minimal version)
class Users(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

# Pydantic model for input validation
class ClothingItem(BaseModel):
    user_id: int
    type: str
    season: str
    fabric: str
    color: str
    size: str
    tags: str
    image_url: str

    class Config:
        orm_mode = True

# FastAPI app instance
app = FastAPI()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
class UserCreate(BaseModel):
    username: str
    email: str
    
# API endpoint to create a new user
@app.post("/users/", response_model=UserCreate)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    new_user = Users(username=user.username, email=user.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# API endpoint to get all clothing items
@app.get("/clothing_items/", response_model=List[ClothingItem])
def get_clothing_items(db: Session = Depends(get_db)):
    items = db.query(WardrobeItems).all()
    return items

# API endpoint to get a specific clothing item by ID
@app.get("/clothing_items/{item_id}", response_model=ClothingItem)
def get_clothing_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(WardrobeItems).filter(WardrobeItems.item_id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

# API endpoint to create a new clothing item
@app.post("/clothing_items/", response_model=ClothingItem)
def create_clothing_item(item: ClothingItem, db: Session = Depends(get_db)):
    new_item = WardrobeItems(**item.dict())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

# API endpoint to update an existing clothing item
@app.put("/clothing_items/{item_id}", response_model=ClothingItem)
def update_clothing_item(item_id: int, updated_item: ClothingItem, db: Session = Depends(get_db)):
    item = db.query(WardrobeItems).filter(WardrobeItems.item_id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Update the fields
    for key, value in updated_item.dict().items():
        setattr(item, key, value)

    db.commit()
    db.refresh(item)
    return item

# API endpoint to delete a clothing item by ID
@app.delete("/clothing_items/{item_id}")
def delete_clothing_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(WardrobeItems).filter(WardrobeItems.item_id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.delete(item)
    db.commit()
    return {"message": "Item deleted successfully"}
