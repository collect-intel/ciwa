# models/owner.py

"""
This module defines the Owner class, representing an owner within the CIwA system.
An owner can manage multiple processes and has a name and email associated with them.
"""

from typing import List
from ciwa.models.identifiable import Identifiable


class Owner(Identifiable):
    """
    Represents an owner within the CIwA system.

    Attributes:
        name (str): The name of the owner.
        email (str): The email of the owner.
        processes (List[Process]): The list of processes managed by the owner.
    """

    def __init__(self, name: str, email: str) -> None:
        super().__init__()
        self.name: str = name
        self.email: str = email
        self.processes: List["Process"] = []

    def add_process(self, process: "Process") -> None:
        """
        Add a process to the owner's list of processes.

        Args:
            process (Process): The process to add.
        """
        self.processes.append(process)

    def get_processes(self) -> List["Process"]:
        """
        Get the list of processes associated with the owner.

        Returns:
            List[Process]: The list of processes.
        """
        return self.processes
