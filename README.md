# ERP Skeleton

A Django-based ERP starter project with both server-rendered UI and REST API support for core business entities:

- Customers
- Products
- Orders
- Order Items

This repository is intentionally structured as a modular monolith so it is easy to extend while keeping strong relational integrity.

## Highlights

- Django 5.2 + Django REST Framework
- Dual interface model:
  - Web UI for back-office workflows
  - REST API for integrations/automation
- Referential integrity safeguards:
  - Customer delete protected when orders exist
  - Product delete protected when used in order items
  - Order delete cascades to order items
- Test coverage for web flows, API CRUD, totals, and delete behavior

## Tech Stack

- Python `>=3.14`
- Django `>=5.2,<6.0`
- Django REST Framework `>=3.16.1`
- django-filter `>=25.2`
- markdown `>=3.10.2`
- SQLite (default local DB)

## Project Structure

```text
config/        Django project config (settings, root urls, API router)
customers/     Customer domain (model, forms, web views, API serializer/viewset, tests)
products/      Product domain (model, forms, web views, API serializer/viewset, tests)
orders/        Order + OrderItem domain (model, forms, web views, API serializer/viewset, tests)
templates/     Server-rendered HTML templates
docs/          System documentation (SCHEMA, API, ARCHITECTURE)
```

## Quick Start

### Option A: Using `uv` (recommended)

```bash
uv sync
uv run python manage.py migrate
uv run python manage.py runserver
```

### Option B: Using `venv` + `pip`

```bash
python -m venv .venv
. .venv/Scripts/activate  # Windows PowerShell: .\.venv\Scripts\Activate.ps1
pip install -e .
python manage.py migrate
python manage.py runserver
```

App will be available at `http://127.0.0.1:8000/`.

## Running Tests

```bash
python manage.py test
```

or with `uv`:

```bash
uv run python manage.py test
```

## Web Routes

- `/customers/` - customer list/create/update/delete
- `/products/` - product list/create/update/delete
- `/orders/` - order list/create/detail/delete
- `/products/<id>/price/` - JSON helper endpoint for product price
- `/admin/` - Django admin

## API Routes

Base path: `/api/`

- `/api/customers/`
- `/api/products/`
- `/api/orders/`
- `/api/order-items/`

Each endpoint supports standard DRF ModelViewSet operations:

- `GET` list/retrieve
- `POST` create
- `PUT/PATCH` update
- `DELETE` delete

Permission model is currently `DjangoModelPermissionsOrAnonReadOnly`.

## Documentation

- Schema: `docs/SCHEMA.md`
- API contract: `docs/API.md`
- Architecture/design: `docs/ARCHITECTURE.md`

## Notes for Production Hardening

Before production use, prioritize:

- Move from SQLite to PostgreSQL
- Set secure `SECRET_KEY`, `DEBUG=False`, and proper `ALLOWED_HOSTS`
- Add explicit API authentication strategy
- Add observability (structured logs, metrics, tracing)
- Add pagination/filtering policy for API list endpoints
