"""Cameras API router."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.deps import get_db
from backend.schemas import CameraCreateRequest, CameraResponse, PaginatedResponse
from database.models import Camera, CameraStatus

router = APIRouter()


@router.post("", response_model=CameraResponse, status_code=201)
def create_camera(request: CameraCreateRequest, db: Session = Depends(get_db)):
    camera = Camera(
        camera_name=request.camera_name,
        location_name=request.location_name,
        latitude=request.latitude,
        longitude=request.longitude,
        status=CameraStatus.ACTIVE,
        installation_date=datetime.utcnow(),
    )
    db.add(camera)
    db.commit()
    db.refresh(camera)
    return camera


@router.get("", response_model=PaginatedResponse)
def list_cameras(
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(Camera)
    
    if status:
        query = query.filter(Camera.status == CameraStatus(status))
    
    total = query.count()
    cameras = query.offset((page - 1) * per_page).limit(per_page).all()
    
    return PaginatedResponse(
        items=[CameraResponse.model_validate(c) for c in cameras],
        total=total,
        page=page,
        per_page=per_page,
        pages=(total + per_page - 1) // per_page,
    )


@router.get("/{camera_id}", response_model=CameraResponse)
def get_camera(camera_id: int, db: Session = Depends(get_db)):
    camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    return camera


@router.patch("/{camera_id}/status")
def update_camera_status(
    camera_id: int,
    status: str,
    db: Session = Depends(get_db),
):
    camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    camera.status = CameraStatus(status)
    camera.last_active_at = datetime.utcnow() if status == "active" else camera.last_active_at
    db.commit()
    return {"status": "updated", "camera_id": camera_id, "new_status": status}


@router.delete("/{camera_id}")
def delete_camera(camera_id: int, db: Session = Depends(get_db)):
    camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    db.delete(camera)
    db.commit()
    return {"status": "deleted", "camera_id": camera_id}
