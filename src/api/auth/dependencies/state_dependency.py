from src.api.auth.utils.state_generator_hashlib import StateGeneratorHashlib
from src.api.auth.utils.state_compare_hmac import StateCompareHmac


def get_state_generator_hashlib(count_bytes: int = 1024) -> StateGeneratorHashlib:
    return StateGeneratorHashlib(count_bytes)

def get_state_compare_hmac() -> StateCompareHmac:
    return StateCompareHmac()