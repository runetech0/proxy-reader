import logging

# Create the package-wide logger
package_name = "proxy_reader"
logger = logging.getLogger(package_name)
logger.addHandler(logging.NullHandler())
logger.setLevel(logging.WARNING)  # Default: Show only warnings/errors


def enable_debug_logs() -> None:
    logger = logging.getLogger(package_name)
    logger.setLevel(logging.DEBUG)  # Set log level

    # 🔥 Make sure a handler is added (VERY IMPORTANT)
    ch = logging.StreamHandler()  # Console handler
    ch.setLevel(logging.DEBUG)  # Match the logger's level
    formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)  # Attach the handler
    logger.debug(f"Debugging enabled on {package_name!r}")
