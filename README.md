# Jenga Equipment Rental
An construction equipment rental service built in python (flask)

## Team
- Alemi Herbert <alemiherbert@gmail.com>

## Motivation
To get my hands as dirty as possible with the code. 

## Installation
### Clone the app repo
```(bash)
git clone https://github.com/alemiherbert/jenga-equipment-rental.git

cd jenga-equipment-rental
```
### Install the dependencies
```(bash)
pip3 install -r requirements.txt
```
### Run the app
```
flask run
```
## Mock Payments API
I created a mock API (PesaPay) for payments, so you need to install that too. Not a part of the project though
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
You are good to go!
## App routes and API Endpoints
```
Endpoint                    Methods  Rule
--------------------------  -------  ----------------------------------------
admin.add_equipment         GET      /admin/equipment/add
admin.dashboard             GET      /admin/dashboard
admin.edit_equipment        GET      /admin/equipment/edit/<int:equipment_id>
admin.get_Users_list        GET      /admin/users
admin.get_bookings_list     GET      /admin/bookings
admin.get_equipment_list    GET      /admin/equipment
admin.get_payments_list     GET      /admin/payments
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
main.cart                   GET      /cart
main.checkout               GET      /checkout
main.get_equipment          GET      /equipment/<int:equipment_id>
main.get_equipment_list     GET      /equipment/all
main.get_equipment_list     GET      /equipment
main.index                  GET      /
main.reset_password         GET      /password-reset
main.signin                 GET      /signin
main.signup                 GET      /signup
static                      GET      /static/<path:filename>
uploaded_file               GET      /uploads/<filename>
```

## Tech Stack Used
- Flask (With SQLAlchemy ORM, and flask-jwt-extended for authenntification)
- SpruceCSS, AlpineJS bundled with webpack for the frontend

## Featured Equipment
`Equipment` implements a simple scoring algorithm that weighs multiple criteria to decide wether an equipment should be featured on the featured section of the website.

Here are the weights
1. Rental Frequency: 25% - Based on last 90 days rentals
2. Availability Status: 45% - Based on current status
3. Recent Additions: 10% - Added within last 30 days
4. Profitability: 20% - Normalized price per day

## Image Credits
1. Hero Section Photo <br>
Photo by <a href="https://unsplash.com/@jasonjarr?utm_content=creditCopyText&utm_medium=referral&utm_source=unsplash">Jason Jarrach</a> on <a href="https://unsplash.com/photos/orange-and-black-heavy-equipment-on-brown-sand-7deCnQFcrUw?utm_content=creditCopyText&utm_medium=referral&utm_source=unsplash">Unsplash</a>
      