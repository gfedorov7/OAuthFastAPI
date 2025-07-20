from src.api.auth.utils.jose_decoder import JoseDecoder


def get_jose_decoder() -> JoseDecoder:
    return JoseDecoder()