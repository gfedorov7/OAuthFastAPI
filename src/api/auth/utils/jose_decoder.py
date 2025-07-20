import logging

from jose import jwt
from jose.exceptions import JWTError

from src.api.auth.utils.decoder import Decoder
from src.exceptions import InternalServerError


logger = logging.getLogger("app.api.auth.utils.jose_decoder")

class JoseDecoder(Decoder):
    def decode(self, token: str) -> dict:
        try:
            return jwt.get_unverified_claims(token)
        except JWTError as e:
            logger.warning(f"Error: {e}")
            raise InternalServerError()