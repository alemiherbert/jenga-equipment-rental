"""
Tests for main application routes
"""

import pytest
from flask import json
from datetime import datetime, timezone
from app import db
from app.models import User, Equipment, Role


@pytest.fixture(scope="function")
def admin_role(app):
    """Create admin role"""
    role = Role(name="admin")
    db.session.add(role)
    db.session.commit()
    db.session.refresh(role)
    return role


@pytest.fixture(scope="function")
def admin_user(app, admin_role):
    """Create admin user"""
    user = User(
        name="Admin User",
        email="admin@example.com",
        phone="0712345678",
        company="Admin Corp",
        role=admin_role,
        status=User.Status.ACTIVE
    )
    user.set_password("adminpass123")
    db.session.add(user)
    db.session.commit()
    db.session.refresh(user)
    return user


@pytest.fixture
def regular_user(app):
    """Create regular user"""
    # Clear the session
    db.session.expunge_all()
    user = User(
        name="Regular User",
        email="user@example.com",
        phone="0723456789",
        company="User Corp",
        status=User.Status.ACTIVE
    )
    user.set_password("userpass123")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def admin_token(admin_user):
    """Get admin user token"""
    return admin_user.get_tokens()["access_token"]


@pytest.fixture
def user_token(regular_user):
    """Get regular user token"""
    return regular_user.get_tokens()["access_token"]


@pytest.fixture
def sample_equipment(app):
    """Create sample equipment"""
    equipment = Equipment(
        name="Test Equipment",
        price_per_day=100000.0,
        transport_cost_per_km=5000.0,
        status=Equipment.Status.AVAILABLE
    )
    db.session.add(equipment)
    db.session.commit()
    return equipment


@pytest.fixture(autouse=True)
def cleanup_users(app):
    """Clean up users after each test."""
    yield
    with app.app_context():
        db.session.query(User).delete()
        db.session.commit()


class TestUserRoutes:
    def test_get_users_admin(self, client, admin_token):
        """Test getting users list as admin"""
        response = client.get(
            '/users',
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "_meta" in data
        assert "items" in data
        assert "_links" in data
        assert data["_meta"]["page"] == 1

    def test_get_user_admin(self, client, regular_user, admin_token):
        """Test getting a user as admin"""
        response = client.get(
            f'/users/{regular_user.id}',
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["id"] == regular_user.id
        assert data["email"] == regular_user.email

    def test_get_user_self(self, client, regular_user, user_token):
        """Test getting own user details"""
        response = client.get(
            f'/users/{regular_user.id}',
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["id"] == regular_user.id
        assert data["email"] == regular_user.email

    def test_get_user_other_unauthorized(self, client, admin_user, user_token):
        """Test getting other user's details as regular user"""
        response = client.get(
            f'/users/{admin_user.id}',
            headers={"Authorization": f"Bearer {user_token}"}
        )
        print("----------------------", response.data)
        assert response.status_code == 403

    def test_get_users_unauthorized(self, client, user_token):
        """Test getting users list as regular user"""
        response = client.get(
            '/users',
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 403

    def test_update_user_self(self, client, regular_user, user_token):
        """Test updating own user details"""
        update_data = {
            "name": "Updated Name",
            "phone": "0787654321",
            "company": "Updated Corp"
        }
        
        response = client.put(
            f'/users/{regular_user.id}',
            headers={
                "Authorization": f"Bearer {user_token}",
                "Content-Type": "application/json"
            },
            data=json.dumps(update_data)
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["user"]["name"] == update_data["name"]
        assert data["user"]["phone"] == update_data["phone"]
        assert data["user"]["company"] == update_data["company"]


class TestEquipmentRoutes:
    def test_get_equipment_list(self, client, sample_equipment):
        """Test getting equipment list"""
        response = client.get('/equipment')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "_meta" in data
        assert "items" in data
        assert "_links" in data
        assert len(data["items"]) > 0

    def test_get_equipment_list_with_filters(self, client, sample_equipment):
        """Test getting equipment list with filters"""
        response = client.get(
            '/equipment?status=available&min_price=50000&max_price=150000'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data["items"]) > 0
        for item in data["items"]:
            assert item["status"] == "available"
            assert item["price_per_day"] >= 50000
            assert item["price_per_day"] <= 150000

    def test_get_equipment_detail(self, client, sample_equipment):
        """Test getting equipment details"""
        response = client.get(f'/equipment/{sample_equipment.id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["id"] == sample_equipment.id
        assert data["name"] == sample_equipment.name

    def test_create_equipment_admin(self, client, admin_token):
        """Test creating equipment as admin"""
        equipment_data = {
            "name": "New Equipment",
            "price_per_day": 150000.0,
            "transport_cost_per_km": 6000.0
        }
        
        response = client.post(
            '/equipment',
            headers={
                "Authorization": f"Bearer {admin_token}",
                "Content-Type": "application/json"
            },
            data=json.dumps(equipment_data)
        )
        assert response.status_code == 201
        data = json.loads(response.data)
        assert "equipment" in data
        assert data["equipment"]["name"] == equipment_data["name"]

    def test_create_equipment_unauthorized(self, client, user_token):
        """Test creating equipment as regular user"""
        equipment_data = {
            "name": "New Equipment",
            "price_per_day": 150000.0,
            "transport_cost_per_km": 6000.0
        }
        
        response = client.post(
            '/equipment',
            headers={
                "Authorization": f"Bearer {user_token}",
                "Content-Type": "application/json"
            },
            data=json.dumps(equipment_data)
        )        
        assert response.status_code == 403

    def test_update_equipment_admin(self, client, admin_token, sample_equipment):
        """Test updating equipment as admin"""
        update_data = {
            "name": "Updated Equipment",
            "price_per_day": 200000.0,
            "status": "maintenance"
        }
        
        response = client.put(
            f'/equipment/{sample_equipment.id}',
            headers={
                "Authorization": f"Bearer {admin_token}",
                "Content-Type": "application/json"
            },
            data=json.dumps(update_data)
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["equipment"]["name"] == update_data["name"]
        assert data["equipment"]["status"] == update_data["status"]

    def test_delete_equipment_admin(self, client, admin_token, sample_equipment):
        """Test deleting equipment as admin"""
        response = client.delete(
            f'/equipment/{sample_equipment.id}',
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        
        # Verify equipment is deleted
        verify_response = client.get(f'/equipment/{sample_equipment.id}')
        assert verify_response.status_code == 404