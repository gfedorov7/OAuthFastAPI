from fastapi import APIRouter, Response, Request, Depends

from src.api.auth.dependencies.repositories_dependencies import get_user_repository
from src.api.auth.models import User
from src.api.auth.schemas import UserRead
from src.api.auth.services.current_user_service import CurrentUserService
from src.api.auth.services.exchange_code_to_token_service import ExchangeCodeToTokenService
from src.api.auth.services.google_login_service import GoogleLoginService
from src.api.auth.dependencies.service_dependencies import (
    get_google_login_with_cookie_and_hashlib_service, get_exchange_code_to_token_with_httpx_and_cookie_service,
    get_user_save_service, get_save_token_service, get_refresh_token_service, get_current_user_service
)
from src.api.auth.services.check_valid_token_service import CheckValidTokenService
from src.api.auth.dependencies.service_dependencies import get_check_valid_token_with_cookie_and_hmac_service
from src.api.auth.services.save_tokens_service import SaveTokensService
from src.api.auth.services.save_user_service import UserSaveService
from src.api.auth.services.refresh_token_service import RefreshTokenService
from src.api.auth.utils.get_token_from_header import get_token_from_header
from src.database.base_repository import BaseRepository
from src.storage.storage_manager import ResponseAwareStorageManager
from src.pagination import PaginationModel


router = APIRouter(tags=["Google OAuth"])

def set_response_to_storage(service, response: Response):
    storage = service.storage_manager
    if isinstance(storage, ResponseAwareStorageManager):
        storage.set_response(response)

@router.get("/auth/login")
async def login_google(
        request: Request,
        google_login_service: GoogleLoginService = Depends(get_google_login_with_cookie_and_hashlib_service),
):
    response = google_login_service.generate_response()
    set_response_to_storage(google_login_service, response)

    google_login_service.save_state()

    return response

@router.get("/auth/login/callback")
async def login_callback(
        response: Response,
        state: str,
        code: str,
        check_valid_service: CheckValidTokenService = Depends(get_check_valid_token_with_cookie_and_hmac_service),
        exchange_service: ExchangeCodeToTokenService = Depends(get_exchange_code_to_token_with_httpx_and_cookie_service),
        user_save_service: UserSaveService = Depends(get_user_save_service),
        token_save_service: SaveTokensService = Depends(get_save_token_service),
):
    set_response_to_storage(check_valid_service, response)
    check_valid_service.compare_token(state)

    response_google = await exchange_service.get_tokens(code)

    id_token = response_google.get("id_token")
    user = await user_save_service.save_user(id_token)
    token = await token_save_service.save_or_update_token(response_google, user.id)

    return {
        "user": user,
        "token": token,
    }

@router.post("/auth/refresh")
async def auth_refresh(
        user_sub: str,
        token_save_service: SaveTokensService = Depends(get_save_token_service),
        refresh_token_service: RefreshTokenService = Depends(get_refresh_token_service),
):
    payload, user_id = await refresh_token_service.update_tokens(user_sub)
    token = await token_save_service.save_or_update_token(payload, user_id)

    return {
        "payload": payload,
        "token": token,
        "user_id": user_id,
    }

@router.get("/users")
async def get_users(
        limit: int = 10,
        offset: int = 0,
        token: str = Depends(get_token_from_header),
        current_user: CurrentUserService = Depends(get_current_user_service),
        user_repo: BaseRepository[User] = Depends(get_user_repository),
):
    await current_user.get_current_user(token)
    count = await user_repo.count()
    users = await user_repo.get_all(offset, limit)
    users_pydantic = [UserRead.model_validate(user, from_attributes=True) for user in users]

    return PaginationModel[UserRead](items=users_pydantic, total=count)