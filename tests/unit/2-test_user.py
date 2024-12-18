"""
Tests for user routes
"""
from flask import json


class TestUserRoutes:
    def test_get_users_admin(self, client, admin_token):
        """Test getting users list as admin"""
        response = client.get(
            '/api/users',
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
            f'/api/users/{regular_user.id}',
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["id"] == regular_user.id
        assert data["email"] == regular_user.email

    def test_get_user_self(self, client, regular_user, user_token):
        """Test getting own user details"""
        response = client.get(
            f'/api/users/{regular_user.id}',
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["id"] == regular_user.id
        assert data["email"] == regular_user.email

    def test_get_user_other_unauthorized(self, client, admin_user, user_token):
        """Test getting other user's details as regular user"""
        response = client.get(
            f'/api/users/{admin_user.id}',
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 403

    def test_get_users_unauthorized(self, client, user_token):
        """Test getting users list as regular user"""
        response = client.get(
            '/api/users',
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
            f'/api/users/{regular_user.id}',
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
