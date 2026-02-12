# Schema

This document describes the core database schema for the ERP skeleton.

## Overview

Core entities:

- **Customer**: who places orders
- **Product**: catalog items that can be ordered
- **Order**: header record for a purchase
- **OrderItem**: line items belonging to an order

Relationships:

- Customer 1 -> * Order
- Order 1 -> * OrderItem
- Product 1 -> * OrderItem

Deletion rules (important):

- Deleting a **Customer** is blocked if they have Orders (**PROTECT**)
- Deleting a **Product** is blocked if it appears in OrderItems (**PROTECT**)
- Deleting an **Order** deletes its OrderItems (**CASCADE**)

> Note: Primary key type is Django's configured default (`DEFAULT_AUTO_FIELD`) - typically `BigAutoField` in newer projects.

---

## Entity Relationship Diagram (logical)

```text
CUSTOMER (customers_customer)
  1 --------< ORDER (orders_order)
               1 --------< ORDER_ITEM (orders_orderitem) >-------- 1 PRODUCT (products_product)
```

---

## Tables

### customers_customer

| Column      | Type          | Constraints / Notes |
|-------------|---------------|---------------------|
| id          | PK            | AutoField/BigAutoField |
| name        | varchar(255)  | required |
| email       | email/varchar | nullable, unique (if configured unique=True) |
| phone       | varchar(50)   | blank allowed |
| notes       | text          | blank allowed |
| created_at  | datetime      | auto_now_add |
| updated_at  | datetime      | auto_now |

Indexes / Constraints:
- `email` unique (only if you set `unique=True`)

---

### products_product

| Column      | Type          | Constraints / Notes |
|-------------|---------------|---------------------|
| id          | PK            | AutoField/BigAutoField |
| sku         | varchar(64)   | required, unique |
| name        | varchar(255)  | required |
| price       | decimal(12,2) | default 0.00 |
| is_active   | boolean       | default true |
| created_at  | datetime      | auto_now_add |
| updated_at  | datetime      | auto_now |

Indexes / Constraints:
- `sku` unique

---

### orders_order

| Column      | Type          | Constraints / Notes |
|-------------|---------------|---------------------|
| id          | PK            | AutoField/BigAutoField |
| customer_id | FK            | -> customers_customer.id, on_delete=PROTECT |
| status      | varchar(20)   | choices, default `DRAFT` |
| order_date  | date          | auto_now_add |
| created_at  | datetime      | auto_now_add |
| updated_at  | datetime      | auto_now |

Status choices (current):
- `DRAFT`
- `PLACED`
- `SHIPPED`
- `CANCELLED`

Indexes / Constraints:
- Implicit FK index on `customer_id` (DB-dependent but typical)

---

### orders_orderitem

| Column      | Type          | Constraints / Notes |
|-------------|---------------|---------------------|
| id          | PK            | AutoField/BigAutoField |
| order_id    | FK            | -> orders_order.id, on_delete=CASCADE |
| product_id  | FK            | -> products_product.id, on_delete=PROTECT |
| quantity    | integer       | positive, default 1 |
| unit_price  | decimal(12,2) | required (often defaulted from product.price in forms/UI) |
| created_at  | datetime      | auto_now_add |
| updated_at  | datetime      | auto_now |

Indexes / Constraints:
- Optional uniqueness rule (depending on implementation):
  - If enabled: unique (order_id, product_id) to prevent duplicate product rows per order

---

## Derived / Computed Values (not stored)

These are computed in Python (not persisted columns):

- `OrderItem.line_total()` = `quantity * unit_price`
- `Order.subtotal()` = `SUM(items.line_total)`
- `Order.total_items()` = `SUM(items.quantity)`

---

## Data Integrity Rules

- Orders require a valid Customer.
- OrderItems require a valid Order and Product.
- Customer/Product deletions are blocked if referenced by orders/items (by FK `PROTECT`).
- Deleting an Order will remove all its OrderItems (by FK `CASCADE`).

---

## Notes / Future Enhancements

Common ERP extensions (not implemented yet):
- Soft-delete products via `is_active` rather than hard-delete
- Order header fields: `shipping`, `tax`, `discount`, `total`
- Snapshotting product details on OrderItem (sku/name) to preserve history even if product changes
- Inventory/stock tables
- Payments / invoices
