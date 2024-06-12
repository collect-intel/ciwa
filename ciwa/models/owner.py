# models/owner.py

from typing import List
from ciwa.models.identifiable import Identifiable


class Owner(Identifiable):
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
