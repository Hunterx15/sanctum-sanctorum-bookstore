# Sanctum Sanctorum — Submission Notes

## Live Deployment

https://sanctum-sanctorum-bookstore.onrender.com

## Completion Status

Completed.

All automated tests pass locally:

- 202 passed
- 2 dependency deprecation warnings

The application is publicly deployed and uses PostgreSQL in production while retaining SQLite for local development and testing.

## Architecture

The application is structured as a FastAPI backend with a layered design:

- Routers handle HTTP/API concerns.
- Services contain business logic.
- SQLAlchemy models define persistence models.
- Pydantic schemas handle request/response validation.
- Database access is centralized through SQLAlchemy sessions.

The application uses SQLite locally and PostgreSQL in production through the `SANCTUM_DATABASE_URL` environment variable.

## Implementation Highlights

Implemented/fixed functionality includes:

- Book creation, listing, searching, sorting, pagination and updates
- ISBN-13 normalization and checksum validation
- Duplicate ISBN protection
- Member creation, validation and statistics
- Order creation, payment and cancellation
- Stock management and price snapshots
- Tier-based discounts
- Restricted-book access control
- Loan creation, return, overdue detection and late-fee calculation
- Loan limits and stock handling
- Book sales reporting
- PostgreSQL production support

## Design / Tradeoffs

The existing application structure was preserved rather than introducing unnecessary architectural layers.

The service layer contains the main business rules, while routers remain relatively thin.

SQLite remains the default database so the application can run locally without an external service. PostgreSQL is selected through the environment variable for production deployment.

The production database connection configuration is conditional so SQLite-specific connection arguments are only used with SQLite.

## Specification / Ambiguities

Where the specification was not completely explicit, behavior was implemented to remain consistent with the surrounding application structure and existing tests.

No test files were modified.

## AI Usage

AI assistance was used during development for:

- Understanding the existing project structure
- Identifying implementation gaps
- Debugging failing tests
- Reviewing SQLAlchemy/FastAPI implementation approaches
- Troubleshooting deployment configuration
- Checking PostgreSQL deployment compatibility

All generated suggestions were reviewed and tested before being incorporated.

One example where AI assistance was unhelpful was the initial deployment recommendation to use `pip install .`. This failed because setuptools attempted automatic package discovery and found both `app` and `frontend` as top-level packages. The deployment was subsequently changed to use the project's existing `uv` workflow with `uv sync --frozen --no-dev`.

The final implementation was verified locally with the complete test suite and the deployed application was started successfully on Render.

## Verification

Local test command:

    uv run pytest

Result:

    202 passed, 2 warnings

Production start command:

    uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT

Production database:

    PostgreSQL via SANCTUM_DATABASE_URL

Live application:

https://sanctum-sanctorum-bookstore.onrender.com
