# BloodLink :blood_donor:
Web-Based Blood Donor Management and Emergency Notification System
for St. Francis Hospital Nsambya, Kampala, Uganda.

Built by: Ainebye Martin
Institution: Cavendish University Uganda
Year: 2026

## Tech Stack
- Python 3.11 / Django 4.2
- MySQL
- Bootstrap 5
- Africa's Talking SMS API

## Setup Instructions
1. Clone the repo
2. Create virtual environment: python -m venv venv
3. Activate: venv\Scripts\activate (Windows) or source venv/bin/activate (Linux)
4. Install dependencies: pip install -r requirements.txt
5. Create .env file with your credentials (see .env.example)
6. Run migrations: python manage.py migrate
7. Create superuser: python manage.py createsuperuser
8. Run server: python manage.py runserver
