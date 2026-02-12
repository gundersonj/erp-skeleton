# Architecture

This document explains how the ERP skeleton is designed today, why those choices were made, and how to evolve it into a production-grade system.

## 1. System Goals

Primary goals:

- Deliver a clean ERP CRUD foundation for `customers`, `products`, `orders`, and `order-items`
- Expose both server-rendered UI and REST API over the same domain model
- Keep the codebase simple enough for rapid iteration while preserving data integrity

Non-goals (current stage):

- High-throughput distributed processing
- Multi-tenant isolation
- Asynchronous integration/event workflows

## 2. Architectural Style

Current style is a modular monolith using Django + Django REST Framework.

- Single deployable unit
- Shared relational database
- Feature modules by bounded area (`customers`, `products`, `orders`)
- Two delivery channels:
  - HTML web views for back-office workflows
  - JSON REST API for programmatic access

Rationale:

- Maximizes delivery speed for early product phases
- Keeps cross-entity transactions straightforward
- Reduces operational complexity compared with microservices

## 3. High-Level Context

Actors and entry points:

- Back-office user -> Django template views (`/customers/`, `/products/`, `/orders/`)
- API client -> DRF endpoints (`/api/customers/`, `/api/products/`, `/api/orders/`, `/api/order-items/`)
- Admin user -> Django admin (`/admin/`)

All entry points execute in one Django process and persist to one relational database (SQLite in current dev config).

## 4. Logical Components

### 4.1 Routing Layer

- `config/urls.py` composes application routes
- Web routes are delegated per module (`*.web_urls`)
- API routes are mounted at `/api/` via `config/api_urls.py` and DRF router

Design value:

- Clear separation of channel concerns (web vs API)
- Predictable URL ownership by module

### 4.2 Domain Modules

Each business area owns its model, forms, serializers, and views.

- `customers`: customer master data
- `products`: product catalog and pricing
- `orders`: order header + line items

Design value:

- Localized change scope
- Easier future extraction into independent services if needed

### 4.3 Presentation Layer (Web)

- Class-based generic views for CRUD workflows
- Order detail page uses inline formset for line-item editing in one screen
- Server-rendered templates keep frontend complexity low

Tradeoff:

- Fast to build, lower JS complexity
- Less dynamic UX than SPA architecture

### 4.4 API Layer

- DRF `ModelViewSet` per resource
- Uniform CRUD semantics and serializer-driven contracts
- Order responses embed read-only nested `items` for convenient reads

Tradeoff:

- Rapid API delivery
- Limited command-specific workflows (for example, place/cancel transitions are currently plain updates)

### 4.5 Persistence Layer

- Relational schema with explicit foreign-key behaviors
- Integrity rules implemented primarily in DB constraints and Django model semantics

Key integrity decisions:

- `Customer -> Order` uses `PROTECT`
- `Product -> OrderItem` uses `PROTECT`
- `Order -> OrderItem` uses `CASCADE`
- `OrderItem(order, product)` unique pair prevents duplicate line rows

## 5. Core Runtime Flows

### 5.1 Create Order (Web)

1. User creates order header (`customer`, `status`) from `/orders/new/`
2. User is redirected to order detail page
3. User adds/edits line items via inline formset
4. If `unit_price` is blank, form logic defaults it from `product.price`
5. On save, formset writes `OrderItem` rows under one order

Why this flow matters:

- Separates order identity creation from item editing
- Supports incremental editing while preserving referential integrity

### 5.2 Create Order (API)

1. Client `POST /api/orders/` with header fields
2. Client `POST /api/order-items/` for each line
3. Client reads `GET /api/orders/{id}/` to retrieve order with nested `items`

Tradeoff:

- Simple resource model
- Multi-step client orchestration instead of one transactional command endpoint

## 6. Consistency and Data Integrity Model

The current system follows strong consistency within a single database transaction boundary per request.

- Synchronous writes through Django ORM
- Immediate read-after-write consistency for same DB
- Hard referential integrity enforced at schema level

Known implications:

- Deleting referenced customer/product fails fast (expected behavior)
- Order deletion is destructive for line items by design (cascade)

## 7. Security and Access Control

Current controls:

- Django middleware stack with CSRF protection for web forms
- DRF permissions: `DjangoModelPermissionsOrAnonReadOnly`
  - Anonymous: read-only API access
  - Authenticated: write access requires model permissions

Gaps to close before production:

- Define explicit authentication strategy for API clients (session, token, JWT, etc.)
- Restrict anonymous reads if business data is sensitive
- Move secrets and environment-specific values out of source

## 8. Performance Characteristics

Current performance profile is suitable for low-to-moderate internal usage.

Strengths:

- Simple query patterns
- Pagination enabled on web list views (`paginate_by = 25`)
- Minimal network round-trips for server-rendered pages

Current bottlenecks at scale:

- SQLite write contention under concurrency
- Potential N+1 query risks on relational displays without `select_related/prefetch_related`
- No API pagination policy configured

## 9. Operational Architecture

Current environment assumptions:

- Single Django process
- Local SQLite database
- No background workers
- No cache tier

Production target baseline (recommended):

- PostgreSQL as primary database
- Gunicorn/Uvicorn workers behind reverse proxy
- Redis for cache/session/queue foundation
- Centralized logging + metrics + health checks

## 10. Evolution Roadmap

### Phase 1: Hardening the Monolith

- Add service-layer use cases for order lifecycle actions (`place`, `ship`, `cancel`)
- Enforce state transition rules in one domain policy location
- Introduce API pagination/filtering/search
- Add structured audit fields/events for critical mutations

### Phase 2: Reliability and Scale

- Migrate SQLite -> PostgreSQL
- Add optimistic or pessimistic locking where concurrent edits matter
- Introduce async jobs for non-critical side effects (notifications, exports)
- Add read-model optimizations for reporting queries

### Phase 3: Modular Decomposition (only if needed)

- Keep modules as bounded contexts inside monolith until clear scaling/team boundaries exist
- Extract highest-volatility or highest-throughput domain first (often orders)
- Use an event contract to decouple integrations before service split

## 11. Design Tradeoff Summary

- Chosen: modular monolith
  - Why: fastest path to coherent domain behavior
  - Cost: limited independent scaling of subdomains
- Chosen: server-rendered UI + REST API
  - Why: supports internal workflows and integration needs simultaneously
  - Cost: two interface surfaces to maintain
- Chosen: strict FK constraints
  - Why: protects business data correctness
  - Cost: destructive operations require explicit handling and user feedback

## 12. Architecture Fitness Criteria

Use these checks to keep architecture quality high as features are added:

- Every new write workflow has explicit invariant checks
- State transitions are modeled as domain actions, not arbitrary field updates
- Query-heavy screens avoid uncontrolled N+1 patterns
- Public API behavior is versioned or backward-compatible
- Permission model is tested at endpoint level
- Operational visibility (logs, metrics, traces) exists for critical flows
