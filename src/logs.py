import logging
import logging.config
import os


def create_directory(directory: str = "logs"):
    os.makedirs(directory, exist_ok=True)

def setup_logging():
    create_directory()
    logging.config.fileConfig("logging.ini", disable_existing_loggers=False)