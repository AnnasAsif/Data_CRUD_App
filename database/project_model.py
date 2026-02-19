from pydantic import BaseModel, Field, field_serializer
from typing import Optional
from datetime import datetime

# Project Models
class Project(BaseModel):
    name: str = Field(..., description="Project name")
    image_url: Optional[str] = Field(default=None, description="Project image URL")
    thumbnail_url: Optional[str] = Field(default=None, description="Project thumbnail URL")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True