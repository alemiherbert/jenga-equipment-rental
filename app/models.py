"""
Application Models
"""

from app import db
from sqlalchemy.orm import mapped_column, relationship, Mapped, WriteOnlyMapped
from sqlalchemy import Integer, String, Float, ForeignKey, DateTime, Enum
# from sqlalchemy.dialects.postgresql import JSON

import enum
from typing import Optional
from datetime import datetime, timezone


class User(db.Model):
    """
    The User model
    """
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64))
    email: Mapped[str] = mapped_column(String(64), index=True, unique=True)
    image_path: Mapped[Optional[str]] = mapped_column(String(256))
    status: Mapped[int] = mapped_column(Integer, default=0)
    company: Mapped[str] = mapped_column(String(64))
    password_hash: Mapped[Optional[str]] = mapped_column(String(256))

    def __repr__(self):
        return f"<User {self.name}>"

class Roles(db.Model):
    """
    Role model
    """
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64))


class Equipment(db.Model):
    """
    Equipment model
    """
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64))
    # images: Mapped[list[str]] = mapped_column(JSON, default=list)
    location_id: Mapped[Optional[int]] = mapped_column(ForeignKey("location.id"))
    location: WriteOnlyMapped["Location"] = relationship("Location", back_populates="equipment")

    def __repr__(self):
        return f"<Equipment {self.name} at Location {self.location.name if self.location else 'N/A'}>"


class Location(db.Model):
    """
    Generic Location model
    """
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(String(128))
    address: Mapped[Optional[str]] = mapped_column(String(256))
    city: Mapped[Optional[str]] = mapped_column(String(64))
    region: Mapped[Optional[str]] = mapped_column(String(64))
    country: Mapped[Optional[str]] = mapped_column(String(64), default="Uganda")
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    object_id: Mapped[Optional[int]] = mapped_column(nullable=True)
    object_type: Mapped[Optional[str]] = mapped_column(String(64))

    equipment: WriteOnlyMapped[list["Equipment"]] = relationship("Equipment", back_populates="location")

    def __repr__(self):
        return f"<Location {self.name or self.city}>"


class Booking(db.Model):
    """
    Booking model
    """
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    equipment_id: Mapped[int] = mapped_column(ForeignKey('equipment.id'))
    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    class Status(enum.Enum):
        PENDING = "pending"
        CONFIRMED = "confirmed"
        CANCELLED = "cancelled"
        COMPLETED = "completed"
    
    status: Mapped[Status] = mapped_column(Enum(Status), default=Status.PENDING.value)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc))

    user: WriteOnlyMapped["User"] = relationship("User", back_populates="bookings")
    equipment: WriteOnlyMapped["Equipment"] = relationship("Equipment", back_populates="bookings")

    def __repr__(self):
        equipment_name = self.equipment.name if self.equipment else "N/A"
        user_name = self.user.name if self.user else "N/A"
        return f"<Booking {self.id} - {equipment_name} by {user_name}>"
