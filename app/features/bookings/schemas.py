from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from app.features.users.models import ServiceType
from app.features.bookings.models import BookingStatus

# Data sent BY the customer to create a booking
class BookingCreate(BaseModel):
    title: str
    service_type: ServiceType
    address: str
    date: datetime  # Pydantic will strictly enforce a valid ISO-8601 UTC string format

# Data sent BY the customer to complete a booking
class BookingComplete(BaseModel):
    remarks: str

# Data sent TO the browser
class BookingResponse(BaseModel):
    id: int
    customer_id: int
    provider_id: Optional[int] = None
    title: str
    remarks: Optional[str] = None
    service_type: ServiceType
    address: str
    date: datetime
    status: BookingStatus

    # Allows Pydantic to read data straight from the SQLAlchemy database object
    model_config = ConfigDict(from_attributes=True)
