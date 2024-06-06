# filename: ciwa/models/process.py

import asyncio
import logging
from collections import deque
from typing import List, Optional, Dict, Any, Deque
from uuid import UUID, uuid4
from ciwa.config.config_manager import ConfigManager
from ciwa.models.session import SessionFactory


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class ProcessFactory:
    @staticmethod
    def create_process(**kwargs):
        """
        Create a Process instance from configurations and runtime parameters.

        Args:
            **kwargs: Arbitrary keyword arguments which can override the default configurations.

        Returns:
            Process: An instance of Process fully configured and ready for use.

        Description:
            This method fetches the default configuration for a process from the ConfigManager,
            applies any runtime overrides provided through kwargs, and then instantiates the
            Process class with a list of sessions created by the SessionFactory. This ensures
            that each Process is tailored to the specific requirements at runtime while adhering
            to the predefined configurations.
        """
        # Load default configuration and update with any provided overrides
        config = ConfigManager.get_instance().get_config("process")
        config.update(kwargs)  # Override defaults with any provided kwargs

        # Handle nested configurations for sessions
        default_session_settings = config.get("default_session_settings", {})
        sessions = deque(
            SessionFactory.create_session(**{**session, **default_session_settings})
            for session in config.pop("sessions", [])
        )

        # Additional processing can be added here if necessary (e.g., validation)

        # Create the Process instance with all configurations
        return Process(sessions=sessions, **config)


class Process:
    def __init__(
        self,
        name: str,
        description: str = None,
        sessions: Deque["session"] = [],
        **kwargs,
    ) -> None:
        self.uuid: UUID = uuid4()
        self.name: str = name
        self.description: str = description
        self.pending_sessions: Deque["Session"] = sessions
        self.current_session: Optional["Session"] = None
        self.completed_sessions: List["Session"] = []
        self.owners: List["Owner"] = []

    async def init_process(self) -> None:
        logging.info("Process initialized with default configurations.")

    def add_owner(self, owner: "Owner") -> None:
        self.owners.append(owner)
        logging.info(f"Owner {owner.name} added to process.")

    def update_process(self, updates: Dict[str, Any]) -> None:
        for key, value in updates.items():
            if hasattr(self, key):
                setattr(self, key, value)
                logging.info(f"Updated {key} to {value}")
            else:
                logging.error(f"Attempted to update non-existing attribute {key}")

    async def run_next_session(self) -> None:
        """
        Runs the next session in the process.

        :return: None
        """
        if self.current_session and not self.current_session.is_complete:
            raise Exception("Current session is still running")

        if self.pending_sessions:
            self.current_session = (
                self.pending_sessions.popleft()
            )  # Move the next session from pending to current
            await self.current_session.run()
            self.completed_sessions.append(self.current_session)
            self.current_session = None
        else:
            logging.info("No more sessions to run.")

    async def run_all_sessions(self) -> None:
        """
         Runs all sessions in the process synchronously, one after the other.

        :return: None
        """
        while self.pending_sessions:
            await self.run_next_session()

    def conclude_process(self) -> None:
        logging.info("Concluding the process...")


async def main() -> None:
    config_manager = ConfigManager.get_instance("ciwa/config/settings.yaml")
    process = ProcessFactory.create_process()
    await process.init_process()

    logging.info(f"Process {process.name} initialized with UUID: {process.uuid}")
    logging.info(f"Process sessions: {[s.uuid for s in process.pending_sessions]}")
    await process.run_all_sessions()

    process.conclude_process()


if __name__ == "__main__":
    asyncio.run(main())
