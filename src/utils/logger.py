import logging
from datetime import datetime

def setup_logger():
    # Create logger
    logger = logging.getLogger('NewsDigest')
    logger.setLevel(logging.INFO)

    # Create console handler with formatting
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '\n%(asctime)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Add formatter to console handler
    console.setFormatter(formatter)
    
    # Add console handler to logger
    logger.addHandler(console)
    
    return logger

logger = setup_logger()