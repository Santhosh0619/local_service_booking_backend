# PRD 01: Authentication & User Management (Phase 1)

## 1. Goal Description
The objective of Phase 1 is to establish the core infrastructure of the local service booking application. This includes setting up secure environment variable management, establishing a robust MySQL database connection via Docker, and defining the foundational `User` entity using a modern, scalable Domain-Driven (Feature-oriented) architecture.

## 2. Architectural Decisions
We have chosen a **Domain-Driven (Feature-oriented) Architecture** over a traditional Layer-oriented architecture. 

*   **Separation of Concerns:** The application is split into self-contained "features" (e.g., `app/features/users`, `app/features/auth`). This allows massive scalability. If we later switch to a third-party login provider (like Google Auth), we can delete the `auth` feature without breaking the `users` profile management feature.
*   **Domain Ownership:** The `users` feature "owns" the database table defining a User. The `auth` feature does not own a table; it acts as a consumer that imports the User model strictly to verify credentials.

## 3. Core Infrastructure Implementation
*   **Environment Management (`app/config.py`):** Uses `pydantic-settings` to strictly enforce the presence of critical `.env` variables (`DATABASE_URL`, `SECRET_KEY`). It fails fast on startup if secrets are missing.
*   **Database Engine (`app/db/session.py`):** Utilizes SQLAlchemy's `create_engine` and `sessionmaker`.
    *   `autocommit=False` ensures transactional safety (rollbacks on failure).
    *   Implements a FastAPI Dependency (`get_db`) using Python Generators (`yield`) and `try-finally` blocks to guarantee database connections are safely closed after every HTTP request.
*   **Dockerized MySQL:** The `docker-compose.yml` spins up a `mysql:8.0` container, tunneling port `3306` to the host machine for easy Workbench access, and using a Docker Volume (`db_data`) to ensure data persists across container restarts.

## 4. The User Feature (`app/features/users/`)

### A. Database Model (`models.py`)
Defines the physical MySQL `users` table via SQLAlchemy:
*   **`id`**: Integer (Primary Key, Auto-increment, Indexed).
*   **`email`**: String(255) (Unique constraint to prevent duplicate accounts, Indexed for lightning-fast login lookups).
*   **`password`**: String(255) (Stores the hashed string, never plaintext).
*   **`role`**: SQLAlchemy Enum mapped to a Python Enum (`CUSTOMER`, `PROVIDER`).
*   **`services`**: `JSON` column. Resolves MySQL's inability to store native lists. It stores a list of Enums. The valid service values are: `plumber`, `electrician`, `carpenter`, and `maid`. It is nullable because Customers do not provide services.
*   **`phone_number` / `pincode`**: Stored as Strings to preserve formatting (like leading zeros or country code symbols like `+`).

### B. Validation Schemas (`schemas.py`)
Utilizes Pydantic to act as a strict data validator (The Bouncer) before data reaches the database or leaves the API.
*   **`UserCreate` (Input Validation):** 
    *   Enforces standard rules (`EmailStr` validation, minimum password length of 8).
    *   **Custom Business Logic:** Implements a `@field_validator` via a `@classmethod`. It intercepts the data on the assembly line and checks the `role`. If the role is `PROVIDER`, it strictly enforces that the `services` list cannot be empty. If the role is `CUSTOMER`, it rejects the request if services are provided.
*   **`UserResponse` (Output Formatting):**
    *   Used to format data sent back to the client.
    *   **Security:** Intentionally omits the `password` field from the schema to guarantee the hashed password is never leaked in an API response.
    *   `from_attributes = True` allows Pydantic to read directly from the SQLAlchemy Model object instead of requiring a standard dictionary.
