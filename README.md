# Local Service Booking Backend

A robust, high-performance REST API built with **FastAPI** to connect customers with local service providers (Plumbers, Electricians, etc.). This project features a secure, role-based workflow for booking, claiming, and completing home services.

## 🚀 Key Features

- **JWT Authentication:** Secure token-based authentication using `PyJWT` and `OAuth2PasswordBearer`.
- **Role-Based Access Control (RBAC):** Distinct permissions and flows for **Customers** and **Service Providers**.
- **Service Booking Lifecycle:**
  - Customers can create service requests with titles and UTC timestamps.
  - Providers can view available jobs filtered specifically by their skills (e.g., a Plumber only sees plumbing jobs).
  - Providers can "Accept" a job, claiming ownership.
  - Customers can mark jobs as "Completed" and provide final remarks.
- **Domain-Driven Design:** Organized by features (Auth, Users, Bookings) for maximum scalability and maintainability.
- **Automated Testing:** 100% coverage of core business logic using `pytest` and an ephemeral SQLite database.
- **Dockerized Environment:** Fully containerized setup with MySQL and FastAPI for "one-command" development.

---

## 🛠️ Tech Stack

- **Framework:** [FastAPI](https://fastapi.tiangolo.com/)
- **Database:** MySQL (Production) / SQLite (Testing)
- **ORM:** [SQLAlchemy 2.0](https://www.sqlalchemy.org/)
- **Validation:** [Pydantic V2](https://docs.pydantic.dev/)
- **Security:** Bcrypt (Hashing), PyJWT (Tokens)
- **Containerization:** Docker & Docker Compose

---

## 📂 Project Structure

```text
├── app/
│   ├── core/           # Security, JWT, and Dependencies
│   ├── db/             # Session management and Base models
│   ├── features/       # Domain-specific logic
│   │   ├── auth/       # Login and Token generation
│   │   ├── users/      # User models and registration
│   │   └── bookings/   # Booking lifecycle and filtering
│   └── config.py       # Pydantic Settings (Env Vars)
├── tests/              # Full Test Suite
├── main.py             # App entry point & Router wiring
├── Dockerfile          # Container definition
└── docker-compose.yml  # Multi-container orchestration
```

---

## 🚦 Getting Started

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.

### Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Santhosh0619/local_service_booking_backend.git
   cd local_service_booking_backend
   ```

2. **Spin up the environment:**
   ```bash
   docker-compose up -d --build
   ```
   This command starts the MySQL database and the FastAPI web server.

3. **Access the API Documentation:**
   Open your browser and go to:
   - **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
   - **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🧪 Running Tests

The project uses `pytest` with a dedicated `conftest.py` that mocks the database. To run tests inside the Docker container:

```bash
docker-compose exec web python -m pytest
```

---

## 🔒 Security

All Booking endpoints are protected. To test them in Swagger:
1. Register a user at `/auth/register`.
2. Login at `/auth/login` to receive an `access_token`.
3. Click the **"Authorize"** padlock button at the top of the Swagger page.
4. Enter the token in the format: `Bearer YOUR_TOKEN_HERE`.

---

## 📝 License
This project is open-source and available under the [MIT License](LICENSE).
