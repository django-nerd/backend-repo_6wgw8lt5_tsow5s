"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List

# Soccer Training App Schemas

class Video(BaseModel):
    """
    Videos collection schema
    Collection name: "video"
    """
    title: str = Field(..., description="Video title")
    url: str = Field(..., description="Public video URL (mp4, webm, or HLS) or embeddable link")
    duration: Optional[float] = Field(None, ge=0, description="Duration in seconds")
    team: Optional[str] = Field(None, description="Team or group name")
    player: Optional[str] = Field(None, description="Player name if specific")
    tags: List[str] = Field(default_factory=list, description="Tags for filtering")

class Analysis(BaseModel):
    """
    Video analysis markers
    Collection name: "analysis"
    """
    video_id: str = Field(..., description="Related video id (stringified ObjectId)")
    time: float = Field(..., ge=0, description="Timestamp in seconds")
    note: Optional[str] = Field(None, description="Coach note")
    tag: Optional[str] = Field(None, description="Category tag, e.g., 'pressing', 'finishing'")
    created_by: Optional[str] = Field(None, description="Author name or id")

class Session(BaseModel):
    """
    Training session plan
    Collection name: "session"
    """
    title: str = Field(..., description="Session title")
    date: Optional[str] = Field(None, description="ISO date (YYYY-MM-DD)")
    drills: List[str] = Field(default_factory=list, description="List of drill names")
    notes: Optional[str] = Field(None, description="General session notes")
    video_ids: List[str] = Field(default_factory=list, description="Related video ids")

# Example schemas (kept for reference but not used directly by the app)
class User(BaseModel):
    name: str
    email: str
    address: str
    age: Optional[int] = None
    is_active: bool = True

class Product(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    category: str
    in_stock: bool = True

# The Flames database viewer can use GET /schema to read these models.
