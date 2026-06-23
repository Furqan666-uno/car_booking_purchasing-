# Car Rental/Purchase API

A backend API for a car rental and selling marketplace built with Django REST Framework.
This project allows users to register as customers or sellers, list vehicles for rent or sale, book rental cars, purchase vehicles, make payments, exchange real-time messages, and manage transactions through a role-based system.

---

## Features

### Authentication & Authorization

* JWT Authentication
* User Registration & Login
* Password Change
* Forgot/Reset Password
* Role-Based Access 

User Roles:

* Customer
* Seller
* Staff
* Admin

---

## Vehicle Management

### Car Listings

Users can:

* Create car listings
* Upload/view/delete multiple car images
* Update listings
* Delete listings
* View individual cars
* View all available cars

Vehicle details include:

* Brand
* Model
* Release Year
* Fuel Type
* Transmission Type
* Seating Capacity
* Rental Price
* Selling Price

---

## Booking and Purchasing System

Customers can rent vehicles.

Features:

* Booking creation
* Rental history
* Booking cancellation
* Availability validation
* Ownership validation
* Date overlap protection

Booking statuses:

* Pending
* Confirmed
* Cancelled

Customers can purchase vehicles.

Features:

* Purchase creation
* Purchase history
* Purchase cancellation
* Automatic vehicle locking during purchase process
* Ownership validation

Purchase statuses:

* Pending
* Confirmed
* Cancelled

---

## Payment System

Supports payments for:

* Vehicle Rentals
* Vehicle Purchases

Payment methods:

* Cash
* Card
* UPI
* Net Banking

Payment statuses:

* Pending
* Confirmed
* Cancelled

---

## Real-Time Chat System

Implemented using Django Channels and WebSockets.

Features:

* One-to-one conversations
* Buyer-Seller messaging
* Online/Offline presence
* Message read receipts
* Conversation authorization
* Pagination support

Only conversation participants can access messages.

---

## Celery ( For Background Tasks )

Implemented using:

* Celery
* Redis

Background jobs include:

### Automatic Booking/Purchasing Expiration

If payment is not completed within 20 minutes:

* Booking is cancelled automatically

If payment is not completed within 20 minutes:

* Purchase is cancelled automatically
* Vehicle becomes available again

---

## Admin Panel

Customized Django Admin Interface.

Includes management of:

* Users
* Cars
* Car Images
* Bookings
* Purchases
* Payments
* Conversations
* Messages

Features:

* Filters
* Search
* Pagination
* Read-only fields
* Organized fieldsets

---

## Security Features

* JWT Authentication
* Role-Based Permissions
* Ownership Validation
* Transaction Atomicity
* Database Row Locking
* Protected Chat Conversations

---

## Tech Stack

### Backend

* Python
* Django REST Framework

### Database

* PostgreSQL

### Authentication

* JWT (SimpleJWT)

### Real-Time Communication

* Django Channels
* WebSockets

### Background Task

* Celery

### Message Broker

* Redis

### Documentation

* Swagger ( drf-spectacular )

---

## Installation 

### Clone Repository

git clone https://github.com/Furqan666-uno/car_booking_purchasing-.git

cd project

### Create Virtual Environment

python -m venv venv-name

cd venv/Sripts/activate

### Install Dependencies

pip install -r requirements.txt

### Environment Variables

create .env ( using .env.example)

### Make/Run Migrations

python manage.py makemigrations

python manage.py migrate

### Create Superuser

python manage.py createsuperuser

### Start Server

daphne -b 0.0.0.0 -p 8000 backend.asgi:application

### Start Redis

redis-server

### Start Celery Worker

celery -A backend worker --pool=solo -l info ( For Windows)

celery -A backend worker -l info ( For Linux)

---

## Docker Setup

This project is containerized using Docker and Docker-Compose and runs with separate containers for:

- Django ASGI application (Daphne)
- PostgreSQL database
- Redis server
- Celery worker


### Services

| Service | Purpose |
|---------|---------|
| django_app | to run Django backend using Daphne ASGI server |
| postgres_db | to store application data |
| redis_cont | to message broker for Celery and Django Channels |
| celery | to handle background tasks |


### Running with Docker

Clone repository:

git clone https://github.com/Furqan666-uno/car_booking_purchasing-.git

Go inside project:

cd backend

Build and start containers:

docker compose up --build

To stop containers:

docker compose down

---

## Deployment (Live Demo)

This project is containerized using Docker and deployed on Railway.

Backend API:
https://django-app-production-8021.up.railway.app

API Documentation:
https://django-app-production-8021.up.railway.app/api/docs/

OpenAPI Schema:
https://django-app-production-8021.up.railway.app/api/schema/

Admin Panel:
https://django-app-production-8021.up.railway.app/admin/


## Deployment Architecture

The application uses separate services:

- Django ASGI application (Daphne)
- PostgreSQL database
- Redis server
- Celery worker

## Environment Variables

The application uses environment variables for sensitive configuration.

SECRET_KEY=
DEBUG=
DATABASE_URL=
REDIS_URL=
EMAIL_HOST=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=

## Screenshots

### Swagger API Documentation:

![Swagger](<screenshots/Screenshot 2026-06-20 225621.png>)
![Swagger](<screenshots/Screenshot 2026-06-20 225645.png>)
![Swagger](<screenshots/Screenshot 2026-06-20 225711.png>)
![Swaggger](<screenshots/Screenshot 2026-06-20 225754.png>)

### Admin Panel:

![Admin](<screenshots/Screenshot 2026-06-23 143506.png>)

### Features: 

![Features](<screenshots/Screenshot 2026-06-23 142903.png>) 
![Features](<screenshots/Screenshot 2026-06-23 142828.png>)

### Deployment Architecture:

![Deployed](<screenshots/Screenshot 2026-06-22 214806.png>)

---

## Notes:

* This is a demo deployment. The server may sleep or restart during inactivity.
* The password-reset functionality is disabled in the deployed demo environment to prevent misuse of the service and unnecessary email requests.

---
