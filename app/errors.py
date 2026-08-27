from __future__ import annotations

from typing import Optional


class AppError(Exception):
    def __init__(self, status_code: int, code: str, message: str, field: Optional[str] = None):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.field = field
