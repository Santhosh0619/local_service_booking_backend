import pytest

users_created = False

def setup_users(client):
    """Helper function to seed the test database with a Customer, Plumber, and Electrician."""
    global users_created
    if users_created: return
    
    client.post("/auth/register", json={
        "name": "Customer", "email": "customer@example.com", "password": "password123",
        "role": "customer", "address": "123 St", "pincode": "123"
    })
    client.post("/auth/register", json={
        "name": "Plumber", "email": "plumber@example.com", "password": "password123",
        "role": "provider", "services": ["plumber"], "address": "123 St", "pincode": "123"
    })
    client.post("/auth/register", json={
        "name": "Electrician", "email": "electrician@example.com", "password": "password123",
        "role": "provider", "services": ["electrician"], "address": "123 St", "pincode": "123"
    })
    users_created = True

def get_auth_headers(client, email):
    """Helper function to log in and return the Authorization Bearer header."""
    response = client.post("/auth/login", json={"email": email, "password": "password123"})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

# --- TESTS ---

def test_auth_failure(client):
    """Ensure unauthenticated users cannot access booking endpoints."""
    response = client.post("/bookings", json={
        "title": "Sink Broken",
        "service_type": "plumber",
        "address": "123 St",
        "date": "2026-05-10T14:30:00Z"
    })
    assert response.status_code == 401 # Unauthorized

def test_customer_create_booking(client):
    """Ensure a customer can create a pending booking."""
    setup_users(client)
    headers = get_auth_headers(client, "customer@example.com")
    
    response = client.post("/bookings", json={
        "title": "Sink Broken",
        "service_type": "plumber",
        "address": "123 St",
        "date": "2026-05-10T14:30:00Z"
    }, headers=headers)
    
    assert response.status_code == 201
    assert response.json()["status"] == "pending"
    assert response.json()["service_type"] == "plumber"
    assert response.json()["title"] == "Sink Broken"

def test_provider_visibility(client):
    """Ensure a plumber sees plumber jobs, but an electrician does not."""
    plumber_headers = get_auth_headers(client, "plumber@example.com")
    elec_headers = get_auth_headers(client, "electrician@example.com")
    
    plumb_resp = client.get("/bookings/available", headers=plumber_headers)
    assert plumb_resp.status_code == 200
    assert len(plumb_resp.json()) == 1 # Sees the booking created in previous test
    
    elec_resp = client.get("/bookings/available", headers=elec_headers)
    assert elec_resp.status_code == 200
    assert len(elec_resp.json()) == 0 # Sees nothing

def test_provider_accept_booking(client):
    """Ensure a provider can accept a booking."""
    plumber_headers = get_auth_headers(client, "plumber@example.com")
    
    response = client.patch("/bookings/1/accept", headers=plumber_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "accepted"
    assert response.json()["provider_id"] is not None

def test_personal_bookings(client):
    """Ensure users can view their personal bookings."""
    cust_headers = get_auth_headers(client, "customer@example.com")
    cust_resp = client.get("/bookings/my-bookings", headers=cust_headers)
    assert len(cust_resp.json()) == 1
    
    plumb_headers = get_auth_headers(client, "plumber@example.com")
    plumb_resp = client.get("/bookings/my-bookings", headers=plumb_headers)
    assert len(plumb_resp.json()) == 1

def test_customer_complete_booking(client):
    """Ensure a customer can mark a booking as complete."""
    cust_headers = get_auth_headers(client, "customer@example.com")
    response = client.patch("/bookings/1/complete", headers=cust_headers, json={"remarks": "Great job!"})
    assert response.status_code == 200
    assert response.json()["status"] == "completed"
    assert response.json()["remarks"] == "Great job!"

def test_role_authorization(client):
    """Ensure users cannot perform actions outside their role."""
    cust_headers = get_auth_headers(client, "customer@example.com")
    plumb_headers = get_auth_headers(client, "plumber@example.com")
    
    # Customer tries to accept (Forbidden)
    assert client.patch("/bookings/1/accept", headers=cust_headers).status_code == 403
    
    # Provider tries to complete (Forbidden)
    assert client.patch("/bookings/1/complete", headers=plumb_headers, json={"remarks": "Done"}).status_code == 403
