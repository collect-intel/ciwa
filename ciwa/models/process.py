# models/process.py

"""
This module defines the ProcessFactory and Process classes for managing and running processes.
"""

import asyncio
import logging
from collections import deque
from typing import List, Dict, Any, Deque, Optional
from ciwa.config.config_manager import ConfigManager
from ciwa.models.session import SessionFactory
from ciwa.models.identifiable import Identifiable


class ProcessFactory:
    """
    Factory class for creating Process instances.
    """

    @staticmethod
    def create_process(config: Dict[str, Any]) -> "Process":
        """
        Create a Process instance from configurations and runtime parameters.

        Args:
            config (Dict[str, Any]): Configuration dictionary for the process.

        Returns:
            Process: An instance of Process fully configured and ready for use.
        """
        # Handle nested configurations for sessions
        default_session_settings = config.pop("default_session_settings", {})
        session_configs = config.pop("sessions", [])

        # Create the Process instance with all configurations
        return Process(
            session_configs=session_configs,
            default_session_settings=default_session_settings,
            **config,
        )


class Process(Identifiable):
    """
    Represents a process that manages and runs sessions.

    Attributes:
        name (str): The name of the process.
        description (Optional[str]): A description of the process.
        current_session (Optional["Session"]): The current session being run.
        completed_sessions (List["Session"]): List of completed sessions.
        owners (List["Owner"]): List of owners of the process.
        default_session_settings (Dict[str, Any]): Default settings for sessions.
        pending_sessions (Deque["Session"]): Queue of pending sessions to be run.
    """

    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        session_configs: Optional[List[Dict[str, Any]]] = None,
        default_session_settings: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> None:
        super().__init__()
        self.name: str = name
        self.description: Optional[str] = description
        self.current_session: Optional["Session"] = None
        self.completed_sessions: List["Session"] = []
        self.owners: List["Owner"] = []
        self.default_session_settings: Dict[str, Any] = default_session_settings or {}
        self.pending_sessions: Deque["Session"] = self._init_sessions(
            session_configs or [], self.default_session_settings
        )
        logging.info("Process initialized.")

    def _init_sessions(
        self,
        session_configs: List[Dict[str, Any]],
        default_session_settings: Dict[str, Any],
    ) -> Deque["Session"]:
        """
        Initialize sessions from the given configurations and default settings.

        Args:
            session_configs (List[Dict[str, Any]]): Configurations for the sessions.
            default_session_settings (Dict[str, Any]): Default settings for the sessions.

        Returns:
            Deque["Session"]: A deque of initialized sessions.
        """
        sessions = deque(
            SessionFactory.create_session(
                process=self, **{**default_session_settings, **session_config}
            )
            for session_config in session_configs
        )
        return sessions

    def add_owner(self, owner: "Owner") -> None:
        """
        Add an owner to the process.

        Args:
            owner (Owner): The owner to add.
        """
        self.owners.append(owner)
        logging.info("Owner %s added to process.", owner.name)

    def update_process(self, updates: Dict[str, Any]) -> None:
        """
        Update the process attributes.

        Args:
            updates (Dict[str, Any]): The attributes to update.
        """
        for key, value in updates.items():
            if hasattr(self, key):
                setattr(self, key, value)
                logging.info("Updated %s to %s", key, value)
            else:
                logging.error("Attempted to update non-existing attribute %s", key)

    def add_session(self, session_config: Dict[str, Any]) -> None:
        """
        Add a session to the process.

        Args:
            session_config (Dict[str, Any]): Configuration for the session to add.
        """
        new_session = SessionFactory.create_session(process=self, **session_config)
        self.pending_sessions.append(new_session)
        logging.info("Added new session: %s", new_session.name)

    def update_session(self, session_id: str, updates: Dict[str, Any]) -> None:
        """
        Update a session's attributes.

        Args:
            session_id (str): The ID of the session to update.
            updates (Dict[str, Any]): The attributes to update.
        """
        for session in self.pending_sessions:
            if session.uuid == session_id:
                for key, value in updates.items():
                    if hasattr(session, key):
                        setattr(session, key, value)
                        logging.info(
                            "Updated session %s: set %s to %s", session_id, key, value
                        )
                break

    async def run_next_session(self) -> None:
        """
        Runs the next session in the process.

        :return: None
        """
        if self.current_session and not self.current_session.is_complete:
            raise Exception("Current session is still running")

        if self.pending_sessions:
            self.current_session = self.pending_sessions.popleft()
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
        """
        Conclude the process.
        """
        logging.info("Concluding the process...")

    @staticmethod
    def get_object_schema() -> dict:
        """
        Returns the JSON schema to represent a Process object's properties.
        """
        return {
            "type": "object",
            "properties": {
                "uuid": {"type": "string"},
                "name": {"type": "string"},
                "description": {"type": "string"},
            },
            "required": ["uuid", "name", "description"],
        }

    def to_json(self) -> dict:
        """
        Returns the JSON representation of the Process object.
        """
        return {
            "uuid": str(self.uuid),
            "name": self.name,
            "description": self.description,
            "sessions": [session.to_json() for session in self.completed_sessions],
        }

    def run(self) -> None:
        """
        Run the process.
        """
        logging.info("Running process %s...", self.name)
        asyncio.run(self.run_all_sessions())
        self.conclude_process()


def main() -> None:
    """
    Main function to initialize and run the process based on the configuration.
    """
    config_manager = ConfigManager(config_path="ciwa/config/settings.yaml")
    process_config = config_manager.get_config("process")
    process = ProcessFactory.create_process(config=process_config)
    process.run()


if __name__ == "__main__":
    main()
