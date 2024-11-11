# wardrobe_model.py

from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime

class WardrobeItemBase(BaseModel):
    clothing_type: str = Field(..., min_length=1, max_length=100)
    for_weather: Optional[str] = Field(None, max_length=100)
    color: Optional[Any] = None  # Assuming color is stored as JSON (e.g., {"primary": "blue", "secondary": "white"})
    size: Optional[str] = Field(None, max_length=10)
    tags: Optional[List[str]] = None
    image_url: Optional[str] = None
    date_added: Optional[datetime] = None

    class Config:
        orm_mode = True

class WardrobeItemCreate(WardrobeItemBase):
    pass

class WardrobeItemUpdate(BaseModel):
    clothing_type: Optional[str] = Field(None, min_length=1, max_length=100)
    for_weather: Optional[str] = Field(None, max_length=100)
    color: Optional[Any] = None
    size: Optional[str] = Field(None, max_length=10)
    tags: Optional[List[str]] = None
    image_url: Optional[str] = None

    class Config:
        orm_mode = True

class WardrobeItemResponse(WardrobeItemBase):
    item_id: int
    user_id: int
    product_id: Optional[int] = None

    class Config:
        orm_mode = True
