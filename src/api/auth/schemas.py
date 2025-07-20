from datetime import datetime

from pydantic import BaseModel


class LoginParams(BaseModel):
    client_id: str
    redirect_uri: str
    response_type: str = "code"
    scope: str = "openid email profile"
    state: str
    access_type: str = "offline"
    prompt: str = "consent"

class CodeMixin(BaseModel):
    client_id: str
    client_secret: str
    grant_type: str

class UpdateTokenRequest(CodeMixin):
    refresh_token: str

class ExchangeCode(CodeMixin):
    code: str
    redirect_uri: str

class UserCreate(BaseModel):
    email: str
    full_name: str
    image: str

class TokenSave(BaseModel):
    access_token: str
    expires_at: datetime
    refresh_token: str
    provider: str = "google"
    is_active: bool
    user_id: int
    token_type: str