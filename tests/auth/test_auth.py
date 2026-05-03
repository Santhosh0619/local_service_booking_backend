def test_register_user_success(client):
    response = client.post(
        "/auth/register",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "securepassword123",
            "role": "customer",
            "address": "123 Test St",
            "pincode": "12345"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "password" not in data # Ensure password isn't leaked!

def test_register_duplicate_email(client):
    payload = {
        "name": "Duplicate User",
        "email": "duplicate@example.com",
        "password": "securepassword123",
        "role": "customer",
        "address": "123 Test St",
        "pincode": "12345"
    }
    # Register first time
    client.post("/auth/register", json=payload)
    
    # Try to register second time with same email
    response = client.post("/auth/register", json=payload)
    
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

def test_login_success(client):
    # Ensure user exists
    client.post(
        "/auth/register",
        json={
            "name": "Login User",
            "email": "login@example.com",
            "password": "securepassword123",
            "role": "customer",
            "address": "123 Test St",
            "pincode": "12345"
        }
    )
    
    response = client.post(
        "/auth/login",
        json={
            "email": "login@example.com",
            "password": "securepassword123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client):
    response = client.post(
        "/auth/login",
        json={
            "email": "login@example.com", # Existing from previous test
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"
