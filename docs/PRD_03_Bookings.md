# PRD 03: Bookings Feature

## 1. Architectural Overview
The Bookings feature forms the core business logic of the `local_service_booking` application. It acts as the bridge connecting Customers with Service Providers through a robust, role-based job lifecycle. This phase also introduces system-wide API protection via JWT Authentication Dependencies.

**Design Philosophy:**
We maintain strict Domain-Driven boundaries. The bookings feature is self-contained in `app/features/bookings/` and manages its own Models, Schemas, Services, and Routing. Access to these routes is strictly fenced by Role-Based Access Control (RBAC).

---

## 2. Core Implementation Components

### A. Authentication Dependency (`app/core/deps.py`)
To ensure that only registered users can interact with bookings, we implemented a global FastAPI Dependency: `get_current_user`.
*   **Behavior:** It intercepts incoming API requests, reads the `Authorization: Bearer <token>` header, and decodes the JWT using `PyJWT`.
*   **Security Enforcement:** If the token is missing, expired, or cryptographically invalid, it actively raises a `401 Unauthorized` exception. If valid, it fetches and returns the full `User` object from the database, effectively proving the identity and Role of the requester.

### B. The Bookings Domain (`app/features/bookings/`)
*   **Models (`models.py`):** 
    *   `customer_id` (Required ForeignKey): Identifies the creator of the job.
    *   `provider_id` (Nullable ForeignKey): Starts as `NULL` and is populated only when a Provider accepts the job.
    *   `title` and `remarks`: The `title` captures the customer's initial problem description, while `remarks` captures the final closing notes when a customer marks the job as completed.
    *   `date`: Explicitly enforces `DateTime(timezone=True)` to ensure global UTC consistency.
    *   `status`: An Enum that defaults to `pending`, and progresses to `accepted`, and finally `completed`.

*   **Schemas (`schemas.py`):** 
    *   `BookingCreate`: Ensures Customers provide the necessary data (`title`, `service_type`, `address`, `date`).
    *   `BookingComplete`: Ensures Customers provide closing `remarks` when finishing a job.
    *   `BookingResponse`: Formats the SQLAlchemy database object into a standardized JSON response.

### C. Role-Based Business Logic (`service.py`)
Every action in the service layer is fenced by strict `UserRole` validation to prevent unauthorized API usage:
*   **Customer Actions:** 
    *   `create_booking()`: The system automatically extracts the `customer_id` from the JWT token. This prevents users from spoofing identities or creating bookings on behalf of others.
    *   `complete_booking()`: The system requires a `BookingComplete` payload containing `remarks`. It rigorously verifies `booking.customer_id == user.id` to ensure a customer cannot maliciously complete someone else's booking.
*   **Provider Actions:** 
    *   `get_available_bookings()`: The system fetches all `pending` jobs, but strictly filters them against the Provider's `User.services` JSON array. A plumber will never see electrical jobs.
    *   `accept_booking()`: The system assigns `provider_id = user.id` and transitions the status to `accepted`.
*   **Shared Actions:** 
    *   `get_my_bookings()`: Both roles can utilize this endpoint. The service dynamically checks their `role` and returns their personal workload (jobs created by the Customer, or jobs accepted by the Provider).

---

## 3. Automated Testing Infrastructure
A comprehensive testing suite was implemented in `tests/bookings/test_bookings.py`. It utilizes a temporary SQLite database (via `conftest.py` dependency overrides) to prevent production data mutation.

The test suite successfully verifies the complete real-world lifecycle:
1.  **Auth Failure:** Verifies that missing tokens return `401 Unauthorized`.
2.  **Creation Flow:** Verifies customers can successfully create jobs containing a `title`.
3.  **Visibility Constraints:** Verifies that Electricians receive empty arrays when querying `/available` if only Plumbing jobs exist.
4.  **Acceptance Flow:** Verifies providers can successfully transition a booking to `accepted` and attach their `provider_id`.
5.  **Workload Tracking:** Verifies both customers and providers can accurately pull their personal histories via `/my-bookings`.
6.  **Completion Flow:** Verifies customers can transition a booking to `completed` while attaching closing `remarks`.
7.  **Role Authorization:** Strictly asserts that Customers receive `403 Forbidden` when attempting to "accept" jobs, and Providers receive `403 Forbidden` when attempting to "complete" jobs.
