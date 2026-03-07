import pytest

from solution import EventRegistration, UserStatus, DuplicateRequest, NotFound


def test_register_until_capacity_then_waitlist_fifo_positions():
    er = EventRegistration(capacity=2)

    s1 = er.register("u1")
    s2 = er.register("u2")
    s3 = er.register("u3")
    s4 = er.register("u4")

    assert s1 == UserStatus("registered")
    assert s2 == UserStatus("registered")
    assert s3 == UserStatus("waitlisted", 1)
    assert s4 == UserStatus("waitlisted", 2)

    snap = er.snapshot()
    assert snap["registered"] == ["u1", "u2"]
    assert snap["waitlist"] == ["u3", "u4"]


def test_cancel_registered_promotes_earliest_waitlisted_fifo():
    er = EventRegistration(capacity=1)
    er.register("u1")
    er.register("u2")  # waitlist
    er.register("u3")  # waitlist

    er.cancel("u1")  # should promote u2

    assert er.status("u1") == UserStatus("none")
    assert er.status("u2") == UserStatus("registered")
    assert er.status("u3") == UserStatus("waitlisted", 1)

    snap = er.snapshot()
    assert snap["registered"] == ["u2"]
    assert snap["waitlist"] == ["u3"]


def test_duplicate_register_raises_for_registered_and_waitlisted():
    er = EventRegistration(capacity=1)
    er.register("u1")
    with pytest.raises(DuplicateRequest):
        er.register("u1")

    er.register("u2")  # waitlisted
    with pytest.raises(DuplicateRequest):
        er.register("u2")


def test_waitlisted_cancel_removes_and_updates_positions():
    er = EventRegistration(capacity=1)
    er.register("u1")
    er.register("u2")  # waitlist pos1
    er.register("u3")  # waitlist pos2

    er.cancel("u2")    # remove from waitlist

    assert er.status("u2") == UserStatus("none")
    assert er.status("u3") == UserStatus("waitlisted", 1)

    snap = er.snapshot()
    assert snap["registered"] == ["u1"]
    assert snap["waitlist"] == ["u3"]


def test_capacity_zero_all_waitlisted_and_promotion_never_happens():
    er = EventRegistration(capacity=0)
    assert er.register("u1") == UserStatus("waitlisted", 1)
    assert er.register("u2") == UserStatus("waitlisted", 2)

    # No one can ever be registered when capacity=0
    assert er.status("u1") == UserStatus("waitlisted", 1)
    assert er.status("u2") == UserStatus("waitlisted", 2)
    assert er.snapshot()["registered"] == []

    # Cancel unknown should raise NotFound
    with pytest.raises(NotFound):
        er.cancel("missing")



#################################################################################
# Add your own additional tests here to cover more cases and edge cases as needed.
#################################################################################
import pytest

from solution import EventRegistration, UserStatus, DuplicateRequest, NotFound


# Covers:
# Constraints: C1, C2, C9
# Acceptance Criteria: AC1
# Edge Cases: none
# Input:
#   capacity = 2
#   register("u1")
#   register("u2")
# Expected Output:
#   UserStatus("registered")
#   UserStatus("registered")
#   snapshot = {"registered": ["u1", "u2"], "waitlist": []}
def test_register_until_capacity():
    er = EventRegistration(capacity=2)

    s1 = er.register("u1")
    s2 = er.register("u2")

    assert s1 == UserStatus("registered")
    assert s2 == UserStatus("registered")
    assert er.snapshot() == {
        "registered": ["u1", "u2"],
        "waitlist": []
    }


# Covers:
# Constraints: C1, C2, C6, C8, C9
# Acceptance Criteria: AC2
# Edge Cases: EC2
# Input:
#   capacity = 2
#   register("u1")
#   register("u2")
#   register("u3")
# Expected Output:
#   UserStatus("waitlisted", 1) for u3
#   snapshot = {"registered": ["u1", "u2"], "waitlist": ["u3"]}
def test_register_when_capacity_full_goes_to_waitlist():
    er = EventRegistration(capacity=2)

    er.register("u1")
    er.register("u2")
    s3 = er.register("u3")

    assert s3 == UserStatus("waitlisted", 1)
    assert er.snapshot() == {
        "registered": ["u1", "u2"],
        "waitlist": ["u3"]
    }


# Covers:
# Constraints: C6, C8, C9
# Acceptance Criteria: AC3
# Edge Cases: EC4
# Input:
#   capacity = 1
#   register("u1")
#   register("u2")
#   register("u3")
#   cancel("u1")
# Expected Output:
#   status("u1") = UserStatus("none")
#   status("u2") = UserStatus("registered")
#   status("u3") = UserStatus("waitlisted", 1)
#   snapshot = {"registered": ["u2"], "waitlist": ["u3"]}
def test_cancel_registered_promotes_first_waitlisted():
    er = EventRegistration(capacity=1)

    er.register("u1")
    er.register("u2")
    er.register("u3")

    er.cancel("u1")

    assert er.status("u1") == UserStatus("none")
    assert er.status("u2") == UserStatus("registered")
    assert er.status("u3") == UserStatus("waitlisted", 1)
    assert er.snapshot() == {
        "registered": ["u2"],
        "waitlist": ["u3"]
    }


# Covers:
# Constraints: C4, C5
# Acceptance Criteria: AC4
# Edge Cases: EC6
# Input:
#   capacity = 1
#   register("u1")
#   register("u1")
# Expected Output:
#   first call succeeds with UserStatus("registered")
#   second call raises DuplicateRequest
def test_duplicate_registration_raises_exception():
    er = EventRegistration(capacity=1)

    er.register("u1")

    with pytest.raises(DuplicateRequest):
        er.register("u1")


# Covers:
# Constraints: C4, C5, C9
# Acceptance Criteria: AC5
# Edge Cases: EC5
# Input:
#   capacity = 1
#   register("u1")
#   register("u2")
#   cancel("u2")
# Expected Output:
#   status("u2") = UserStatus("none")
#   snapshot = {"registered": ["u1"], "waitlist": []}
def test_waitlisted_user_cancel_before_promotion():
    er = EventRegistration(capacity=1)

    er.register("u1")
    er.register("u2")

    er.cancel("u2")

    assert er.status("u2") == UserStatus("none")
    assert er.snapshot() == {
        "registered": ["u1"],
        "waitlist": []
    }


# Covers:
# Constraints: C1, C8, C9
# Acceptance Criteria: AC6
# Edge Cases: EC1
# Input:
#   capacity = 0
#   register("u1")
#   register("u2")
# Expected Output:
#   UserStatus("waitlisted", 1)
#   UserStatus("waitlisted", 2)
#   snapshot = {"registered": [], "waitlist": ["u1", "u2"]}
def test_capacity_zero_all_users_waitlisted():
    er = EventRegistration(capacity=0)

    s1 = er.register("u1")
    s2 = er.register("u2")

    assert s1 == UserStatus("waitlisted", 1)
    assert s2 == UserStatus("waitlisted", 2)
    assert er.snapshot() == {
        "registered": [],
        "waitlist": ["u1", "u2"]
    }


# Covers:
# Constraints: C4, C5, C6, C10
# Acceptance Criteria: AC7
# Edge Cases: EC9
# Input:
#   Run twice with:
#   capacity = 2
#   register("u1"), register("u2"), register("u3"), cancel("u1")
# Expected Output:
#   both runs produce identical snapshot
#   snapshot = {"registered": ["u2", "u3"], "waitlist": []}
def test_same_operation_sequence_is_deterministic():
    er1 = EventRegistration(capacity=2)
    er2 = EventRegistration(capacity=2)

    for er in (er1, er2):
        er.register("u1")
        er.register("u2")
        er.register("u3")
        er.cancel("u1")

    assert er1.snapshot() == er2.snapshot()
    assert er1.snapshot() == {
        "registered": ["u2", "u3"],
        "waitlist": []
    }


# Covers:
# Constraints: C7, C9
# Acceptance Criteria: AC8
# Edge Cases: EC10
# Input:
#   capacity = 1
#   register("u1")
#   status("u1")
# Expected Output:
#   status("u1") = UserStatus("registered")
#   snapshot = {"registered": ["u1"], "waitlist": []}
def test_status_after_completed_registration():
    er = EventRegistration(capacity=1)

    er.register("u1")
    result = er.status("u1")

    assert result == UserStatus("registered")
    assert er.snapshot() == {
        "registered": ["u1"],
        "waitlist": []
    }


# Covers:
# Constraints: C4, C5, C9
# Acceptance Criteria: AC9
# Edge Cases: none
# Input:
#   capacity = 2
#   register("u1")
#   status("u2")
# Expected Output:
#   status("u2") = UserStatus("none")
#   snapshot = {"registered": ["u1"], "waitlist": []}
def test_status_for_user_not_in_system():
    er = EventRegistration(capacity=2)

    er.register("u1")

    assert er.status("u2") == UserStatus("none")
    assert er.snapshot() == {
        "registered": ["u1"],
        "waitlist": []
    }


# Covers:
# Constraints: C6, C7, C9
# Acceptance Criteria: AC10
# Edge Cases: EC8
# Input:
#   capacity = 1
#   register("u1")
#   register("u2")
#   register("u3")
#   cancel("u1")
#   cancel("u2")
# Expected Output:
#   final snapshot = {"registered": ["u3"], "waitlist": []}
def test_multiple_cancellations_in_sequence():
    er = EventRegistration(capacity=1)

    er.register("u1")
    er.register("u2")
    er.register("u3")

    er.cancel("u1")
    er.cancel("u2")

    assert er.snapshot() == {
        "registered": ["u3"],
        "waitlist": []
    }


# Covers:
# Constraints: C9
# Acceptance Criteria: none directly, but needed for EC coverage
# Edge Cases: EC3
# Input:
#   capacity = 1
#   register("u1")
#   cancel("u1")
# Expected Output:
#   snapshot = {"registered": [], "waitlist": []}
#   status("u1") = UserStatus("none")
def test_cancel_registered_when_waitlist_empty():
    er = EventRegistration(capacity=1)

    er.register("u1")
    er.cancel("u1")

    assert er.snapshot() == {
        "registered": [],
        "waitlist": []
    }
    assert er.status("u1") == UserStatus("none")


# Covers:
# Constraints: C4, C5, C9
# Acceptance Criteria: none directly, but needed for EC coverage
# Edge Cases: EC7
# Input:
#   capacity = 1
#   register("u1")
#   cancel("u1")
#   register("u1")
# Expected Output:
#   second register returns UserStatus("registered")
#   snapshot = {"registered": ["u1"], "waitlist": []}
def test_reregister_after_cancel():
    er = EventRegistration(capacity=1)

    er.register("u1")
    er.cancel("u1")
    result = er.register("u1")

    assert result == UserStatus("registered")
    assert er.snapshot() == {
        "registered": ["u1"],
        "waitlist": []
    }


# Covers:
# Constraints: C4, C5, C9
# Acceptance Criteria: none directly, but needed for EC coverage
# Edge Cases: EC11
# Input:
#   capacity = 1
#   register("u1")
#   cancel("u1")
#   cancel("u1")
# Expected Output:
#   second cancel raises NotFound
def test_duplicate_cancellation_raises_notfound():
    er = EventRegistration(capacity=1)

    er.register("u1")
    er.cancel("u1")

    with pytest.raises(NotFound):
        er.cancel("u1")


# Covers:
# Constraints: C1
# Acceptance Criteria: none directly, but needed for constraint coverage
# Edge Cases: invalid capacity boundary
# Input:
#   capacity = -1
# Expected Output:
#   ValueError raised
def test_negative_capacity_rejected():
    with pytest.raises(ValueError):
        EventRegistration(capacity=-1)


# Covers:
# Constraints: C6, C9
# Acceptance Criteria: AC5 related behavior
# Edge Cases: EC5 plus FIFO preservation after middle removal
# Input:
#   capacity = 1
#   register("u1")
#   register("u2")
#   register("u3")
#   register("u4")
#   cancel("u3")
# Expected Output:
#   snapshot = {"registered": ["u1"], "waitlist": ["u2", "u4"]}
#   status("u2") = UserStatus("waitlisted", 1)
#   status("u4") = UserStatus("waitlisted", 2)
def test_waitlist_order_preserved_after_middle_waitlist_cancel():
    er = EventRegistration(capacity=1)

    er.register("u1")
    er.register("u2")
    er.register("u3")
    er.register("u4")

    er.cancel("u3")

    assert er.snapshot() == {
        "registered": ["u1"],
        "waitlist": ["u2", "u4"]
    }
    assert er.status("u2") == UserStatus("waitlisted", 1)
    assert er.status("u4") == UserStatus("waitlisted", 2)
