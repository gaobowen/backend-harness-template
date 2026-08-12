from app.schemas.common import fail, ok


def test_response_helpers_keep_a_stable_envelope() -> None:
    assert ok({"value": 1}).model_dump() == {"code": 200, "data": {"value": 1}, "msg": ""}
    assert fail(code=400, msg="bad", error_code="BAD").model_dump() == {
        "code": 400,
        "data": {"error_code": "BAD"},
        "msg": "bad",
    }
