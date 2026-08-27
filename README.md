# Product Showcase — API Test Automation

Portfolio project: a small FastAPI service (product catalog — list/create/update/delete,
JSON-file storage) plus a `pytest` + `requests` test suite that drives it over real HTTP.

## Structure

```
app/            FastAPI service under test
tests/          pytest + requests test suite
requirements.txt        deps to run the API
requirements-test.txt   deps to run the tests
```

## Run the API

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Swagger UI: http://127.0.0.1:8000/docs

Storage location defaults to `./data/products.json`; override with the
`PRODUCTS_DATA_DIR` env var (useful to point tests at a disposable data dir
instead of your working copy).

## Run the tests

With the API running in one terminal:

```bash
pip install -r requirements-test.txt
pytest
```

By default tests hit `http://127.0.0.1:8000`; override with `API_BASE_URL`.

The `tests/` suite (fixtures, test files) is a work in progress — being built from scratch
as a learning exercise. See the API contract and Auth sections below for what to cover.

## API contract (summary)

| Method | Path | Notes |
|---|---|---|
| POST | `/auth/login` | body: `username`, `password`; returns `{"access_token", "token_type"}` |
| GET | `/products` | public; filters: `min_price`, `max_price`; sort: `sort` (`price_asc`/`price_desc`/`name_asc`/`name_desc`); pagination: `limit` (1-100, default 20), `offset` (default 0) |
| GET | `/products/{id}` | public; 404 if not found |
| POST | `/products` | **requires auth**; body: `name`, `price` required, `description` optional; unknown fields rejected |
| PUT | `/products/{id}` | **requires auth**; full replace, all three fields required (`description` may be `null` but must be present); idempotent |
| DELETE | `/products/{id}` | **requires auth**; 204, idempotent 404 on repeat |

Product: `id` (server-generated uuid4), `name` (1-100 chars, not blank), `price` (> 0
after rounding to 2 decimals), `description` (optional, nullable).

Error body: `{"code": "...", "message": "...", "field": "..."}`.
Codes: `VALIDATION_ERROR`, `MISSING_FIELD`, `UNKNOWN_FIELD` (400), `UNAUTHORIZED`,
`INVALID_CREDENTIALS` (401), `NOT_FOUND` (404), `STORAGE_CORRUPTED` (500).

## Auth

`POST/PUT/DELETE /products` require a JWT: `Authorization: Bearer <token>`, obtained from
`POST /auth/login`. Reads (`GET`) stay public.

Seeded demo user (no database, single hardcoded account — this is a learning project):
- username: `admin`
- password: `admin123`, override with the `DEMO_USER_PASSWORD` env var (must match on both
  the API process and wherever tests read it)

Token secret defaults to a dev value; override with `JWT_SECRET_KEY`. Tokens expire after
30 minutes.
