# Budget Tracker API

![Python](https://img.shields.io/badge/Python-3.8-blue)
![Django](https://img.shields.io/badge/Django-4.2-green)
![DRF](https://img.shields.io/badge/Django_REST_Framework-3.15-red)
![JWT](https://img.shields.io/badge/Auth-JWT-orange)

A REST API for tracking personal income and expenses. Built with Django and Django REST Framework, secured with JWT authentication.

## Features

- JWT authentication (access + refresh tokens)
- Create and manage expense/income categories
- Create and manage transactions
- Filter transactions by type and category
- Summary endpoint showing total income, expenses and balance

## Tech Stack

- Python 3.8
- Django 4.2
- Django REST Framework 3.15
- djangorestframework-simplejwt 5.3
- SQLite (development)

## Installation

```bash
git clone https://github.com/Didinga/budget-tracker-api.git
cd budget-tracker-api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/auth/token/ | Get JWT token |
| POST | /api/auth/token/refresh/ | Refresh JWT token |
| GET/POST | /api/categories/ | List / create categories |
| GET/POST | /api/transactions/ | List / create transactions |
| GET | /api/transactions/summary/ | Income, expense and balance totals |

## Authentication

All endpoints require a JWT token in the Authorization header:

```
Authorization: Bearer <access_token>
```

Get a token:

```bash
curl -X POST http://127.0.0.1:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'
```

## Example Usage

Create a category:

```bash
curl -X POST http://127.0.0.1:8000/api/categories/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "Food"}'
```

Create a transaction:

```bash
curl -X POST http://127.0.0.1:8000/api/transactions/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Groceries", "amount": "500.00", "type": "expense", "date": "2026-03-08", "category": 1}'
```

## Author

Didinga Omodi - [GitHub](https://github.com/Didinga) - [LinkedIn](https://www.linkedin.com/in/didiomodi/)
