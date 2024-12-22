// featured-equipment.js
document.addEventListener('alpine:init', () => {
    Alpine.data('featuredEquipment', () => ({
        equipment: [
            {
                "id": "123",
                "name": "20\" Chainsaw",
                "category": "Power Tools",
                "image": "/static/dist/img/hero.jpg",
                "dayRate": 45.00,
                "available": true,
                "isNew": false
            },
            {
                "id": "13",
                "name": "20\" Chainsaw",
                "category": "Power Tools",
                "image": "/static/dist/img/hero.jpg",
                "dayRate": 45.00,
                "available": true,
                "isNew": false
            },
            {
                "id": "23",
                "name": "20\" Chainsaw",
                "category": "Power Tools",
                "image": "/static/dist/img/hero.jpg",
                "dayRate": 45.00,
                "available": true,
                "isNew": false
            },
            {
                "id": "1263",
                "name": "20\" Chainsaw",
                "category": "Power Tools",
                "image": "/static/dist/img/hero.jpg",
                "dayRate": 45.00,
                "available": true,
                "isNew": false
            }
        ],
        loading: true,//false
        error: null,

        /*
        async fetchEquipment() {
            this.loading = true;
            this.error = null;

            try {
                const response = await fetch('/api/featured-equipment');
                if (!response.ok) {
                    throw new Error('Failed to fetch equipment');
                }
                
                this.equipment = await response.json();
            } catch (err) {
                this.error = 'Unable to load featured equipment. Please try again later.';
                console.error('Error fetching equipment:', err);
            } finally {
                this.equipment = {
                    "id": "123",
                    "name": "20\" Chainsaw",
                    "category": "Power Tools",
                    "image": "/static/dist/img/hero.jpg",
                    "dayRate": 45.00,
                    "available": true,
                    "isNew": false
                };
                this.loading = true; // false
            }
        },*/

        rentEquipment(item) {
            // Navigate to rental page or open rental modal
            window.location.href = `/rent/${item.id}`;
        },

        viewDetails(item) {
            // Navigate to equipment details page
            window.location.href = `/equipment/${item.id}`;
        }
    }));
});

/* Expected API Response Format:
{
    "id": "123",
    "name": "20\" Chainsaw",
    "category": "Power Tools",
    "image": "/static/dist/img/hero.jpg",
    "dayRate": 45.00,
    "available": true,
    "isNew": false
}
*/