# models/identifiable.py

"""
This module defines the IdentifiableMixin and Identifiable classes, which provide
UUID-based identification for objects.
"""

from abc import ABC
from uuid import uuid4, UUID


class IdentifiableMixin:
    """
    Mixin class that provides a unique identifier (UUID) for an object.
    """

    def __init__(self) -> None:
        self._uuid: UUID = uuid4()

    @property
    def uuid(self) -> str:
        """
        Returns the UUID of the object as a string.

        Returns:
            str: The UUID of the object.
        """
        return str(self._uuid)

    def get_id_str(self) -> str:
        """
        Returns a string representation of the object's class name and UUID.

        Returns:
            str: The string representation of the object's class name and UUID.
        """
        return f"{self.__class__.__name__}_{self.uuid}"


class Identifiable(ABC, IdentifiableMixin):
    """
    Abstract base class that combines IdentifiableMixin and ABC,
    providing UUID-based identification and abstract base class functionality.
    """

    def __init__(self) -> None:
        IdentifiableMixin.__init__(self)
