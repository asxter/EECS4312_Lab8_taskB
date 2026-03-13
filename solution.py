from __future__ import annotations

from typing import Dict, List, Optional


class EventRegistration:
    """
    Event registration system for a single event with:
    - fixed non-negative capacity
    - FIFO waitlist
    - automatic promotion
    - explicit, consistent results for every operation
    """

    def __init__(self, capacity: int) -> None:
        if not isinstance(capacity, int):
            raise TypeError("capacity must be an integer")
        if capacity < 0:
            raise ValueError("capacity must be non-negative")

        self._capacity: int = capacity
        self._registered: List[str] = []
        self._waitlist: List[str] = []

    def _response(
        self,
        operation_result: str,
        explanation: str,
        user_status: Optional[str] = None,
        waitlist_position: Optional[int] = None,
    ) -> Dict[str, object]:
        return {
            "operation_result": operation_result,
            "explanation": explanation,
            "registered_list": list(self._registered),
            "waitlist": list(self._waitlist),
            "user_status": user_status,
            "waitlist_position": waitlist_position,
        }

    def register(self, user: str) -> Dict[str, object]:
        if user in self._registered or user in self._waitlist:
            return self._response(
                operation_result="duplicate_rejected",
                explanation=f"Registration rejected because user '{user}' is already in the system.",
            )

        if len(self._registered) < self._capacity:
            self._registered.append(user)
            return self._response(
                operation_result="registered",
                explanation=f"User '{user}' was added to the registered list.",
            )

        self._waitlist.append(user)
        return self._response(
            operation_result="waitlisted",
            explanation=f"User '{user}' was added to the waitlist because capacity is full.",
        )

    def cancel(self, user: str) -> Dict[str, object]:
        if user in self._registered:
            self._registered.remove(user)

            if self._waitlist:
                promoted = self._waitlist.pop(0)
                self._registered.append(promoted)
                return self._response(
                    operation_result="canceled_with_promotion",
                    explanation=(
                        f"User '{user}' was removed from the registered list. "
                        f"User '{promoted}' was promoted from the waitlist."
                    ),
                )

            return self._response(
                operation_result="canceled",
                explanation=f"User '{user}' was removed from the registered list.",
            )

        if user in self._waitlist:
            self._waitlist.remove(user)
            return self._response(
                operation_result="waitlist_canceled",
                explanation=f"User '{user}' was removed from the waitlist.",
            )

        return self._response(
            operation_result="not_found",
            explanation=f"Cancellation failed because user '{user}' was not found in the system.",
        )

    def status(self, user: str) -> Dict[str, object]:
        if user in self._registered:
            return self._response(
                operation_result="status_reported",
                explanation=f"User '{user}' is currently registered.",
                user_status="registered",
            )

        if user in self._waitlist:
            position = self._waitlist.index(user) + 1
            return self._response(
                operation_result="status_reported",
                explanation=f"User '{user}' is currently waitlisted at position {position}.",
                user_status="waitlisted",
                waitlist_position=position,
            )

        return self._response(
            operation_result="status_reported",
            explanation=f"User '{user}' was not found in the system.",
            user_status="not_found",
        )

    def snapshot(self) -> Dict[str, List[str]]:
        return {
            "registered": list(self._registered),
            "waitlist": list(self._waitlist),
        }
