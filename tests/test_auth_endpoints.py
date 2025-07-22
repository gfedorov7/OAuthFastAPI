from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock

from src.api.auth.dependencies.repositories_dependencies import get_user_repository, get_refresh_token_repository
from src.api.auth.dependencies.service_dependencies import get_google_login_with_cookie_and_hashlib_service, \
    get_exchange_code_to_token_with_httpx_and_cookie_service, get_check_valid_token_with_cookie_and_hmac_service, \
    get_save_token_service, get_user_save_service, get_refresh_token_service, get_current_user_service
from src.main import app
from src.api.auth.schemas import Token, UserRead
from src.pagination import PaginationModel
from src.utils.dependencies import get_cookie_storage_manager

client = TestClient(app)

@pytest.fixture
def mock_google_login_service():
    mock = MagicMock()
    mock.generate_response.return_value = client.app.router.routes[0].endpoint.__annotations__.get('response', None) or MagicMock()
    mock.generate_response.return_value = client.get("/")
    mock.generate_response.return_value = MagicMock(status_code=307, headers={"location": "https://accounts.google.com/o/oauth2/auth"})
    mock.save_state.return_value = None
    return mock

@pytest.fixture
def mock_check_valid_token_service():
    mock = MagicMock()
    mock.compare_token.return_value = None
    return mock

@pytest.fixture
def mock_exchange_code_to_token_service():
    mock = AsyncMock()
    mock.get_tokens.return_value = {
        "id_token": "mocked_id_token",
        "access_token": "mocked_access_token",
        "refresh_token": "mocked_refresh_token",
        "token_type": "Bearer"
    }
    return mock

@pytest.fixture
def mock_user_save_service():
    mock = AsyncMock()
    user = MagicMock(id=123)
    mock.save_user.return_value = user
    return mock

@pytest.fixture
def mock_save_token_service():
    mock = AsyncMock()
    token = MagicMock(
        token_type="Bearer",
        access_token="mocked_access_token",
        refresh_token="mocked_refresh_token"
    )
    mock.save_or_update_token.return_value = token
    return mock

@pytest.fixture
def mock_cookie_storage_manager():
    mock = MagicMock()
    mock.get_.return_value = "mocked_refresh_token"
    mock.set_response.return_value = None
    return mock

@pytest.fixture
def mock_refresh_token_service():
    mock = AsyncMock()
    mock.update_tokens.return_value = ({"token_type": "Bearer", "access_token": "new_access_token", "refresh_token": "new_refresh_token"}, 123)
    return mock

@pytest.fixture
def mock_current_user_service():
    mock = AsyncMock()
    mock.get_current_user.return_value = UserRead(email="test@gmail.com", full_name="test test test",
                                                  image="http://test.jpg", created_at=datetime.now())
    return mock

@pytest.fixture
def mock_user_repository():
    mock = AsyncMock()
    mock.count.return_value = 1
    mock.get_all.return_value = [MagicMock(email="test@gmail.com", full_name="test test test",
                                          image="http://test.jpg", created_at=datetime.now())]
    return mock

@pytest.fixture
def mock_refresh_token_repository():
    mock = AsyncMock()
    mock.get_by_conditions.return_value = [MagicMock(id=1, is_active=True)]
    mock.update.return_value = None
    return mock

def override_dependencies(**kwargs):
    for dep, mock in kwargs.items():
        app.dependency_overrides[dep] = lambda: mock


def clear_overrides():
    app.dependency_overrides = {}



def test_login_google_redirect(mock_google_login_service):
    app.dependency_overrides[get_google_login_with_cookie_and_hashlib_service] = lambda: mock_google_login_service
    response = client.get("/api/auth/login")
    assert response.status_code == 200
    clear_overrides()


@pytest.mark.asyncio
async def test_login_callback(monkeypatch,
                              mock_check_valid_token_service,
                              mock_exchange_code_to_token_service,
                              mock_user_save_service,
                              mock_save_token_service):
    app.dependency_overrides[get_check_valid_token_with_cookie_and_hmac_service] = lambda: mock_check_valid_token_service
    app.dependency_overrides[get_exchange_code_to_token_with_httpx_and_cookie_service] = lambda: mock_exchange_code_to_token_service
    app.dependency_overrides[get_user_save_service] = lambda: mock_user_save_service
    app.dependency_overrides[get_save_token_service] = lambda: mock_save_token_service

    response = client.get("/api/auth/login/callback?state=abc&code=123")
    assert response.status_code == 404
    clear_overrides()


def test_auth_refresh(mock_cookie_storage_manager,
                      mock_save_token_service,
                      mock_refresh_token_service):
    app.dependency_overrides[get_cookie_storage_manager] = lambda: mock_cookie_storage_manager
    app.dependency_overrides[get_save_token_service] = lambda: mock_save_token_service
    app.dependency_overrides[get_refresh_token_service] = lambda: mock_refresh_token_service

    response = client.post("/api/auth/refresh")
    assert response.status_code == 200
    json_resp = response.json()
    assert "access_token" in json_resp
    clear_overrides()


@pytest.mark.asyncio
async def test_get_users(mock_current_user_service,
                         mock_user_repository):
    app.dependency_overrides[get_current_user_service] = lambda: mock_current_user_service
    app.dependency_overrides[get_user_repository] = lambda: mock_user_repository

    response = client.get("/api/users?limit=1&offset=0", headers={"Authorization": "Bearer faketoken"})
    assert response.status_code == 200
    data = response.json()
    assert "items" in data and "total" in data
    clear_overrides()


@pytest.mark.asyncio
async def test_get_current_user(mock_current_user_service):
    app.dependency_overrides[get_current_user_service] = lambda: mock_current_user_service

    response = client.get("/api/current-user", headers={"Authorization": "Bearer faketoken"})
    assert response.status_code == 200
    data = response.json()
    assert data.get("email") == "test@gmail.com"
    clear_overrides()


@pytest.mark.asyncio
async def test_logout(mock_refresh_token_repository):
    app.dependency_overrides[get_refresh_token_repository] = lambda: mock_refresh_token_repository

    response = client.post("/api/auth/logout", cookies={"refresh_token_cookie_key": "tokenvalue"})
    assert response.status_code == 200 or response.status_code == 204
    clear_overrides()
