"""
Application Models
"""

from app import db
from sqlalchemy.orm import mapped_column, relationship, Mapped
from sqlalchemy import Integer, String, Float, ForeignKey, DateTime, Enum
# from sqlalchemy.dialects.postgresql import JSON

import enum
from typing import Optional, List
from datetime import datetime, timezone


class User(db.Model):
    """
    The User model
    """
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64))
    email: Mapped[str] = mapped_column(String(64), index=True, unique=True)
    image_path: Mapped[Optional[str]] = mapped_column(String(256))
    
    # Role relationship (users can have multiple roles)
    role_id: Mapped[Optional[int]] = mapped_column(ForeignKey('role.id'))
    role: Mapped["Role"] = relationship("Role", backref="users")

    class Status(enum.Enum):
        PENDING = "pending"
        ACTIVE = "active"
        INACTIVE = "inactive"
        BANNED = "banned"

    status: Mapped[Status] = mapped_column(Enum(Status), default=Status.PENDING.value)
    company: Mapped[str] = mapped_column(String(64))
    password_hash: Mapped[Optional[str]] = mapped_column(String(256))
    location_id: Mapped[Optional[int]] = mapped_column(ForeignKey("location.id"))
    location: Mapped[Optional["Location"]] = relationship("Location", back_populates="users")

    bookings: Mapped[List["Booking"]] = relationship("Booking", back_populates="user")

    def __repr__(self) -> str:
        return f"<User {self.name}>"


class Role(db.Model):
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
    # images: Mapped[List[str]] = mapped_column(JSON, default=List)
    price_per_day: Mapped[float] = mapped_column(Float, nullable=False, default=100_000.0)

    class Status(enum.Enum):
        AVAILABLE = "available"
        MAINTENANCE = "maintenance"
        RENTED = "rented"
    
    status: Mapped[Status] = mapped_column(Enum(Status), default=Status.AVAILABLE.value)

    location_id: Mapped[Optional[int]] = mapped_column(ForeignKey("location.id"))
    location: Mapped[Optional["Location"]] = relationship("Location", back_populates="equipment")
    
    bookings: Mapped[List["Booking"]] = relationship("Booking", back_populates="equipment")

    def __repr__(self) -> str:
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

    users: Mapped[List["User"]] = relationship("User", back_populates="location")
    equipment: Mapped[List["Equipment"]] = relationship("Equipment", back_populates="location")

    def __repr__(self) -> str:
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

    # Fixed: Changed WriteOnlyMapped to regular Mapped for many-to-one relationships
    user: Mapped["User"] = relationship("User", back_populates="bookings")
    equipment: Mapped["Equipment"] = relationship("Equipment", back_populates="bookings")

    def __repr__(self) -> str:
        equipment_name = self.equipment.name if self.equipment else "N/A"
        user_name = self.user.name if self.user else "N/A"
        return f"<Booking {self.id} - {equipment_name} by {user_name}>"


