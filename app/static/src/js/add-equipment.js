document.addEventListener('alpine:init', () => {
    Alpine.data('equipmentForm', () => ({
        equipment: {
            name: '',
            category: '',
            location_id: '',
            price_per_day: '',
            transport_cost_per_km: '',
            image: null
        },
        locations: [],
        fetchLocations() {
            fetch('/api/locations')
                .then(response => response.json())
                .then(data => {
                    this.locations = data.items;
                })
                .catch(error => {
                    console.error('Error fetching locations:', error);
                });
        },
        createEquipment() {
            if (!this.equipment.name || !this.equipment.category || !this.equipment.location_id) {
                alert('Please fill in all required fields.');
                return;
            }

            if (!this.equipment.price_per_day || isNaN(parseFloat(this.equipment.price_per_day))) {
                alert('Please enter a valid price per day.');
                return;
            }
            if (!this.equipment.transport_cost_per_km || isNaN(parseFloat(this.equipment.transport_cost_per_km))) {
                alert('Please enter a valid transport cost per km.');
                return;
            }

            if (this.equipment.image && this.equipment.image.size > 5 * 1024 * 1024) {
                alert('The image file size must not exceed 5 MB.');
                return;
            }

            const formData = new FormData();
            formData.append('name', this.equipment.name);
            formData.append('category', this.equipment.category);
            formData.append('location_id', this.equipment.location_id);
            formData.append('price_per_day', parseFloat(this.equipment.price_per_day));
            formData.append('transport_cost_per_km', parseFloat(this.equipment.transport_cost_per_km));

            if (this.equipment.image) {
                formData.append('image', this.equipment.image);
            }

            fetch('/api/equipment', {
                method: 'POST',
                body: formData
            })
                .then(response => response.json())
                .then(data => {
                    if (data.msg) {
                        alert(data.msg);
                    } else {
                        alert('Error creating equipment');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                }).finally(() => { window.location.href = '/admin/equipment' }
                );
        },
        init() {
            this.fetchLocations();
        }
    }));
});