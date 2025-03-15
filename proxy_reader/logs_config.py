import logging

# Create the package-wide logger
logger = logging.getLogger("proxy_reader")
logger.addHandler(logging.NullHandler())
logger.setLevel(logging.WARNING)  # Default: Show only warnings/errors
