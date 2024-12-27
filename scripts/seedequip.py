from datetime import datetime, timedelta, timezone
from sqlalchemy import create_engine, select
from app.models import Equipment, Location

# Database connection
from app import db

# Sample data for equipment
equipment_data = [
    # Earthmoving Equipment
    {"name": "CAT 320 Excavator", "category": "Earthmoving", "price_per_day": 150000, "transport_cost_per_km": 7000},
    {"name": "Komatsu PC210LC-11 Excavator", "category": "Earthmoving", "price_per_day": 140000, "transport_cost_per_km": 6500},
    {"name": "CAT D6T Bulldozer", "category": "Earthmoving", "price_per_day": 180000, "transport_cost_per_km": 8000},
    {"name": "John Deere 850K Dozer", "category": "Earthmoving", "price_per_day": 170000, "transport_cost_per_km": 7500},
    {"name": "CAT 950M Wheel Loader", "category": "Earthmoving", "price_per_day": 160000, "transport_cost_per_km": 7000},
    {"name": "Volvo L120H Wheel Loader", "category": "Earthmoving", "price_per_day": 155000, "transport_cost_per_km": 6800},
    {"name": "CAT 430F Backhoe Loader", "category": "Earthmoving", "price_per_day": 130000, "transport_cost_per_km": 6000},
    {"name": "Case 580 Super N Backhoe Loader", "category": "Earthmoving", "price_per_day": 135000, "transport_cost_per_km": 6200},
    {"name": "CAT 14M Motor Grader", "category": "Earthmoving", "price_per_day": 145000, "transport_cost_per_km": 6700},
    {"name": "Komatsu GD825A Motor Grader", "category": "Earthmoving", "price_per_day": 140000, "transport_cost_per_km": 6500},

    # Material Handling Equipment
    {"name": "Liebherr LTM 1200-5.1 Crane", "category": "Material Handling", "price_per_day": 200000, "transport_cost_per_km": 10000},
    {"name": "Terex AC 350 Crane", "category": "Material Handling", "price_per_day": 190000, "transport_cost_per_km": 9500},
    {"name": "Toyota 8FGCU25 Forklift", "category": "Material Handling", "price_per_day": 50000, "transport_cost_per_km": 3000},
    {"name": "Hyster H50FT Forklift", "category": "Material Handling", "price_per_day": 52000, "transport_cost_per_km": 3100},
    {"name": "JCB 540-170 Telehandler", "category": "Material Handling", "price_per_day": 80000, "transport_cost_per_km": 4000},
    {"name": "Manitou MLA 628 Telehandler", "category": "Material Handling", "price_per_day": 82000, "transport_cost_per_km": 4100},
    {"name": "CAT TH357 Telehandler", "category": "Material Handling", "price_per_day": 85000, "transport_cost_per_km": 4200},
    {"name": "Terex Conveyor Belt", "category": "Material Handling", "price_per_day": 30000, "transport_cost_per_km": 2000},
    {"name": "Ingersoll Rand Hoist", "category": "Material Handling", "price_per_day": 25000, "transport_cost_per_km": 1500},
    {"name": "Genie GTH-1056 Telehandler", "category": "Material Handling", "price_per_day": 83000, "transport_cost_per_km": 4150},

    # Construction Vehicles
    {"name": "CAT 777F Dump Truck", "category": "Construction Vehicles", "price_per_day": 220000, "transport_cost_per_km": 11000},
    {"name": "Komatsu HD785-7 Dump Truck", "category": "Construction Vehicles", "price_per_day": 210000, "transport_cost_per_km": 10500},
    {"name": "Volvo FMX Concrete Mixer Truck", "category": "Construction Vehicles", "price_per_day": 180000, "transport_cost_per_km": 9000},
    {"name": "Schwing Stetter Concrete Mixer Truck", "category": "Construction Vehicles", "price_per_day": 185000, "transport_cost_per_km": 9200},
    {"name": "CAT 740 Off-Highway Truck", "category": "Construction Vehicles", "price_per_day": 230000, "transport_cost_per_km": 11500},
    {"name": "BelAZ 75710 Dump Truck", "category": "Construction Vehicles", "price_per_day": 250000, "transport_cost_per_km": 12000},
    {"name": "Ford F-550 Flatbed Truck", "category": "Construction Vehicles", "price_per_day": 70000, "transport_cost_per_km": 3500},
    {"name": "Isuzu NPR Water Tanker", "category": "Construction Vehicles", "price_per_day": 75000, "transport_cost_per_km": 3700},
    {"name": "Mack Granite Dump Truck", "category": "Construction Vehicles", "price_per_day": 210000, "transport_cost_per_km": 10500},
    {"name": "Peterbilt 567 Refueler", "category": "Construction Vehicles", "price_per_day": 80000, "transport_cost_per_km": 4000},

    # Compaction Equipment
    {"name": "CAT CS533E Vibratory Roller", "category": "Compaction", "price_per_day": 90000, "transport_cost_per_km": 4500},
    {"name": "Bomag BW213D Vibratory Roller", "category": "Compaction", "price_per_day": 85000, "transport_cost_per_km": 4300},
    {"name": "Sakai SW850 Plate Compactor", "category": "Compaction", "price_per_day": 30000, "transport_cost_per_km": 2000},
    {"name": "Wacker Neuson WP1550 Plate Compactor", "category": "Compaction", "price_per_day": 32000, "transport_cost_per_km": 2100},
    {"name": "Dynapac CA2500D Roller", "category": "Compaction", "price_per_day": 88000, "transport_cost_per_km": 4400},
    {"name": "Hamm HD12VV Tandem Roller", "category": "Compaction", "price_per_day": 87000, "transport_cost_per_km": 4350},
    {"name": "Multiquip MVC-88V Plate Compactor", "category": "Compaction", "price_per_day": 31000, "transport_cost_per_km": 2050},
    {"name": "Ingersoll Rand SD-117DX Roller", "category": "Compaction", "price_per_day": 86000, "transport_cost_per_km": 4300},
    {"name": "Amman AV110 Roller", "category": "Compaction", "price_per_day": 84000, "transport_cost_per_km": 4200},
    {"name": "Case CX18C Mini Excavator with Compactor Attachment", "category": "Compaction", "price_per_day": 95000, "transport_cost_per_km": 4700},

    # Paving and Concrete Equipment
    {"name": "CAT AP655F Asphalt Paver", "category": "Paving and Concrete", "price_per_day": 170000, "transport_cost_per_km": 8500},
    {"name": "Volvo P6820C Asphalt Paver", "category": "Paving and Concrete", "price_per_day": 165000, "transport_cost_per_km": 8300},
    {"name": "Schwing SP 500 Concrete Pump", "category": "Paving and Concrete", "price_per_day": 190000, "transport_cost_per_km": 9500},
    {"name": "Putzmeister BSA 1406 Concrete Pump", "category": "Paving and Concrete", "price_per_day": 195000, "transport_cost_per_km": 9600},
    {"name": "Wirtgen W 200i Milling Machine", "category": "Paving and Concrete", "price_per_day": 180000, "transport_cost_per_km": 9000},
    {"name": "LeeBoy 8520 Asphalt Paver", "category": "Paving and Concrete", "price_per_day": 160000, "transport_cost_per_km": 8000},
    {"name": "Allen Engineering Concrete Trowel", "category": "Paving and Concrete", "price_per_day": 40000, "transport_cost_per_km": 2500},
    {"name": "Multiquip MVC-82 Concrete Vibrator", "category": "Paving and Concrete", "price_per_day": 35000, "transport_cost_per_km": 2000},
    {"name": "Gomaco GT-3600 Concrete Paver", "category": "Paving and Concrete", "price_per_day": 200000, "transport_cost_per_km": 10000},
    {"name": "Husqvarna PG 820 Grinder", "category": "Paving and Concrete", "price_per_day": 90000, "transport_cost_per_km": 4500},
]

# Function to seed equipment data
def seed_equipment():
    for item in equipment_data:
        equipment = Equipment(
            name=item["name"],
            category=item["category"],
            price_per_day=item["price_per_day"],
            transport_cost_per_km=item["transport_cost_per_km"],
            created_at=datetime.now(timezone.utc)
        )
        db.session.add(equipment)
    db.session.commit()
    print("Equipment data seeded successfully!")

seed_equipment()