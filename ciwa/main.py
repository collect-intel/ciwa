# main.py

"""
This will run a CIwA Process based on a settings file given at the command line.
"""

import argparse
from ciwa.config import ConfigManager
from ciwa.models.process import ProcessFactory


def main() -> None:
    """
    Main function to initialize and run the process based on the configuration.
    """
    parser = argparse.ArgumentParser(
        description="Run CIwA process with a specified configuration file."
    )
    parser.add_argument(
        "--config",
        type=str,
        default="ciwa/config/settings.yaml",
        help="Path to the settings.yaml file",
    )
    args = parser.parse_args()

    config_manager = ConfigManager(config_path=args.config)
    process_config = config_manager.get_config("process")
    process = ProcessFactory.create_process(config=process_config)
    process.run()


if __name__ == "__main__":
    main()
