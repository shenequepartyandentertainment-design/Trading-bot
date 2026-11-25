Create bot/utils.py and paste:
import logging
from datetime import datetime
from pathlib import Path

def setup_logger(name: str, log_file: str, level=logging.INFO):
    """
    Create and return a logger that writes to the given log_file.
    """
    # Make sure directory exists
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid adding multiple handlers if called more than once
    if not logger.handlers:
        logger.addHandler(handler)

    return logger

def now_str() -> str:
    """
    Return current UTC time as a string.
    """
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
