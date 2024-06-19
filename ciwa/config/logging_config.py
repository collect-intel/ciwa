# config/logging_config.py

"""
This module sets up logging configuration for the application.

It configures the logging to output log messages to both the console and a file.
"""

import logging

LOG_OUTPUT_FILE = "output.log"


def setup_logging():
    """
    Configures the logging module to log to both the console and a file.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(LOG_OUTPUT_FILE), logging.StreamHandler()],
    )


setup_logging()
