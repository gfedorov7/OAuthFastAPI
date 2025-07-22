from urllib.parse import urlencode

from fastapi import APIRouter, Response, Request, Depends
from starlette.responses import RedirectResponse

from src.api.auth.dependencies.repositories_dependencies import get_user_repository, get_refresh_token_repository
from src.api.auth.models import User, RefreshToken
from src.api.auth.schemas import UserRead, Token
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
from src.config import settings
from src.database.base_repository import BaseRepository
from src.storage.storage_manager import ResponseAwareStorageManager
from src.pagination import PaginationModel
from src.utils.dependencies import get_cookie_storage_manager

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
        state: str,
        code: str,
        check_valid_service: CheckValidTokenService = Depends(get_check_valid_token_with_cookie_and_hmac_service),
        exchange_service: ExchangeCodeToTokenService = Depends(get_exchange_code_to_token_with_httpx_and_cookie_service),
        user_save_service: UserSaveService = Depends(get_user_save_service),
        token_save_service: SaveTokensService = Depends(get_save_token_service),
):
    check_valid_service.compare_token(state)

    response_google = await exchange_service.get_tokens(code)
    id_token = response_google.get("id_token")

    user = await user_save_service.save_user(id_token)
    token = await token_save_service.save_or_update_token(response_google, user.id)

    token_params = Token(
        token_type=token.token_type,
        access_token=token.access_token,
    )
    query_params = urlencode(token_params.model_dump())

    url = settings.oauth_settings.path_to_front_success_login + query_params
    response = RedirectResponse(url)
    response.set_cookie(
        settings.oauth_settings.refresh_token_cookie_key,
        token.refresh_token,
        httponly=True,
        secure=True,
        path="/"
    )
    return response

@router.post("/auth/refresh")
async def auth_refresh(
        response: Response,
        cookie_storage: ResponseAwareStorageManager = Depends(get_cookie_storage_manager),
        token_save_service: SaveTokensService = Depends(get_save_token_service),
        refresh_token_service: RefreshTokenService = Depends(get_refresh_token_service),
):
    refresh_token = cookie_storage.get_(settings.oauth_settings.refresh_token_cookie_key)
    payload, user_id = await refresh_token_service.update_tokens(refresh_token)
    token = await token_save_service.save_or_update_token(payload, user_id)

    return Token(
        token_type=token.token_type,
        access_token=token.access_token,
    )

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

@router.get("/current-user")
async def get_current_user(
        token: str = Depends(get_token_from_header),
        current_user: CurrentUserService = Depends(get_current_user_service),
) -> UserRead:
    return await current_user.get_current_user(token)

@router.post("/auth/logout")
async def logout(
        response: Response,
        request: Request,
        token_repository: BaseRepository[Token] = Depends(get_refresh_token_repository),
):
    refresh_token = request.cookies.get(settings.oauth_settings.refresh_token_cookie_key)
    response.delete_cookie(
        settings.oauth_settings.refresh_token_cookie_key,
        httponly=True,
        secure=True,
        path="/",
    )

    if not refresh_token:
        return

    tokens = await token_repository.get_by_conditions(RefreshToken.refresh_token == refresh_token)
    if tokens:
        token = tokens[0]
        await token_repository.update(token.id, {"is_active": False})