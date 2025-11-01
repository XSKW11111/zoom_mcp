def _extract_error_message(payload: object) -> str | None:
    """Pull a human-readable error message out of the Zoom API payload."""

    if isinstance(payload, dict):
        for key in ("message", "error", "errorMessage"):
            if key in payload and payload[key]:
                return str(payload[key])

    return None
