# src/routes.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional

from . import models, schemas
from .database import get_db, engine # Added engine for direct execution if needed

# Create tables if they don't exist (for simplicity in development)
# In a production scenario, you might use Alembic for migrations.
models.Base.metadata.create_all(bind=engine)

router = APIRouter()

# --- Helper function to update matrix timestamp ---
def update_matrix_timestamp(db: Session, matrix_id: str):
    db_matrix = db.query(models.Matrix).filter(models.Matrix.id == matrix_id).first()
    if db_matrix:
        db.commit() # This will trigger onupdate=func.now() for updated_at
        db.refresh(db_matrix)

# --- Matrix Endpoints ---
@router.post("/matrices", response_model=schemas.MatrixResponse, status_code=status.HTTP_201_CREATED)
def create_matrix(db: Session = Depends(get_db)):
    db_matrix = models.Matrix()
    db.add(db_matrix)
    db.commit()
    db.refresh(db_matrix)
    # In a real app, the domain would come from config
    sharable_link = f"https://example.com/matrix/{db_matrix.id}" 
    return schemas.MatrixResponse(
        id=db_matrix.id,
        created_at=db_matrix.created_at,
        updated_at=db_matrix.updated_at,
        sharable_link=sharable_link
    )

@router.get("/matrices/{matrix_id}", response_model=schemas.MatrixDetail)
def get_matrix_details(matrix_id: str, db: Session = Depends(get_db)):
    db_matrix = (
        db.query(models.Matrix)
        .options(joinedload(models.Matrix.tasks).joinedload(models.Task.labels), joinedload(models.Matrix.labels))
        .filter(models.Matrix.id == matrix_id)
        .first()
    )
    if db_matrix is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Matrix not found")
    
    # Manually construct the tasks with their labels to match TaskInDB structure
    tasks_with_labels = []
    for task in db_matrix.tasks:
        task_data = schemas.TaskInDB.from_orm(task)
        tasks_with_labels.append(task_data)

    return schemas.MatrixDetail(
        id=db_matrix.id,
        created_at=db_matrix.created_at,
        updated_at=db_matrix.updated_at,
        labels=[schemas.LabelInDB.from_orm(label) for label in db_matrix.labels],
        tasks=tasks_with_labels
    )

# --- Label Endpoints ---
@router.post("/matrices/{matrix_id}/labels", response_model=schemas.LabelInDB, status_code=status.HTTP_201_CREATED)
def create_label_for_matrix(matrix_id: str, label: schemas.LabelCreate, db: Session = Depends(get_db)):
    db_matrix = db.query(models.Matrix).filter(models.Matrix.id == matrix_id).first()
    if not db_matrix:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Matrix not found")
    
    existing_label = db.query(models.Label).filter(models.Label.matrix_id == matrix_id, models.Label.name == label.name).first()
    if existing_label:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Label with this name already exists for this matrix")

    db_label = models.Label(**label.dict(), matrix_id=matrix_id)
    db.add(db_label)
    db.commit()
    update_matrix_timestamp(db, matrix_id)
    db.refresh(db_label)
    return db_label

@router.get("/matrices/{matrix_id}/labels", response_model=List[schemas.LabelInDB])
def get_labels_for_matrix(matrix_id: str, db: Session = Depends(get_db)):
    db_matrix = db.query(models.Matrix).filter(models.Matrix.id == matrix_id).first()
    if not db_matrix:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Matrix not found")
    return db.query(models.Label).filter(models.Label.matrix_id == matrix_id).all()

@router.put("/matrices/{matrix_id}/labels/{label_id}", response_model=schemas.LabelInDB)
def update_label(matrix_id: str, label_id: int, label_update: schemas.LabelUpdate, db: Session = Depends(get_db)):
    db_label = db.query(models.Label).filter(models.Label.id == label_id, models.Label.matrix_id == matrix_id).first()
    if not db_label:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Label not found")

    if label_update.name is not None:
        existing_label_with_name = db.query(models.Label).filter(
            models.Label.matrix_id == matrix_id, 
            models.Label.name == label_update.name, 
            models.Label.id != label_id
        ).first()
        if existing_label_with_name:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Another label with this name already exists for this matrix")
        db_label.name = label_update.name
    
    if label_update.color is not None:
        db_label.color = label_update.color

    db.commit()
    update_matrix_timestamp(db, matrix_id)
    db.refresh(db_label)
    return db_label

@router.delete("/matrices/{matrix_id}/labels/{label_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_label(matrix_id: str, label_id: int, db: Session = Depends(get_db)):
    db_label = db.query(models.Label).filter(models.Label.id == label_id, models.Label.matrix_id == matrix_id).first()
    if not db_label:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Label not found")
    
    # SQLAlchemy will handle cascade for task_labels association if configured, 
    # but here we explicitly clear associations before deleting the label to be safe
    # or ensure the relationship cascade is set up correctly in models.py
    # For now, assuming cascade on task_labels works or is handled by DB constraints if any.
    # If not, manual removal from task_labels would be needed.

    db.delete(db_label)
    db.commit()
    update_matrix_timestamp(db, matrix_id)
    return

# --- Task Endpoints ---
@router.post("/matrices/{matrix_id}/tasks", response_model=schemas.TaskInDB, status_code=status.HTTP_201_CREATED)
def create_task_for_matrix(matrix_id: str, task: schemas.TaskCreate, db: Session = Depends(get_db)):
    db_matrix = db.query(models.Matrix).filter(models.Matrix.id == matrix_id).first()
    if not db_matrix:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Matrix not found")

    task_data = task.dict(exclude={"label_ids"})
    db_task = models.Task(**task_data, matrix_id=matrix_id)

    if task.label_ids:
        for label_id in task.label_ids:
            label = db.query(models.Label).filter(models.Label.id == label_id, models.Label.matrix_id == matrix_id).first()
            if label:
                db_task.labels.append(label)
            else:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Label with id {label_id} not found in this matrix")

    db.add(db_task)
    db.commit()
    update_matrix_timestamp(db, matrix_id)
    db.refresh(db_task)
    # Eager load labels for the response
    db.expire(db_task) # re-fetch with relationships
    refreshed_task = db.query(models.Task).options(joinedload(models.Task.labels)).filter(models.Task.id == db_task.id).one()
    return refreshed_task

@router.get("/matrices/{matrix_id}/tasks", response_model=List[schemas.TaskInDB])
def get_tasks_for_matrix(matrix_id: str, db: Session = Depends(get_db)):
    db_matrix = db.query(models.Matrix).filter(models.Matrix.id == matrix_id).first()
    if not db_matrix:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Matrix not found")
    
    tasks = db.query(models.Task).options(joinedload(models.Task.labels)).filter(models.Task.matrix_id == matrix_id).all()
    return tasks

@router.put("/matrices/{matrix_id}/tasks/{task_id}", response_model=schemas.TaskInDB)
def update_task(matrix_id: str, task_id: int, task_update: schemas.TaskUpdate, db: Session = Depends(get_db)):
    db_task = db.query(models.Task).options(joinedload(models.Task.labels)).filter(models.Task.id == task_id, models.Task.matrix_id == matrix_id).first()
    if not db_task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    update_data = task_update.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        if key == "label_ids":
            # Handle label updates
            db_task.labels.clear() # Clear existing labels first
            if value:
                for label_id in value:
                    label = db.query(models.Label).filter(models.Label.id == label_id, models.Label.matrix_id == matrix_id).first()
                    if label:
                        db_task.labels.append(label)
                    else:
                        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Label with id {label_id} not found in this matrix")
        else:
            setattr(db_task, key, value)

    db.commit()
    update_matrix_timestamp(db, matrix_id)
    db.refresh(db_task)
    # Eager load labels for the response
    db.expire(db_task) # re-fetch with relationships
    refreshed_task = db.query(models.Task).options(joinedload(models.Task.labels)).filter(models.Task.id == db_task.id).one()
    return refreshed_task

@router.delete("/matrices/{matrix_id}/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(matrix_id: str, task_id: int, db: Session = Depends(get_db)):
    db_task = db.query(models.Task).filter(models.Task.id == task_id, models.Task.matrix_id == matrix_id).first()
    if not db_task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    db.delete(db_task)
    db.commit()
    update_matrix_timestamp(db, matrix_id)
    return

