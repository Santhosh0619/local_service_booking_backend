from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime
from app.db.base import Base
from app.features.users.models import ServiceType
import enum

# Define the allowed states for a booking
class BookingStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    completed = "completed"

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    
    # customer_id is strictly required (cannot be null)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # provider_id starts as NULL when the booking is 'pending'
    provider_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # We reuse the ServiceType enum from the Users domain (plumber, electrician, etc.)
    service_type = Column(Enum(ServiceType), nullable=False)
    
    title = Column(String(100), nullable=False)
    remarks = Column(String(500), nullable=True)
    
    address = Column(String(255), nullable=False)
    
    # DateTime with timezone=True handles UTC timestamps properly
    date = Column(DateTime(timezone=True), nullable=False)
    
    # Default status is always pending
    status = Column(Enum(BookingStatus), default=BookingStatus.pending, nullable=False)
