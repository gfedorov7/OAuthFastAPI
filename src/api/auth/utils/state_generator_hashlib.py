import hashlib
import os

from src.api.auth.utils.state_generator import StateGenerator


class StateGeneratorHashlib(StateGenerator):
    def __init__(self, count_bytes: int = 1024):
        self.count_bytes = count_bytes

    def generate(self):
        return hashlib.sha512(os.urandom(self.count_bytes)).hexdigest()