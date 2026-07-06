import logging
import os
import sys

def setup_logger(name="healthcare_fraud_logger", log_file="app.log", level=logging.INFO):
    """
    Configure and return a standard logger.
    """
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers if already configured
    if logger.handlers:
        return logger
        
    logger.setLevel(level)

    # Formatter
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s in %(module)s (line %(lineno)d): %(message)s"
    )

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Log file directory
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    # File Handler
    try:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"Warning: Failed to set up file logging: {e}")

    return logger

# Shared global logger instance
logger = setup_logger(log_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "app.log"))
