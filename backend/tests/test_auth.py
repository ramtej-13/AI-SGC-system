import pytest

def test_student_login_success(client):
    response = client.post("/api/auth/login", json={
        "email": "student1@test.local",
        "password": "Pass@123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "student"
    assert data["email"] == "student1@test.local"

def test_admin_login_success(client):
    response = client.post("/api/auth/login", json={
        "email": "admin@test.local",
        "password": "Pass@123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "admin"
    assert data["email"] == "admin@test.local"

def test_login_failure(client):
    response = client.post("/api/auth/login", json={
        "email": "student1@test.local",
        "password": "WrongPassword"
    })
    assert response.status_code == 401

def test_get_me_authorized(client, student_auth_headers):
    response = client.get("/api/auth/me", headers=student_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "student1@test.local"
    assert data["role"] == "student"

def test_get_me_unauthorized(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401
