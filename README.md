# Jenga Equipment Rental
An construction equipment rental service built in python (flask)

Its live here: https://charis.systems/apidocs

## Team
- Alemi Herbert <alemiherbert@gmail.com>

## Motivation
To get my hands as dirty as possible with code -- only utilising unopinionated libraries that will allow me to write as much code as possible.

## Installation
### Clone the app repo
```(bash)
git clone https://github.com/alemiherbert/jenga-equipment-rental.git

cd jenga-equipment-rental
```
### Install the dependencies (in a virtual envirionment of course)
```(bash)
pip3 install -r requirements.txt
```
### Setting Up the database
If you have MySQL installed, you can just uncomment this line in `.flaskenv` with your credentials.
```
# DATABASE_URL=mysql+pymysql://<db-name>:<db-password>@localhost/<table-name>
```
Otherwise you will be using sqlite.

Then run the migrations
```(bash)
flask db init
flask db migrate -m "Initial migrations"
flask db upgrade
```

### Run the app
```
flask run
```
## Mock Payments API
I created a mock API (PesaPay) for payments (an older project), so you need to install that too to have payments functionality. Not a part of the project though.
```(bash)
git clone https://github.com/alemiherbert/pesa-pay.git
```
### Install its dependencies
```(bash)
pip3 install -r requirements.txt
```
### Run the app
```
python3 app.py
```
Lets add some equipment, then you are good to go!
## Seeding the database.
Open the flask shell (another terminal)
```(bash)
flask shell
```
Run seedquip.py inside the python shell
```(python)
equip = open('seedequip.py').read()
exec(equip)
```
This also creates a default admin user for your testing, with email as `admin@example.com` and password as `password885`
## App routes and API Endpoints
```
Endpoint                    Methods  Rule
--------------------------  -------  ----------------------------------------
api.create_booking          POST     /api/bookings
api.create_equipment        POST     /api/equipment
api.create_location         POST     /api/locations
api.create_payment          POST     /api/payments
api.delete_booking          DELETE   /api/bookings/<int:booking_id>
api.delete_equipment        DELETE   /api/equipment/<int:equipment_id>
api.delete_location         DELETE   /api/locations/<int:location_id>
api.delete_payment          DELETE   /api/payments/<int:payment_id>
api.get_booking             GET      /api/bookings/<int:booking_id>
api.get_booking_list        GET      /api/bookings
api.get_equipment           GET      /api/equipment/<int:equipment_id>
api.get_equipment_list      GET      /api/equipment
api.get_featured_equipment  GET      /api/equipment/featured
api.get_location            GET      /api/locations/<int:location_id>
api.get_location_list       GET      /api/locations
api.get_payment             GET      /api/payments/<int:payment_id>
api.get_payment_list        GET      /api/payments
api.get_self                GET      /api/users/me
api.get_user                GET      /api/users/<int:user_id>
api.get_users               GET      /api/users
api.login                   POST     /api/login
api.logout                  DELETE   /api/logout
api.register                POST     /api/register
api.update_booking          PUT      /api/bookings/<int:booking_id>
api.update_equipment        PUT      /api/equipment/<int:equipment_id>
api.update_location         PUT      /api/locations/<int:location_id>
api.update_payment          PUT      /api/payments/<int:payment_id>
api.update_user             PUT      /api/users/<int:user_id>

static                      GET      /static/<path:filename>
uploaded_file               GET      /uploads/<filename>
```

## Tech Stack Used
- Flask (With SQLAlchemy ORM, and flask-jwt-extended for authenntification)
- Gunicorn as application server
- MySQL
- NGINX as a reverse proxy

## Featured Equipment
`Equipment` implements a simple scoring algorithm that weighs multiple criteria to decide wether an equipment should be featured on the featured section of the website.

Here are the weights
1. Rental Frequency: 25% - Based on last 90 days rentals
2. Availability Status: 45% - Based on current status
3. Recent Additions: 10% - Added within last 30 days
4. Profitability: 20% - Normalized price per day




