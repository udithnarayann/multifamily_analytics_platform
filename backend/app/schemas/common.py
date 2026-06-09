from datetime import UTC, datetime
from typing import Any

JsonDict = dict[str, Any]


def utc_now() -> datetime:
    return datetime.now(UTC)
