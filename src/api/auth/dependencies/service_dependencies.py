from fastapi import Depends, Request, Response

from src.api.auth.dependencies.repositories_dependencies import (
    get_user_repository, get_refresh_token_repository
)
from src.api.auth.models import User, RefreshToken
from src.api.auth.services.current_user_service import CurrentUserService
from src.api.auth.services.google_login_service import GoogleLoginService
from src.api.auth.services.refresh_token_service import RefreshTokenService
from src.api.auth.services.save_tokens_service import SaveTokensService
from src.api.auth.services.save_user_service import UserSaveService
from src.api.auth.utils.state_compare import StateCompare
from src.database.base_repository import BaseRepository
from src.http_client.httpx_http_client import HttpxHttpClient
from src.storage.cookie_storage_manager import CookieStorageManager
from src.utils.dependencies import get_cookie_storage_manager, get_httpx_http_client
from src.api.auth.utils.state_generator_hashlib import StateGeneratorHashlib
from src.api.auth.dependencies.state_dependency import get_state_generator_hashlib
from src.api.auth.services.check_valid_token_service import CheckValidTokenService
from src.api.auth.dependencies.state_dependency import get_state_compare_hmac
from src.api.auth.services.exchange_code_to_token_service import ExchangeCodeToTokenService
from src.api.auth.dependencies.decoder_dependencies import get_jose_decoder
from src.api.auth.utils.jose_decoder import JoseDecoder


def get_google_login_with_cookie_and_hashlib_service(
        request: Request,
        cookie_manager: CookieStorageManager = Depends(get_cookie_storage_manager),
        state_generator_hashlib: StateGeneratorHashlib = Depends(get_state_generator_hashlib),
) -> GoogleLoginService:
    return GoogleLoginService(cookie_manager, state_generator_hashlib)

def get_check_valid_token_with_cookie_and_hmac_service(
        compare: StateCompare = Depends(get_state_compare_hmac),
        cookie_manager: CookieStorageManager = Depends(get_cookie_storage_manager),
) -> CheckValidTokenService:
    return CheckValidTokenService(compare, cookie_manager)

def get_exchange_code_to_token_with_httpx_and_cookie_service(
        httpx_client: HttpxHttpClient = Depends(get_httpx_http_client),
) -> ExchangeCodeToTokenService:
    return ExchangeCodeToTokenService(httpx_client)

def get_user_save_service(
        decoder: JoseDecoder = Depends(get_jose_decoder),
        repo: BaseRepository[User] = Depends(get_user_repository)
) -> UserSaveService:
    return UserSaveService(
        decoder,
        repo
    )

def get_save_token_service(
        response: Response,
        repo: BaseRepository[RefreshToken] = Depends(get_refresh_token_repository),
        cookie_manager: CookieStorageManager = Depends(get_cookie_storage_manager),
) -> SaveTokensService:
    return SaveTokensService(response, repo, cookie_manager)

def get_refresh_token_service(
        user_repo: BaseRepository[User] = Depends(get_user_repository),
        token_repo: BaseRepository[RefreshToken] = Depends(get_refresh_token_repository),
        httpx_client: HttpxHttpClient = Depends(get_httpx_http_client),
) -> RefreshTokenService:
    return RefreshTokenService(httpx_client, token_repo, user_repo)

def get_current_user_service(
        user_repo: BaseRepository[User] = Depends(get_user_repository),
        token_repo: BaseRepository[RefreshToken] = Depends(get_refresh_token_repository),
        httpx_client: HttpxHttpClient = Depends(get_httpx_http_client),
) -> CurrentUserService:
    return CurrentUserService(user_repo, token_repo, httpx_client)