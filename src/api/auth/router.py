from fastapi import APIRouter, Response, Request, Depends
from fastapi.responses import RedirectResponse

from src.api.auth.services.exchange_code_to_token_service import ExchangeCodeToTokenService
from src.api.auth.services.google_login_service import GoogleLoginService
from src.api.auth.dependencies.service_dependencies import (
    get_google_login_with_cookie_and_hashlib_service, get_exchange_code_to_token_with_httpx_and_cookie_service,
    get_user_save_service, get_save_token_service
)
from src.api.auth.services.check_valid_token_service import CheckValidTokenService
from src.api.auth.dependencies.service_dependencies import get_check_valid_token_with_cookie_and_hmac_service
from src.api.auth.services.save_tokens_service import SaveTokensService
from src.api.auth.services.save_user_service import UserSaveService
from src.storage.storage_manager import ResponseAwareStorageManager


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
