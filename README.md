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

git clone <repository-url>

cd project

### Create Virtual Environment

python -m venv venv-name

cd venv/Sripts/activate

### Install Dependencies

pip install -r requirements.txt

### Environment Variables

Create .env using given .env.example

### Make/Run Migrations

python manage.py makemigrations

python manage.py migrate

### Create Superuser

python manage.py createsuperuser

### Start Server

python manage.py runserver

### Start Redis

redis-server

### Start Celery Worker

celery -A backend worker --pool=solo -l info ( For Windows)

celery -A backend worker -l info ( For Linux)

---

## API Documentation

Swagger UI:

/api/docs/

OpenAPI Schema:

/api/schema/

---

## Learning Outcomes

This project can helped gain experience with:

* REST API Design
* JWT Authentication
* PostgreSQL
* Django ORM
* WebSockets
* Redis
* Celery
* Role-Based Access Control
* Transaction Management
* Background Processing
* Real-Time Communication
* API Documentation
