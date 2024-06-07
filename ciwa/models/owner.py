# filename: ciwa/models/owner.py

import logging
from typing import List, Optional, Dict
from ciwa.models.identifiable import Identifiable


class Owner(Identifiable):
    def __init__(self, name: str, email: str) -> None:
        super().__init__()
        self.name: str = name
        self.email: str = email
        self.processes: List["Process"] = []

    def add_process(self, process: "Process") -> None:
        self.processes.append(process)

    def get_processes(self) -> List["Process"]:
        return self.processes
