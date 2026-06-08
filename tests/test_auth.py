import pytest
from httpx import AsyncClient
from src.auth.jwt import verify_password, get_password_hash, create_access_token, decode_access_token

def test_password_hashing():
    pwd = "secret-password"
    hashed = get_password_hash(pwd)
    assert hashed != pwd
    assert verify_password(pwd, hashed) is True
    assert verify_password("wrong-password", hashed) is False

def test_jwt_token_claims():
    data = {"sub": "alice", "role": "admin"}
    token = create_access_token(data)
    assert token is not None
    
    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "alice"
    assert decoded["role"] == "admin"

@pytest.mark.asyncio
async def test_auth_api_flow(client: AsyncClient):
    # 1. Register a test user
    reg_payload = {"username": "bob_agent", "password": "agentpassword", "role": "agent"}
    reg_res = await client.post("/auth/register", json=reg_payload)
    assert reg_res.status_code == 201
    assert reg_res.json()["username"] == "bob_agent"
    assert reg_res.json()["role"] == "agent"

    # 2. Duplicate registration check
    dup_res = await client.post("/auth/register", json=reg_payload)
    assert dup_res.status_code == 400

    # 3. Request auth token
    login_payload = {"username": "bob_agent", "password": "agentpassword"}
    login_res = await client.post("/auth/token", json=login_payload)
    assert login_res.status_code == 200
    token_data = login_res.json()
    assert "access_token" in token_data
    assert token_data["role"] == "agent"

    # 4. Access protected profile endpoint
    headers = {"Authorization": f"Bearer {token_data['access_token']}"}
    profile_res = await client.get("/auth/users/me", headers=headers)
    assert profile_res.status_code == 200
    assert profile_res.json()["username"] == "bob_agent"

    # 5. Access with invalid token
    bad_headers = {"Authorization": "Bearer invalidtoken123"}
    bad_res = await client.get("/auth/users/me", headers=bad_headers)
    assert bad_res.status_code == 401
