from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, field_validator

SortOption = Literal["price_asc", "price_desc", "name_asc", "name_desc"]


def _round_price(value: float) -> float:
    return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


class ProductCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    price: float
    description: Optional[str] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if not value.strip() or len(value) > 100:
            raise ValueError("name must be 1-100 characters and not only whitespace")
        return value

    @field_validator("price")
    @classmethod
    def validate_price(cls, value: float) -> float:
        rounded = _round_price(value)
        if rounded <= 0:
            raise ValueError("price must be greater than 0")
        return rounded


class ProductUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    price: float
    description: Optional[str]

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if not value.strip() or len(value) > 100:
            raise ValueError("name must be 1-100 characters and not only whitespace")
        return value

    @field_validator("price")
    @classmethod
    def validate_price(cls, value: float) -> float:
        rounded = _round_price(value)
        if rounded <= 0:
            raise ValueError("price must be greater than 0")
        return rounded


class Product(BaseModel):
    id: str
    name: str
    price: float
    description: Optional[str] = None


class ErrorResponse(BaseModel):
    code: str
    message: str
    field: Optional[str] = None


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
