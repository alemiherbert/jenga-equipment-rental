"""
Tests for database models
"""

import pytest
from datetime import datetime, timedelta, timezone
from app import db
from app.models import User, Equipment, Location, Booking, Payment


@pytest.fixture
def app():
    """Create and configure a test application instance."""
    from app import create_app
    app = create_app('testing')

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def test_location(app):
    """Create a test location."""
    location = Location(
        name="Meraki Construction Offices",
        address="123 Mega St",
        city="Kampala",
        latitude=0.347596,
        longitude=32.582520
    )
    db.session.add(location)
    db.session.commit()
    return location


@pytest.fixture
def test_user(app, test_location):
    """Create a test user."""
    user = User(
        name="Alemi Herbert",
        email="alemiherbert@example.com",
        phone="0772345678",
        company="Alemi Consulting",
        location=test_location,
        status=User.Status.ACTIVE
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def test_equipment(app, test_location):
    """Create a test equipment."""
    equipment = Equipment(
        name="CAT Bulldozer",
        price_per_day=100000.0,
        transport_cost_per_km=5000.0,
        location=test_location,
        status=Equipment.Status.AVAILABLE
    )
    db.session.add(equipment)
    db.session.commit()
    return equipment


@pytest.fixture
def test_booking(app, test_user, test_equipment):
    """Create a test booking."""
    start_date = datetime.now(timezone.utc)
    end_date = start_date + timedelta(days=3)
    booking = Booking(
        user=test_user,
        equipment=test_equipment,
        start_date=start_date,
        end_date=end_date,
        distance_km=50.0,
        rental_amount=300000.0,
        transport_amount=250000.0,
        total_amount=550000.0
    )
    db.session.add(booking)
    db.session.commit()
    return booking


@pytest.fixture
def test_payment(app, test_booking, test_user):
    """Create a test payment."""
    payment = Payment(
        booking=test_booking,
        user=test_user,
        rental_amount=300000.0,
        transport_amount=250000.0,
        total_amount=550000.0,
        stripe_payment_intent_id="pi_test_123",
        stripe_payment_method_id="pm_test_123"
    )
    db.session.add(payment)
    db.session.commit()
    return payment


class TestLocationModel:
    def test_create_location(self, test_location):
        """Test location creation."""
        assert test_location.id is not None
        assert test_location.name == "Meraki Construction Offices"
        assert test_location.city == "Kampala"
        assert test_location.latitude == pytest.approx(0.347596)
        assert test_location.longitude == pytest.approx(32.582520)

    def test_location_relationships(self, test_location, test_user, test_equipment):
        """Test location relationships."""
        assert test_user in test_location.users
        assert test_equipment in test_location.equipment


class TestUserModel:
    def test_create_user(self, test_user):
        """Test user creation."""
        assert test_user.id is not None
        assert test_user.name == "Alemi Herbert"
        assert test_user.email == "alemiherbert@example.com"
        assert test_user.phone == "0772345678"
        assert test_user.status == User.Status.ACTIVE


    def test_user_location_relationship(self, test_user, test_location):
        """Test user-location relationship."""
        assert test_user.location == test_location
        assert test_user in test_location.users


class TestEquipmentModel:
    def test_create_equipment(self, test_equipment):
        """Test equipment creation."""
        assert test_equipment.id is not None
        assert test_equipment.name == "CAT Bulldozer"
        assert test_equipment.price_per_day == 100000.0
        assert test_equipment.transport_cost_per_km == 5000.0
        assert test_equipment.status == Equipment.Status.AVAILABLE

    def test_equipment_location_relationship(self, test_equipment, test_location):
        """Test equipment-location relationship."""
        assert test_equipment.location == test_location
        assert test_equipment in test_location.equipment


class TestBookingModel:
    def test_create_booking(self, test_booking):
        """Test booking creation."""
        assert test_booking.id is not None
        assert test_booking.distance_km == 50.0
        assert test_booking.rental_amount == 300000.0
        assert test_booking.transport_amount == 250000.0
        assert test_booking.total_amount == 550000.0

    def test_booking_relationships(self, test_booking, test_user, test_equipment):
        """Test booking relationships."""
        assert test_booking.user == test_user
        assert test_booking.equipment == test_equipment
        assert test_booking in test_user.bookings
        assert test_booking in test_equipment.bookings


class TestPaymentModel:
    def test_create_payment(self, test_payment):
        """Test payment creation."""
        assert test_payment.id is not None
        assert test_payment.rental_amount == 300000.0
        assert test_payment.transport_amount == 250000.0
        assert test_payment.total_amount == 550000.0
        assert test_payment.stripe_payment_intent_id == "pi_test_123"
        assert test_payment.stripe_payment_method_id == "pm_test_123"

    def test_payment_relationships(self, test_payment, test_booking, test_user):
        """Test payment relationships."""
        assert test_payment.booking == test_booking
        assert test_payment.user == test_user
        assert test_payment in test_booking.payments
        assert test_payment in test_user.payments

    def test_payment_timestamps(self, test_payment):
        """Test payment timestamp fields."""
        assert test_payment.created_at is not None
        assert test_payment.updated_at is not None
        assert isinstance(test_payment.created_at, datetime)
        assert isinstance(test_payment.updated_at, datetime)
