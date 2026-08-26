# Error messages must never persist API credentials.
from yawarakame.errors import safe_error_message


class UnauthorizedError(Exception):
    status_code = 401


def test_unauthorized_error_does_not_echo_key() -> None:
    error = UnauthorizedError("Incorrect API key provided: secret-part-123")
    message = safe_error_message(error)
    assert "secret-part-123" not in message
    assert "401" in message


def test_generic_error_redacts_api_key() -> None:
    message = safe_error_message(Exception("api_key=sk-example-secret failed"))
    assert "sk-example-secret" not in message
    assert "[REDACTED]" in message
