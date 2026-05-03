from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.features.users.models import User
from app.core.deps import get_current_user
from app.features.bookings.schemas import BookingCreate, BookingResponse, BookingComplete
from app.features.bookings import service

# All routes in this file will automatically start with /bookings
router = APIRouter(prefix="/bookings", tags=["Bookings"])

# Note: Every single route below uses `current_user: User = Depends(get_current_user)`.
# This physically forces FastAPI to read the JWT token before allowing the route to execute!

@router.post("", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(
    data: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Customer creates a booking."""
    return service.create_booking(db=db, user=current_user, data=data)

@router.get("/available", response_model=List[BookingResponse])
def get_available_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Provider views available bookings matching their skills."""
    return service.get_available_bookings(db=db, user=current_user)

@router.get("/my-bookings", response_model=List[BookingResponse])
def get_my_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Returns the user's personal workload/history."""
    return service.get_my_bookings(db=db, user=current_user)

@router.patch("/{booking_id}/accept", response_model=BookingResponse)
def accept_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Provider claims a pending booking."""
    return service.accept_booking(db=db, user=current_user, booking_id=booking_id)

@router.patch("/{booking_id}/complete", response_model=BookingResponse)
def complete_booking(
    booking_id: int,
    data: BookingComplete,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Customer marks their accepted booking as complete."""
    return service.complete_booking(db=db, user=current_user, booking_id=booking_id, data=data)
