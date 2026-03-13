import pytest

from solution import EventRegistration


# Covers C3, C15, C16, AC1
def test_register_two_users_returns_one_result_and_updated_state():
    er = EventRegistration(2)

    r1 = er.register("UserA")
    r2 = er.register("UserB")

    assert r1["operation_result"] == "registered"
    assert r2["operation_result"] == "registered"
    assert r2["registered_list"] == ["UserA", "UserB"]
    assert r2["waitlist"] == []
    assert set(r2.keys()) == {
        "operation_result",
        "explanation",
        "registered_list",
        "waitlist",
        "user_status",
        "waitlist_position",
    }


# Covers C1, C2, C7, C14, AC2
def test_cancel_promotes_earliest_waitlisted_with_explicit_result():
    er = EventRegistration(1)
    er.register("UserA")
    er.register("UserB")

    result = er.cancel("UserA")

    assert result["operation_result"] == "canceled_with_promotion"
    assert "promoted" in result["explanation"]
    assert result["registered_list"] == ["UserB"]
    assert result["waitlist"] == []


# Covers C4, C8, C9, C10, C13, C15, AC3
def test_duplicate_registered_user_is_rejected_explicitly():
    er = EventRegistration(1)
    er.register("UserA")

    result = er.register("UserA")

    assert result["operation_result"] == "duplicate_rejected"
    assert "rejected" in result["explanation"]
    assert result["registered_list"] == ["UserA"]
    assert result["waitlist"] == []


# Covers C8, C10, C12, C15, C16, AC4
def test_capacity_zero_places_all_users_in_waitlist():
    er = EventRegistration(0)

    r1 = er.register("UserA")
    r2 = er.register("UserB")

    assert r1["operation_result"] == "waitlisted"
    assert r2["operation_result"] == "waitlisted"
    assert r2["registered_list"] == []
    assert r2["waitlist"] == ["UserA", "UserB"]


# Covers C8, C9, C10, C13, C15, AC5
def test_cancel_missing_user_returns_explicit_error_and_preserves_state():
    er = EventRegistration(1)
    er.register("UserA")

    before = er.snapshot()
    result = er.cancel("UserB")
    after = er.snapshot()

    assert result["operation_result"] == "not_found"
    assert "not found" in result["explanation"]
    assert before == after


# Covers C1, C6, C8, C15, AC6
def test_waitlisted_user_cancel_preserves_relative_order():
    er = EventRegistration(1)
    er.register("UserA")
    er.register("UserB")
    er.register("UserC")

    result = er.cancel("UserB")

    assert result["operation_result"] == "waitlist_canceled"
    assert result["registered_list"] == ["UserA"]
    assert result["waitlist"] == ["UserC"]


# Covers C5, C6, C12, C15, AC7
def test_same_initial_state_and_sequence_produce_same_result():
    er1 = EventRegistration(2)
    er2 = EventRegistration(2)

    for er in (er1, er2):
        er.register("UserA")
        er.register("UserB")
        er.register("UserC")
        final = er.cancel("UserA")

    assert er1.snapshot() == er2.snapshot()
    assert final["registered_list"] == ["UserB", "UserC"]
    assert final["waitlist"] == []


# Covers C9, C10, C13, C15, AC8
def test_status_for_missing_user_is_explicit():
    er = EventRegistration(1)
    er.register("UserA")

    result = er.status("UserB")

    assert result["operation_result"] == "status_reported"
    assert result["user_status"] == "not_found"
    assert "not found" in result["explanation"]


# Covers C11, C12, C15, AC9
def test_multiple_cancellations_in_sequence_preserve_valid_state():
    er = EventRegistration(1)
    er.register("UserA")
    er.register("UserB")

    first = er.cancel("UserA")
    second = er.cancel("UserB")

    assert first["registered_list"] == ["UserB"]
    assert second["registered_list"] == []
    assert second["waitlist"] == []


# Covers C10, C12, C15, AC10
def test_status_for_waitlisted_user_reports_waitlisted():
    er = EventRegistration(1)
    er.register("UserA")
    er.register("UserB")

    result = er.status("UserB")

    assert result["operation_result"] == "status_reported"
    assert result["user_status"] == "waitlisted"
    assert result["waitlist_position"] == 1


# Covers C11, C12, C15, AC11
def test_reregister_after_cancel_is_accepted_as_new_request():
    er = EventRegistration(1)
    er.register("UserA")
    er.cancel("UserA")

    result = er.register("UserA")

    assert result["operation_result"] == "registered"
    assert result["registered_list"] == ["UserA"]
    assert result["waitlist"] == []


# Covers C3, C10, C15, AC12
def test_status_for_registered_user_is_explicit():
    er = EventRegistration(1)
    er.register("UserA")

    result = er.status("UserA")

    assert result["operation_result"] == "status_reported"
    assert result["user_status"] == "registered"
    assert "registered" in result["explanation"]


# Covers C1, C6, EC4
def test_promotion_is_fifo_when_multiple_users_wait():
    er = EventRegistration(1)
    er.register("UserA")
    er.register("UserB")
    er.register("UserC")
    er.register("UserD")

    result = er.cancel("UserA")

    assert result["registered_list"] == ["UserB"]
    assert result["waitlist"] == ["UserC", "UserD"]


# Covers C8, C10, C12, EC9
def test_registered_cancel_with_empty_waitlist_returns_explicit_result():
    er = EventRegistration(1)
    er.register("UserA")

    result = er.cancel("UserA")

    assert result["operation_result"] == "canceled"
    assert result["registered_list"] == []
    assert result["waitlist"] == []


# Covers C8, C10, C12, EC10
def test_repeated_cancellation_returns_explicit_error_and_preserves_last_valid_state():
    er = EventRegistration(1)
    er.register("UserA")
    er.cancel("UserA")

    result = er.cancel("UserA")

    assert result["operation_result"] == "not_found"
    assert result["registered_list"] == []
    assert result["waitlist"] == []


# Covers C4, C8, C9, C10, C13, C15, EC2
def test_duplicate_waitlisted_user_is_rejected_explicitly():
    er = EventRegistration(1)
    er.register("UserA")
    er.register("UserB")

    result = er.register("UserB")

    assert result["operation_result"] == "duplicate_rejected"
    assert result["registered_list"] == ["UserA"]
    assert result["waitlist"] == ["UserB"]


# Covers C1, C6, C8, EC5
def test_middle_waitlist_cancellation_keeps_remaining_order():
    er = EventRegistration(1)
    er.register("UserA")
    er.register("UserB")
    er.register("UserC")
    er.register("UserD")

    result = er.cancel("UserC")

    assert result["waitlist"] == ["UserB", "UserD"]


# Covers C16, FR capacity bound
def test_registered_count_never_exceeds_capacity():
    er = EventRegistration(2)
    er.register("UserA")
    er.register("UserB")
    result = er.register("UserC")

    assert len(result["registered_list"]) == 2
    assert len(result["registered_list"]) <= 2
    assert result["waitlist"] == ["UserC"]


# Covers C15 consistent response structure across operations
def test_register_cancel_status_use_same_response_structure():
    er = EventRegistration(1)

    reg = er.register("UserA")
    cancel = er.cancel("UserA")
    status = er.status("UserA")

    assert set(reg.keys()) == set(cancel.keys()) == set(status.keys())


# Covers C7, C10, C13 explicit explanation for promotion
def test_promotion_explanation_names_promoted_user():
    er = EventRegistration(1)
    er.register("UserA")
    er.register("UserB")

    result = er.cancel("UserA")

    assert "UserB" in result["explanation"]
    assert "promoted" in result["explanation"]


# Covers initialization assumption/constraint on non-negative capacity
def test_negative_capacity_raises_value_error():
    with pytest.raises(ValueError):
        EventRegistration(-1)
