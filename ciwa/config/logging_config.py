# config/logging_config.py

import logging

LOG_OUTPUT_FILE = "output.log"


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(LOG_OUTPUT_FILE), logging.StreamHandler()],
    )


setup_logging()
