import pytest
from app import create_app, db
from app.models import User, Equipment, Role


@pytest.fixture(scope='session')
def app():
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def client(app):
    return app.test_client()

@pytest.fixture(scope='function')
def runner(app):
    return app.test_cli_runner()

@pytest.fixture(scope='function')
def session(app):
    with app.app_context():
        yield db.session


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