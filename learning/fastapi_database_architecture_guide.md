# Learning Guide: Architecture, Databases, and Python Concepts

This guide compiles the advanced concepts discussed during the setup of Phase 1 (Database and Users).

---

## 1. Domain-Driven vs. Layer-Oriented Architecture
When structuring a large backend project, there are two main approaches:

*   **Layer-Oriented (Beginner):** Groups code by *what it is* technically. You have a giant `models/` folder for all tables, a giant `schemas/` folder for all validation, and a giant `routers/` folder for all URLs. (Hard to scale).
*   **Domain-Driven / Feature-Oriented (Professional):** Groups code by *what it does* for the business. You have a `features/auth/` folder and a `features/users/` folder. Everything a feature needs (its own models, schemas, and routes) lives inside its folder. If you want to delete or rewrite a feature, you only touch one folder.

### The "Chicken and Egg" of Auth vs Users
**Why separate `auth` from `users`?** 
If you decide to switch your custom password login to "Login with Google", you can completely rewrite the `auth` folder without touching the `users` profile management code.
**Domain Ownership:** The `users` feature *owns* the Database Table definition (`models.py`). The `auth` feature doesn't create tables; it simply imports the `User` model to verify passwords.

---

## 2. Deep Dive: `app/db/session.py`

This file is the lifeblood of our application. Here is what happens under the hood:

*   **`create_engine`**: The Engine is the core connection pool. It translates our Python into MySQL dialect and holds the physical network cables open to the database.
*   **`sessionmaker`**: The factory that generates individual sessions (conversations) with the database.
    *   `autocommit=False`: Ensures **Transactions**. If a function does 5 database changes but fails on the 5th, `autocommit=False` automatically rolls back the first 4 changes so data isn't corrupted. You must manually call `db.commit()` when you are completely finished.
    *   `autoflush=False`: Gives us strict manual control over when queries are sent to MySQL.

### The FastAPI Dependency (`yield` and `try-finally`)
```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```
*   **`yield db`**: Instead of `return` (which kills the function instantly), `yield` turns this into a Generator. It "pauses" this function, hands the `db` connection over to FastAPI to process a user's web request, and waits.
*   **`try...finally`**: Once FastAPI is done with the web request, this function unpauses and hits `finally: db.close()`. `finally` is an absolute guarantee. Even if the web request crashed with a massive 500 Server Error, Python is forced to run the `finally` block, ensuring the database connection is safely returned to the pool and preventing memory leaks.

---

## 3. Database Design: Strings vs Integers
*Question: Why are phone numbers and pincodes `String` instead of `Integer`?*

**Golden Rule:** If you are never going to perform mathematical operations on a value (like calculating averages), it should usually be a String.
1.  **Leading Zeros:** If a pincode is `01234`, an Integer type will save it as `1234`, breaking the pincode. Strings preserve the `0`.
2.  **Special Characters:** Phone numbers often require characters like `+` (e.g., `+1-555-1234`), which crash Integer columns.

---

## 4. Python Concepts: What is `@classmethod`?
In `schemas.py`, we used `@classmethod` for our custom Pydantic validator.

*   **Normal Method (`self`):** Requires the object to be completely built before you can call the function. (e.g., You must build the car before you can honk the horn).
*   **Class Method (`cls`):** Operates on the "blueprint" of the class, *before* the object is created. 

Pydantic needs to validate the raw incoming JSON data *before* it allows the final `UserCreate` object to be built. `@classmethod` acts like a safety inspector on the factory assembly line, checking the parts before the car is allowed to be finished.
