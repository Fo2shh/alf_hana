# Alfhana Kitchen - Kitchen Management System

Complete internal management system for "Alfhana" Eastern meals kitchen - designed for cashiers, admins, and delivery drivers.

## Features

### 1. Main Dashboard
- Create new orders easily
- Select customer from list or add new customer
- Select multiple menu items
- View orders from last 24 hours
- Highlight delivered orders with different color

### 2. Menu Management
- Display Eastern menu in organized table
- Add, edit, and delete items (admin only)
- Categorize items by sections

### 3. Customer Management
- Add, edit, and delete customers (admin only)
- Store GPS coordinates
- Auto-generate QR Code for each customer
- Direct link to Google Maps

### 4. Driver Tracking
- Mobile app for delivery drivers
- Track driver location every 2 minutes
- Save locations in case of connection loss
- Live map for admin to monitor drivers
- Draw driver route

### 5. Thermal Printing
- Custom print template for 80mm thermal printers
- Auto-print when opening invoice page
- Display customer QR Code on invoice

## Technologies Used

- **Backend:** Python Django 5.1
- **Database:** SQLite
- **Frontend:** HTML5, CSS3, Bootstrap 5 RTL
- **Maps:** Leaflet.js + OpenStreetMap
- **QR Code:** qrcode library
- **Search:** Select2.js

## Installation and Running

### Requirements
- Python 3.8+
- pip

### Quick Start (One-Click)

Double-click `start.bat` to:
- Create Virtual Environment if not exists
- Install required packages
- Create migrations
- Apply migrations to database
- Collect static files
- Create users
- Add seed data
- Start server automatically

### Manual Installation Steps

1. Install required packages:
```bash
pip install django qrcode[pil]
```

2. Create Virtual Environment:
```bash
python -m venv venv
venv\Scripts\activate  # on Windows
source venv/bin/activate  # on Linux/Mac
```

3. Install packages in virtual environment:
```bash
pip install -r requirements.txt
```

4. Create migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Create users:
```bash
python create_admin.py
```

6. Start server:
```bash
python manage.py runserver
```

## Login Credentials

### Admin User
- **Username:** admin
- **Password:** admin123
- **Permissions:** Full (menu, customers, drivers, orders management)

### Kitchen User
- **Username:** kitchen
- **Password:** kitchen123
- **Permissions:** Orders and menu management only

### Driver User
- **Username:** driver1
- **Password:** driver123
- **Permissions:** Driver app only

## Project Structure

```
alfhana_kitchen/
├── alfhana_kitchen/          # Main project settings
├── core/                     # Core app
│   ├── models.py            # Database models
│   ├── views.py             # Main functions
│   ├── urls.py              # Routes
│   └── templates/core/      # Templates
├── orders/                   # Orders app
│   ├── views.py             # Order functions
│   ├── urls.py              # Order routes
│   └── templates/orders/    # Order templates
├── media/                    # Uploaded files (QR Codes, Images)
└── create_admin.py          # User creation script
```

## Database Models

### User
- Custom user system with roles (admin, kitchen, driver)

### Category
- Menu sections

### MenuItem
- Menu items with prices

### Customer
- Customer data with coordinates and QR Code

### Order
- Orders with daily serial number

### OrderItem
- Items in each order

### DriverLocation
- Driver locations for tracking

### Trip
- Driver trips

## Endpoints

### / - Main Dashboard
### /menu/ - Menu Management
### /customers/ - Customer Management
### /drivers/map/ - Driver Map
### /driver-app/ - Driver App
### /orders/create/ - Create New Order
### /orders/<id>/ - Order Details
### /orders/<id>/print/ - Print Invoice

## Important Notes

1. Request location permission in driver app
2. Map uses OpenStreetMap (free)
3. QR Code is auto-generated when adding customer coordinates
4. Order serial number resets daily
5. Thermal printing designed for 80mm printers

## Future Development

- Add notification system
- Support electronic payment methods
- Native mobile app for drivers
- Advanced reports and statistics
- Multi-language support

## Support

For support and inquiries, please contact the development team.
