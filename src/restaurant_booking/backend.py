import datetime as dt
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session
import uvicorn

# Database imports
from .database import Booking, get_db, init_db

# Initialize database
init_db()


# Pydantic Schemas
class BookingRequest(BaseModel):
    customer_name: str
    special_request: str
    start_time: dt.datetime


class BookingResponse(BaseModel):
    id: int
    customer_name: str
    special_request: str | None
    start_time: dt.datetime
    canceled: bool
    created_at: dt.datetime  


class CancelBookingRequest(BaseModel):
    customer_name: str
    date: dt.date


class CancelBookingResponse(BaseModel):
    canceled_count: int


class ListBookingRequest(BaseModel):
    date: dt.date


# FastAPI App
app = FastAPI()


@app.post("/schedule_booking/")
def schedule_booking(request: BookingRequest, db: Session = Depends(get_db)):
    new_booking = Booking(
        customer_name=request.customer_name,
        special_request=request.special_request,
        start_time=request.start_time,
    )
    db.add(new_booking)
    db.commit()  
    db.refresh(new_booking)

    new_booking_return_obj = BookingResponse(
        id=new_booking.id,
        customer_name=new_booking.customer_name,
        special_request=new_booking.special_request,  
        start_time=new_booking.start_time,
        canceled=new_booking.canceled,
        created_at=new_booking.created_at,
    )
    return new_booking_return_obj


@app.post("/cancel_booking/")
def cancel_booking(request: CancelBookingRequest, db: Session = Depends(get_db)):
    start_dt = dt.datetime.combine(request.date, dt.time.min)
    end_dt = start_dt + dt.timedelta(days=1)

    result = db.execute(
        select(Booking)
        .where(Booking.customer_name == request.customer_name)
        .where(Booking.start_time >= start_dt)
        .where(Booking.start_time <= end_dt)
        .where(Booking.canceled == False)
    )

    bookings = result.scalars().all()
    if not bookings:  
        raise HTTPException(
            status_code=404,
            detail="No matching booking for the details found in our system",
        )

    for booking in bookings:
        booking.canceled = True  

    db.commit()  

    return CancelBookingResponse(canceled_count=len(bookings))


@app.post("/list_bookings/")
def list_bookings(request: ListBookingRequest, db: Session = Depends(get_db)):
    start_dt = dt.datetime.combine(request.date, dt.time.min)
    end_dt = start_dt + dt.timedelta(days=1)

    result = db.execute(
        select(Booking)
        .where(Booking.canceled == False)
        .where(Booking.start_time >= start_dt)
        .where(Booking.start_time <= end_dt)
        .order_by(Booking.start_time.asc())
    )

    bookings = result.scalars().all()
    booked_booking = []
    for booking in bookings:
        booking_obj = BookingResponse(
            id=booking.id,
            customer_name=booking.customer_name,
            special_request=booking.special_request,
            start_time=booking.start_time,
            canceled=booking.canceled,
            created_at=booking.created_at,
        )
        booked_booking.append(booking_obj)  

    return booked_booking


if __name__ == "__main__":  
    uvicorn.run("main:app", host="127.0.0.1", port=4444, reload=True)