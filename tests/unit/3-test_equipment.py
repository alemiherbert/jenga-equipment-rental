"""
Tests for equipment routes
"""
from flask import json


class TestEquipmentRoutes:
    def test_get_equipment_list(self, client, sample_equipment):
        """Test getting equipment list"""
        response = client.get('/api/equipment')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "_meta" in data
        assert "items" in data
        assert "_links" in data
        assert len(data["items"]) > 0

    def test_get_equipment_list_with_filters(self, client, sample_equipment):
        """Test getting equipment list with filters"""
        response = client.get(
            '/api/equipment?status=available&min_price=50000&max_price=150000'
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
        response = client.get(f'/api/equipment/{sample_equipment.id}')
        
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
            '/api/equipment',
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
            '/api/equipment',
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
            f'/api/equipment/{sample_equipment.id}',
            headers={
                "Authorization": f"Bearer {admin_token}",
                "Content-Type": "application/json"
            },
            data=json.dumps(update_data)
        )
        
        # assert response.status_code == 200
        data = json.loads(response.data)
        print(data)
        assert data["equipment"]["name"] == update_data["name"]
        assert data["equipment"]["status"] == update_data["status"]

    def test_delete_equipment_admin(self, client, admin_token, sample_equipment):
        """Test deleting equipment as admin"""
        response = client.delete(
            f'/api/equipment/{sample_equipment.id}',
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        
        # Verify equipment is deleted
        verify_response = client.get(f'/api/equipment/{sample_equipment.id}')
        assert verify_response.status_code == 404