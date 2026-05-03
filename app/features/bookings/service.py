from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.features.bookings.models import Booking, BookingStatus
from app.features.bookings.schemas import BookingCreate, BookingComplete
from app.features.users.models import User, UserRole
def create_booking(db: Session, user: User, data: BookingCreate):
    """Customer creates a new pending booking."""
    if user.role != UserRole.CUSTOMER:
        raise HTTPException(status_code=403, detail="Only customers can create bookings")
        
    new_booking = Booking(
        customer_id=user.id, # Automatically assigned from their JWT token!
        title=data.title,
        service_type=data.service_type,
        address=data.address,
        date=data.date,
        status=BookingStatus.pending
    )
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    return new_booking

def get_available_bookings(db: Session, user: User):
    """Provider views all pending bookings matching their skills."""
    if user.role != UserRole.PROVIDER:
        raise HTTPException(status_code=403, detail="Only providers can view available bookings")
    
    # 1. Fetch all pending jobs in the city
    all_pending = db.query(Booking).filter(Booking.status == BookingStatus.pending).all()
    
    # 2. Filter down to jobs this provider is skilled for
    # (Using Python filtering here avoids complex JSON MySQL queries, and is perfectly fast for this scale)
    available = [b for b in all_pending if b.service_type.value in user.services]
    return available

def get_my_bookings(db: Session, user: User):
    """Returns the user's personal workload/history."""
    if user.role == UserRole.CUSTOMER:
        return db.query(Booking).filter(Booking.customer_id == user.id).all()
    elif user.role == UserRole.PROVIDER:
        return db.query(Booking).filter(Booking.provider_id == user.id).all()

def accept_booking(db: Session, user: User, booking_id: int):
    """Provider claims a pending booking."""
    if user.role != UserRole.PROVIDER:
        raise HTTPException(status_code=403, detail="Only providers can accept bookings")
        
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
        
    if booking.status != BookingStatus.pending:
        raise HTTPException(status_code=400, detail="Booking is no longer available")
        
    if booking.service_type.value not in user.services:
        raise HTTPException(status_code=400, detail="You do not have the required skills for this booking")
        
    # Claim it!
    booking.status = BookingStatus.accepted
    booking.provider_id = user.id
    db.commit()
    db.refresh(booking)
    return booking

def complete_booking(db: Session, user: User, booking_id: int, data: BookingComplete):
    """Customer marks their accepted booking as complete."""
    if user.role != UserRole.CUSTOMER:
        raise HTTPException(status_code=403, detail="Only customers can complete bookings")
        
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
        
    if booking.customer_id != user.id:
        raise HTTPException(status_code=403, detail="You do not own this booking")
        
    if booking.status != BookingStatus.accepted:
        raise HTTPException(status_code=400, detail="Booking must be accepted before it can be completed")
        
    # Finish it!
    booking.status = BookingStatus.completed
    booking.remarks = data.remarks
    db.commit()
    db.refresh(booking)
    return booking
