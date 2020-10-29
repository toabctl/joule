from enum import Enum
from typing import Optional


class Events(Enum):
    """
    Enumeration of possible events.
    """

    JOIN = 0
    LAUNCH = 1
    TERMINATE = 2


class Event:
    """
    Event instance.
    """

    def __init__(self, event: Enum, instance: str, token: Optional[str] = None):
        self.event: Enum = event
        self.instance: str = instance
        self.token: Optional[str] = token
