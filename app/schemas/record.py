from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional
from enum import Enum

class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"

class RecordBase(BaseModel):
    amount: float = Field(..., gt=0)
    type: TransactionType
    category: str = Field(..., min_length=1, max_length=50)
    notes: Optional[str] = Field(None, max_length=200)
    date: Optional[datetime] = None

class RecordCreate(RecordBase):
    """Schema for incoming creation request"""
    pass

class RecordUpdate(BaseModel):
    """Schema for record modifications"""
    amount: Optional[float] = Field(None, gt=0)
    type: Optional[TransactionType] = None
    category: Optional[str] = None
    notes: Optional[str] = None
    date: Optional[datetime] = None

class RecordOut(RecordBase):
    """Schema for API responses"""
    id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
