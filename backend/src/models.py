# src/models.py

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

# Association table for many-to-many relationship between tasks and labels
task_labels_association = Table(
    "task_labels",
    Base.metadata,
    Column("task_id", Integer, ForeignKey("tasks.id"), primary_key=True),
    Column("label_id", Integer, ForeignKey("labels.id"), primary_key=True),
)

class Matrix(Base):
    __tablename__ = "matrices"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    labels = relationship("Label", back_populates="matrix", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="matrix", cascade="all, delete-orphan")

class Label(Base):
    __tablename__ = "labels"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    matrix_id = Column(String, ForeignKey("matrices.id"), nullable=False)
    name = Column(String, nullable=False)
    color = Column(String, nullable=True) # e.g., "#FF5733"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    matrix = relationship("Matrix", back_populates="labels")
    tasks = relationship(
        "Task", secondary=task_labels_association, back_populates="labels"
    )

    __table_args__ = (UniqueConstraint("matrix_id", "name", name="_matrix_label_name_uc"),)

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    matrix_id = Column(String, ForeignKey("matrices.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    quadrant = Column(String, nullable=False) # e.g., "urgent_important"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    matrix = relationship("Matrix", back_populates="tasks")
    labels = relationship(
        "Label", secondary=task_labels_association, back_populates="tasks"
    )

