"""
Application Models
"""
from app import db
from sqlalchemy.orm import mapped_column, relationship, Mapped
from sqlalchemy import select, String, Float, ForeignKey, DateTime, Enum, Numeric, Boolean
# from sqlalchemy.dialects.postgresql import JSON
from flask import url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token

import enum
from typing import Optional, List
from datetime import datetime, timezone, timedelta


class TokenBlocklist(db.Model):
    """
    Token blocklist for tracking revoked JWT tokens
    """
    id: Mapped[int] = mapped_column(primary_key=True)
    jti: Mapped[str] = mapped_column(String(36), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    def __repr__(self) -> str:
        return f"<TokenBlocklist {self.jti}>"


class PaginatedAPIMixin(object):
    """
    Add pagination for HATEOAS compliance
    """
    @staticmethod
    def to_collection_dict(query, page, per_page, endpoint, **kwargs):
        resources = db.paginate(query, page=page, per_page=per_page,
                              error_out=False)
        data = {
            'items': [item.to_dict() for item in resources.items],
            '_meta': {
                'page': page,
                'per_page': per_page,
                'total_pages': resources.pages,
                'total_items': resources.total
            },
            '_links': {
                'self': url_for(endpoint, page=page, per_page=per_page,
                              **kwargs),
                'next': url_for(endpoint, page=page + 1, per_page=per_page,
                              **kwargs) if resources.has_next else None,
                'prev': url_for(endpoint, page=page - 1, per_page=per_page,
                              **kwargs) if resources.has_prev else None
            }
        }
        return data


class User(PaginatedAPIMixin, db.Model):
    """
    The User model
    """
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64))
    email: Mapped[str] = mapped_column(String(64), index=True, unique=True)
    phone: Mapped[str] = mapped_column(String(64), index=True, unique=True)
    image_path: Mapped[Optional[str]] = mapped_column(String(256))
    
    # Role relationship (users can have multiple roles)
    role_id: Mapped[Optional[int]] = mapped_column(ForeignKey("role.id"))
    role: Mapped["Role"] = relationship("Role", backref="users")

    class Status(enum.Enum):
        PENDING = "pending"
        ACTIVE = "active"
        INACTIVE = "inactive"
        BANNED = "banned"

    status: Mapped[Status] = mapped_column(Enum(Status), default=Status.PENDING)
    company: Mapped[str] = mapped_column(String(64))
    password_hash: Mapped[Optional[str]] = mapped_column(String(256))
    location_id: Mapped[Optional[int]] = mapped_column(ForeignKey("location.id"))
    location: Mapped[Optional["Location"]] = relationship("Location", back_populates="users")
    
    # Token management
    token_version: Mapped[int] = mapped_column(default=0)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime)

    payments: Mapped[List["Payment"]] = relationship("Payment", back_populates="user") # type: ignore
    bookings: Mapped[List["Booking"]] = relationship("Booking", back_populates="user")

    def to_dict(self, include_email=True):
        """Serialize user object to dictionary"""
        data = {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'company': self.company,
            'status': self.status.value,
            'role': self.role.name if self.role else None,
            'location': self.location.name if self.location else None,
            'image_path': self.image_path,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            '_links': {
                'self': url_for('api.get_user', user_id=self.id)
            }
        }
        if include_email:
            data['email'] = self.email
        return data

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def get_tokens(self) -> dict:
        """Generate access and refresh tokens"""
        # Update last login timestamp
        self.last_login = datetime.now(timezone.utc)
        db.session.commit()
        
        access_token = create_access_token(
            identity=self,
            fresh=True,
            expires_delta=timedelta(minutes=15),
            additional_claims={
                "token_version": self.token_version,
                "role": self.role.name if self.role else None,
                "status": self.status.value
            }
        )
        
        refresh_token = create_refresh_token(
            identity=self,
            expires_delta=timedelta(days=7),
            additional_claims={
                "token_version": self.token_version
            }
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 90000 # 900
        }
    
    def revoke_tokens(self) -> None:
        """Revoke all tokens for this user"""
        self.token_version += 1
        db.session.commit()
    
    @staticmethod
    def verify_by_email(email: str) -> Optional["User"]:
        """Verify if user exists using their email"""
        return db.session.scalar(select(User).where(User.email == email))

    def __repr__(self) -> str:
        return f"<User {self.name}>"


class Role(db.Model):
    """
    Role model
    """
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64))


class Equipment(PaginatedAPIMixin, db.Model):
    """
    Equipment model
    """
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64))
    # images: Mapped[List[str]] = mapped_column(JSON, default=List)
    price_per_day: Mapped[float] = mapped_column(Float, nullable=False, default=100_000.0)
    transport_cost_per_km: Mapped[float] = mapped_column(Float, nullable=False, default=5_000.0)

    # Category shall later have to be a model
    category: Mapped[Optional[str]] = mapped_column(String(64))

    stripe_product_id: Mapped[Optional[str]] = mapped_column(String(128))

    class Status(enum.Enum):
        AVAILABLE = "available"
        MAINTENANCE = "maintenance"
        RENTED = "rented"
    
    status: Mapped[Status] = mapped_column(Enum(Status), default=Status.AVAILABLE)
    featured: Mapped[bool] = mapped_column(Boolean, default=False)
    location_id: Mapped[Optional[int]] = mapped_column(ForeignKey("location.id"))
    location: Mapped[Optional["Location"]] = relationship("Location", back_populates="equipment")
    bookings: Mapped[List["Booking"]] = relationship("Booking", back_populates="equipment")
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc))

    def calculate_feature_score(self) -> float:
        """Calculate the feature score based on weighted criteria:
        1. Rental Frequency: 25% - Based on last 90 days rentals
        2. Availability Status: 45% - Based on current status
        3. Recent Additions: 10% - Added within last 30 days
        4. Profitability: 20% - Normalized price per day
        """
        now = datetime.now(timezone.utc)
        
        rental_count = db.session.query(
            db.func.count(Booking.id)
        ).filter(
            Booking.equipment_id == self.id,
            Booking.start_date >= now - timedelta(days=90),
            Booking.status != Booking.Status.CANCELLED
        ).scalar() or 0
        
        max_rentals = 10
        rental_score = min(rental_count / max_rentals, 1.0)
        
        availability_score = 1 if self.status == self.Status.AVAILABLE else 0
        # Ensure created_at has timezone info
        created_at = self.created_at.replace(tzinfo=timezone.utc) if self.created_at and self.created_at.tzinfo is None else self.created_at
        recent_addition_score = 1 if (
            created_at and
            created_at >= now - timedelta(days=30)
        ) else 0
        
        max_price = db.session.query(db.func.max(Equipment.price_per_day)).scalar()
        if not max_price or max_price <= 0:
            profitability_score = 0
        else:
            profitability_score = min(self.price_per_day / max_price, 1.0)
        
        feature_score = (
            rental_score * 0.25 +
            availability_score * 0.45 +
            recent_addition_score * 0.1 +
            profitability_score * 0.2
        )
        
        return round(feature_score, 3)

    def update_featured_status(self):
        """Update the featured status based on the feature score."""
        self.featured = self.calculate_feature_score() >= 0.7 

    def to_dict(self) -> dict:
        """Serialize equipment object to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'price_per_day': self.price_per_day,
            'transport_cost_per_km': self.transport_cost_per_km,
            'status': self.status.value,
            'featured': self.featured,
            'location': self.location.name if self.location else None,
            'stripe_product_id': self.stripe_product_id,
            '_links': {
                'self': url_for('api.get_equipment', equipment_id=self.id)
            }
        }

    def __repr__(self) -> str:
        return f"<Equipment {self.name} at Location {self.location.name if self.location else 'N/A'}>"


class Location(PaginatedAPIMixin, db.Model):
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

    def to_dict(self):
        """Serialize location object to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'city': self.city,
            'region': self.region,
            'country': self.country,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'object_id': self.object_id,
            'object_type': self.object_type,
            '_links': {
                'self': url_for('api.get_location', location_id=self.id)
            }
        }

    def __repr__(self) -> str:
        return f"<Location {self.name or self.city}>"


payment_booking_association = db.Table(
    'payment_booking_association',
    db.Column('payment_id', db.Integer, db.ForeignKey('payment.id'), primary_key=True),
    db.Column('booking_id', db.Integer, db.ForeignKey('booking.id'), primary_key=True)
)


class Booking(PaginatedAPIMixin, db.Model):
    """
    Booking model
    """
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    equipment_id: Mapped[int] = mapped_column(ForeignKey("equipment.id"))
    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    # Distance and cost calculations
    distance_km: Mapped[float] = mapped_column(Float, nullable=False)
    rental_amount: Mapped[float] = mapped_column(Numeric(10, 2))
    transport_amount: Mapped[float] = mapped_column(Numeric(10, 2))
    total_amount: Mapped[float] = mapped_column(Numeric(10, 2))
    currency: Mapped[str] = mapped_column(String(3), default="UGX")
    
    class Status(enum.Enum):
        PENDING = "pending"
        PAYMENT_REQUIRED = "payment_required"
        CONFIRMED = "confirmed"
        CANCELLED = "cancelled"
        COMPLETED = "completed"
    
    status: Mapped[Status] = mapped_column(Enum(Status), default=Status.PENDING)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc))

    user: Mapped["User"] = relationship("User", back_populates="bookings")
    equipment: Mapped["Equipment"] = relationship("Equipment", back_populates="bookings")
    
    # Relationship to Payment via the association table
    payment: Mapped[Optional["Payment"]] = relationship(
        "Payment",
        secondary=payment_booking_association,
        back_populates="bookings"
    )

    def to_dict(self):
        """Serialize booking object to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'equipment_id': self.equipment_id,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'distance_km': self.distance_km,
            'rental_amount': float(self.rental_amount),
            'transport_amount': float(self.transport_amount),
            'total_amount': float(self.total_amount),
            'currency': self.currency,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'equipment_name': self.equipment.name if self.equipment else None,
            'user_name': self.user.name if self.user else None,
            'payment_id': self.payment.id if self.payment else None,
            '_links': {
                'self': url_for('api.get_booking', booking_id=self.id),
                'user': url_for('api.get_user', user_id=self.user_id),
                'equipment': url_for('api.get_equipment', equipment_id=self.equipment_id)
            }
        }

    def __repr__(self) -> str:
        equipment_name = self.equipment.name if self.equipment else "N/A"
        user_name = self.user.name if self.user else "N/A"
        return f"<Booking {self.id} - {equipment_name} by {user_name}>"


class Payment(db.Model):
    """
    Payment model for tracking payments
    """
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    
    total_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="UGX")
    payment_method: Mapped[Optional[str]] = mapped_column(String(64))
    payment_reference: Mapped[Optional[str]] = mapped_column(String(64))
    
    class Status(enum.Enum):
        PENDING = "pending"
        SUCCEEDED = "succeeded"
        FAILED = "failed"
        REFUNDED = "refunded"
    
    status: Mapped[Status] = mapped_column(Enum(Status), default=Status.PENDING)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc)
    )
    
    bookings: Mapped[List["Booking"]] = relationship(
        "Booking",
        secondary=payment_booking_association,
        back_populates="payment"
    )
    
    user: Mapped["User"] = relationship("User", back_populates="payments")
    
    def to_dict(self):
        """Serialize payment object to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'total_amount': float(self.total_amount),
            'currency': self.currency,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'booking_ids': [booking.id for booking in self.bookings],
            '_links': {
                'self': url_for('api.get_payment', payment_id=self.id),
                'user': url_for('api.get_user', user_id=self.user_id)
            }
        }
   
    def __repr__(self) -> str:
        return f"<Payment {self.id} - {self.total_amount} {self.currency} - {self.status}>"
