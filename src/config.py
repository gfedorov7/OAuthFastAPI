from pydantic_settings import BaseSettings


class DataBaseSettings(BaseSettings):
    database_url: str
    database_echo: bool

    class Config:
        env_file = ".env.backend"
        extra = "allow"

class OAuthSettings(BaseSettings):
    url: str = "http://localhost:8000/"
    endpoint_callback: str = "auth/login/callback"
    state_token_key: str = "oauth_state"
    current_token_type: str = "Bearer"
    refresh_token_cookie_key: str = "refresh_token"
    path_to_front_success_login: str = "http://localhost:8080/success.html?"

    google_auth_url: str = "https://accounts.google.com/o/oauth2/v2/auth?"
    google_exchange_url: str = "https://oauth2.googleapis.com/token"
    google_valid_access_token_url: str = "https://www.googleapis.com/oauth2/v1/tokeninfo?access_token="

    client_id: str
    client_secret: str

    grant_type: str = "authorization_code"
    grant_type_refresh: str = "refresh_token"

    class Config:
        env_file = ".env.backend"
        extra = "allow"

class Settings:
    database_settings: DataBaseSettings = DataBaseSettings()
    oauth_settings: OAuthSettings = OAuthSettings()

settings = Settings()