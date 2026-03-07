## Student Name:
## Student ID:

from dataclasses import dataclass
from typing import List, Optional


class DuplicateRequest(Exception):
    """Raised if a user tries to register but is already registered or waitlisted."""
    pass


class NotFound(Exception):
    """Raised if a user cannot be found for cancellation."""
    pass


@dataclass(frozen=True)
class UserStatus:
    """
    state:
      - "registered"
      - "waitlisted"
      - "none"
    position: 1-based waitlist position if waitlisted; otherwise None
    """
    state: str
    position: Optional[int] = None


class EventRegistration:
    """
    Event registration system with:
      - fixed capacity
      - FIFO waitlist
      - deterministic promotion
      - duplicate prevention
      - status lookup
    """

    def __init__(self, capacity: int) -> None:
        """
        Args:
            capacity: maximum number of registered users (>= 0)
        """
        if not isinstance(capacity, int):
            raise TypeError("capacity must be an integer")
        if capacity < 0:
            raise ValueError("capacity must be >= 0")

        self._capacity: int = capacity
        self._registered: List[str] = []
        self._waitlist: List[str] = []

    def register(self, user_id: str) -> UserStatus:
        """
        Register a user:
          - if capacity available -> registered
          - else -> waitlisted (FIFO)

        Raises:
            DuplicateRequest if user already exists (registered or waitlisted)
        """
        if user_id in self._registered or user_id in self._waitlist:
            raise DuplicateRequest(f"{user_id} is already in the system")

        if len(self._registered) < self._capacity:
            self._registered.append(user_id)
            return UserStatus("registered")

        self._waitlist.append(user_id)
        return UserStatus("waitlisted", len(self._waitlist))

    def cancel(self, user_id: str) -> None:
        """
        Cancel a user:
          - if registered -> remove and promote earliest waitlisted user (if any)
          - if waitlisted -> remove from waitlist
          - if not found -> raise NotFound

        Raises:
            NotFound
        """
        if user_id in self._registered:
            self._registered.remove(user_id)

            if self._waitlist and len(self._registered) < self._capacity:
                promoted = self._waitlist.pop(0)
                self._registered.append(promoted)
            return

        if user_id in self._waitlist:
            self._waitlist.remove(user_id)
            return

        raise NotFound(f"{user_id} was not found")

    def status(self, user_id: str) -> UserStatus:
        """
        Return status of a user:
          - registered
          - waitlisted with position (1-based)
          - none
        """
        if user_id in self._registered:
            return UserStatus("registered")

        if user_id in self._waitlist:
            return UserStatus("waitlisted", self._waitlist.index(user_id) + 1)

        return UserStatus("none")

    def snapshot(self) -> dict:
        """
        Return a deterministic snapshot of internal state.
        """
        return {
            "registered": list(self._registered),
            "waitlist": list(self._waitlist),
        }
