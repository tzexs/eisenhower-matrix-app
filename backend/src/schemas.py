# src/schemas.py
from pydantic import BaseModel
from typing import List, Optional
import datetime

# Label Schemas
class LabelBase(BaseModel):
    name: str
    color: Optional[str] = None

class LabelCreate(LabelBase):
    pass

class LabelUpdate(LabelBase):
    name: Optional[str] = None # Allow partial updates
    color: Optional[str] = None

class LabelInDB(LabelBase):
    id: int
    matrix_id: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True

# Task Schemas
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    quadrant: str # e.g., "urgent_important"

class TaskCreate(TaskBase):
    label_ids: Optional[List[int]] = []

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    quadrant: Optional[str] = None
    label_ids: Optional[List[int]] = None # Allow updating labels

class TaskInDB(TaskBase):
    id: int
    matrix_id: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    labels: List[LabelInDB] = [] # To show associated labels

    class Config:
        from_attributes = True

# Matrix Schemas
class MatrixBase(BaseModel):
    pass

class MatrixCreate(MatrixBase):
    pass

class MatrixInDBBase(MatrixBase):
    id: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True

class MatrixResponse(MatrixInDBBase):
    sharable_link: str

class MatrixDetail(MatrixInDBBase):
    labels: List[LabelInDB] = []
    tasks: List[TaskInDB] = []

