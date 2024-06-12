# models/identifiable.py

from abc import ABC
from uuid import uuid4, UUID


class IdentifiableMixin:
    def __init__(self) -> None:
        self._uuid: UUID = uuid4()

    @property
    def uuid(self) -> str:
        return str(self._uuid)

    def get_id_str(self) -> str:
        return f"{self.__class__.__name__}_{self.uuid}"


class Identifiable(ABC, IdentifiableMixin):
    def __init__(self) -> None:
        super().__init__()
