# Learning Guide: Authentication, Testing, and Docker Operations

This guide compiles the advanced concepts and Q&A discussed during the execution of Phase 2 (Authentication).

---

## 1. API Design Decisions

### JSON Body vs. OAuth2 Form Data
When building the `/auth/login` endpoint, FastAPI provides a built-in tool called `OAuth2PasswordRequestForm`. 
*   **The Problem:** This tool strictly forces the frontend to send data as `application/x-www-form-urlencoded` (Form Data). 
*   **Our Decision:** We created a custom Pydantic `LoginRequest` schema to accept standard JSON instead. Since modern frontend frameworks (React, Flutter, Vue) natively speak JSON, forcing them to use Form Data just for the login screen is a bad developer experience.

### Why `422 Unprocessable Entity`?
When a user submits a password that is too short, or an invalid email address, our API returns `422 Unprocessable Entity` instead of `400 Bad Request`.
*   **400 Bad Request:** Used when the data breaks a *business rule* (e.g., "Email already registered").
*   **422 Unprocessable Entity:** Used when the JSON is formatted correctly, but the contents fail *schema validation*.
*   **The "Big Message" Feature:** Pydantic generates a large, structured JSON array for 422 errors. This is highly intentional! It tells frontend developers exactly which field failed (`loc: ["body", "password"]`) so they can automatically highlight that specific text box in red on the screen.

### Automatic Swagger Integration
FastAPI automatically generates the Swagger UI (`/docs`) without any extra coding. It reads the Pydantic schemas, Python type hints, and `@router` decorators to build an "OpenAPI Specification" JSON document. It then hosts the Swagger webpage to display this document interactively.

---

## 2. Docker Operations

### Detached Mode (`-d`)
*   `docker-compose up` takes over your terminal window. If you close the window or hit `Ctrl+C`, the server instantly dies.
*   `docker-compose up -d` runs the server in **Detached Mode**. It boots up silently in the background and instantly gives you your terminal back so you can continue typing commands (like `pytest` or `git commit`).

### Port Conflicts (MySQL)
We encountered the error: `bind: Only one usage of each socket address is normally permitted`.
*   **Cause:** The Windows host machine already had a program (like local MySQL or XAMPP) occupying port `3306`.
*   **Solution:** We changed the `docker-compose.yml` port mapping to `3307:3306`. This tells Docker: *"Run MySQL on 3306 internally, but expose it to the host machine on 3307."* 
*   *(Note: The FastAPI container still talks to `db:3306` because it is inside the Docker network. Only external tools like MySQL Workbench need to use 3307).*

---

## 3. Testing Architecture

### Local `venv` vs. Docker Testing
You can run Pytest in two different places:
1.  **Local `venv` (`python -m pytest`)**: Extremely fast. Used 90% of the time during active development.
2.  **Inside Docker (`docker-compose exec web python -m pytest`)**: Slower, but perfectly replicates the final Linux production server. Used primarily in CI/CD pipelines before merging code.
*   *(Note: The `python -m` wrapper is crucial to ensure Python correctly identifies the root project folder).*

### Database Testing & Git
*   We use a FastAPI `dependency_override` in `conftest.py` to intercept the `get_db` request and replace the real MySQL connection with a fake, lightweight **SQLite** database (`test.db`). 
*   **Gitignore:** The `test.db` file MUST be added to `.gitignore`. Databases are large binary files; committing them causes repository bloat and massive merge conflicts. Furthermore, test databases contain fake, ephemeral data that is deleted and recreated constantly.
