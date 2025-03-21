# Inventory Management System API

## Overview

This project is a backend API for a simple Inventory Management System built using Django Rest Framework (DRF). It supports CRUD operations on inventory items, integrates JWT-based authentication for secure access, and utilizes SQLite for the database and Redis for caching.

## Features

- **CRUD Operations**: Create, read, update, and delete inventory items.
- **JWT Authentication**: Secure all endpoints using JWT for user authentication.
- **Redis Caching**: Cache frequently accessed items to improve performance.
- **Celery**: Use Celery for sending verification emails in the background.
- **Logging**: Integrated logging system for monitoring and debugging.
- **Unit Tests**: Comprehensive unit tests to ensure functionality.

## Technologies Used

- **Django**: Version 5.1.1
- **Django Rest Framework**: Version 3.15.2
- **SQLite**: Database
- **Redis**: Caching
- **Celery**: For background task management
- **JWT**: Authentication

## Installation

### Prerequisites

- Python 3.8+
- Redis
- Celery
- Virtualenv (optional, for isolated environment)

1. **Clone the Repository**:
   git clone <repository_url>
   cd inventory-management-system
   
2. Create a Virtual Environment (optional):
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   
3. Install Dependencies:
   pip install -r requirements.txt

4. Run Database Migrations:
   python manage.py makemigrations
   python manage.py migrate
   
5. Create a Superuser (optional for admin access):
   python manage.py createsuperuser

6. Start the Celery Worker in a separate terminal:
    celery -A ims.celery worker --pool=solo -l info  (windows)

7.Run the Development Server:
  python manage.py runserver   (The API will be available at http://127.0.0.1:8000.)


   
   





