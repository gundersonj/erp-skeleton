# API

This document describes the REST API exposed by this project.

## Base URL

- Base path: `/api/`
- Router: Django REST Framework `DefaultRouter`
- Endpoint style: trailing slash required (for example, `/api/customers/`)

## Auth and Permissions

Current DRF setting:

- `DEFAULT_PERMISSION_CLASSES = DjangoModelPermissionsOrAnonReadOnly`

Behavior:

- Anonymous users: read-only (`GET`, `HEAD`, `OPTIONS`)
- Authenticated users: write operations allowed only if the user has the matching Django model permissions

## Content Type

- Request: `application/json`
- Response: `application/json`

## Error Format

Typical validation error response:

```json
{
  "field_name": ["error message"]
}
```

Typical non-field or object-level error:

```json
{
  "non_field_errors": ["error message"]
}
```

---

## Customers

Resource path:

- Collection: `/api/customers/`
- Item: `/api/customers/{id}/`

### Fields

- `id` (read-only, integer)
- `name` (string, required, max 255)
- `email` (string, optional, nullable, unique)
- `phone` (string, optional, max 50)
- `notes` (string, optional)
- `created_at` (read-only, datetime)
- `updated_at` (read-only, datetime)

### Methods

- `GET /api/customers/` list customers
- `POST /api/customers/` create customer
- `GET /api/customers/{id}/` retrieve customer
- `PUT /api/customers/{id}/` replace customer
- `PATCH /api/customers/{id}/` partial update customer
- `DELETE /api/customers/{id}/` delete customer

### Example Create

Request:

```json
{
  "name": "Acme Corp",
  "email": "ops@acme.example",
  "phone": "555-0100",
  "notes": "Priority account"
}
```

Response (`201`):

```json
{
  "id": 1,
  "name": "Acme Corp",
  "email": "ops@acme.example",
  "phone": "555-0100",
  "notes": "Priority account",
  "created_at": "2026-02-12T18:00:00Z",
  "updated_at": "2026-02-12T18:00:00Z"
}
```

---

## Products

Resource path:

- Collection: `/api/products/`
- Item: `/api/products/{id}/`

### Fields

- `id` (read-only, integer)
- `sku` (string, required, unique, max 64)
- `name` (string, required, max 255)
- `price` (decimal with 2 places, default `0.00`)
- `is_active` (boolean, default `true`)
- `created_at` (read-only, datetime)
- `updated_at` (read-only, datetime)

Note: DRF serializes decimal values as JSON strings by default (for example, `"19.99"`).

### Methods

- `GET /api/products/`
- `POST /api/products/`
- `GET /api/products/{id}/`
- `PUT /api/products/{id}/`
- `PATCH /api/products/{id}/`
- `DELETE /api/products/{id}/`

### Example Create

Request:

```json
{
  "sku": "SKU-1001",
  "name": "Widget",
  "price": "19.99",
  "is_active": true
}
```

Response (`201`):

```json
{
  "id": 1,
  "sku": "SKU-1001",
  "name": "Widget",
  "price": "19.99",
  "is_active": true,
  "created_at": "2026-02-12T18:00:00Z",
  "updated_at": "2026-02-12T18:00:00Z"
}
```

---

## Orders

Resource path:

- Collection: `/api/orders/`
- Item: `/api/orders/{id}/`

### Fields

- `id` (read-only, integer)
- `customer` (integer, required, FK to `customers_customer.id`)
- `status` (string, required, choices: `DRAFT`, `PLACED`, `SHIPPED`, `CANCELLED`, default `DRAFT`)
- `order_date` (read-only, date, auto-set on create)
- `created_at` (read-only, datetime)
- `updated_at` (read-only, datetime)
- `items` (read-only array of nested order items)

Important: `items` is included in response, but cannot be written through the order endpoint.

### Methods

- `GET /api/orders/`
- `POST /api/orders/`
- `GET /api/orders/{id}/`
- `PUT /api/orders/{id}/`
- `PATCH /api/orders/{id}/`
- `DELETE /api/orders/{id}/`

### Example Create

Request:

```json
{
  "customer": 1,
  "status": "DRAFT"
}
```

Response (`201`):

```json
{
  "id": 1,
  "customer": 1,
  "status": "DRAFT",
  "order_date": "2026-02-12",
  "created_at": "2026-02-12T18:00:00Z",
  "updated_at": "2026-02-12T18:00:00Z",
  "items": []
}
```

### Example Retrieve With Items

```json
{
  "id": 1,
  "customer": 1,
  "status": "PLACED",
  "order_date": "2026-02-12",
  "created_at": "2026-02-12T18:00:00Z",
  "updated_at": "2026-02-12T18:10:00Z",
  "items": [
    {
      "id": 10,
      "order": 1,
      "product": 2,
      "quantity": 3,
      "unit_price": "19.99",
      "created_at": "2026-02-12T18:05:00Z",
      "updated_at": "2026-02-12T18:05:00Z"
    }
  ]
}
```

---

## Order Items

Resource path:

- Collection: `/api/order-items/`
- Item: `/api/order-items/{id}/`

### Fields

- `id` (read-only, integer)
- `order` (integer, required, FK to `orders_order.id`)
- `product` (integer, required, FK to `products_product.id`)
- `quantity` (integer, required, positive, default `1`)
- `unit_price` (decimal with 2 places, required)
- `created_at` (read-only, datetime)
- `updated_at` (read-only, datetime)

### Constraints

- Unique pair: (`order`, `product`)
  - You cannot add the same product more than once to the same order.
- `order` delete behavior: deleting an order deletes its order items (`CASCADE`).
- `product` delete behavior: product deletion is blocked if referenced (`PROTECT`).

### Methods

- `GET /api/order-items/`
- `POST /api/order-items/`
- `GET /api/order-items/{id}/`
- `PUT /api/order-items/{id}/`
- `PATCH /api/order-items/{id}/`
- `DELETE /api/order-items/{id}/`

### Example Create

Request:

```json
{
  "order": 1,
  "product": 2,
  "quantity": 3,
  "unit_price": "19.99"
}
```

Response (`201`):

```json
{
  "id": 10,
  "order": 1,
  "product": 2,
  "quantity": 3,
  "unit_price": "19.99",
  "created_at": "2026-02-12T18:05:00Z",
  "updated_at": "2026-02-12T18:05:00Z"
}
```

---

## Notes

- No custom pagination is configured in `REST_FRAMEWORK`; list endpoints currently return a plain JSON array.
- Write operations can fail with `403` unless the authenticated user has the required model permissions.
- Deleting customers with existing orders will fail due to FK `PROTECT`.
