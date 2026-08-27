from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query, Response

from app.auth import authenticate_user, create_access_token, get_current_user
from app.errors import AppError
from app.models import (
    ErrorResponse,
    LoginRequest,
    Product,
    ProductCreate,
    ProductUpdate,
    SortOption,
    TokenResponse,
)
from app.storage import load_products, save_products

router = APIRouter(tags=["products"])

_STORAGE_CORRUPTED_RESPONSE = {
    "model": ErrorResponse,
    "description": "Файл-хранилище повреждён",
}
_NOT_FOUND_RESPONSE = {"model": ErrorResponse, "description": "Товар не найден"}
_VALIDATION_RESPONSE = {
    "model": ErrorResponse,
    "description": "Ошибка валидации, отсутствующее или неизвестное поле",
}
_UNAUTHORIZED_RESPONSE = {
    "model": ErrorResponse,
    "description": "Токен отсутствует, невалиден или истёк",
}


def _not_found(product_id: str) -> None:
    raise AppError(404, "NOT_FOUND", f"product {product_id} not found", field="id")


@router.post(
    "/auth/login",
    response_model=TokenResponse,
    tags=["auth"],
    summary="Получить JWT токен",
    description="Проверяет логин/пароль и возвращает access-токен для защищённых эндпоинтов.",
    responses={401: _UNAUTHORIZED_RESPONSE},
)
def login(payload: LoginRequest):
    if not authenticate_user(payload.username, payload.password):
        raise AppError(401, "INVALID_CREDENTIALS", "invalid username or password")
    return TokenResponse(access_token=create_access_token(payload.username))


@router.get(
    "/products",
    response_model=list[Product],
    summary="Список товаров",
    description=(
        "Возвращает список товаров с опциональным фильтром по цене "
        "(`min_price`, `max_price`), сортировкой (`sort`) и пагинацией "
        "(`limit`/`offset`). Порядок применения: сначала фильтр по цене, "
        "потом сортировка, потом пагинация."
    ),
    responses={400: _VALIDATION_RESPONSE, 500: _STORAGE_CORRUPTED_RESPONSE},
)
def list_products(
    min_price: Optional[float] = Query(default=None, description="Нижняя граница цены, включительно"),
    max_price: Optional[float] = Query(default=None, description="Верхняя граница цены, включительно"),
    sort: Optional[SortOption] = Query(
        default=None, description="Сортировка: price_asc, price_desc, name_asc, name_desc"
    ),
    limit: int = Query(default=20, ge=1, le=100, description="Размер страницы, 1–100"),
    offset: int = Query(default=0, ge=0, description="Смещение от начала списка"),
):
    products = load_products()

    if min_price is not None:
        products = [p for p in products if p["price"] >= min_price]
    if max_price is not None:
        products = [p for p in products if p["price"] <= max_price]

    sort_key = {
        "price_asc": (lambda p: p["price"], False),
        "price_desc": (lambda p: p["price"], True),
        "name_asc": (lambda p: p["name"], False),
        "name_desc": (lambda p: p["name"], True),
    }.get(sort)
    if sort_key is not None:
        key, reverse = sort_key
        products = sorted(products, key=key, reverse=reverse)

    return products[offset : offset + limit]


@router.get(
    "/products/{product_id}",
    response_model=Product,
    summary="Товар по id",
    description="Возвращает один товар по идентификатору.",
    responses={404: _NOT_FOUND_RESPONSE, 500: _STORAGE_CORRUPTED_RESPONSE},
)
def get_product(product_id: str):
    for product in load_products():
        if product["id"] == product_id:
            return product
    _not_found(product_id)


@router.post(
    "/products",
    response_model=Product,
    status_code=201,
    summary="Создать товар",
    description=(
        "Создаёт товар. `name` и `price` обязательны, `description` опционален. "
        "Неизвестные поля в теле запроса отклоняются."
    ),
    responses={400: _VALIDATION_RESPONSE, 401: _UNAUTHORIZED_RESPONSE, 500: _STORAGE_CORRUPTED_RESPONSE},
)
def create_product(payload: ProductCreate, _user: str = Depends(get_current_user)):
    products = load_products()
    product = {
        "id": str(uuid.uuid4()),
        "name": payload.name,
        "price": payload.price,
        "description": payload.description,
    }
    products.append(product)
    save_products(products)
    return product


@router.put(
    "/products/{product_id}",
    response_model=Product,
    summary="Обновить товар (полная замена)",
    description=(
        "Полностью заменяет товар. Все три поля обязательны, включая `description` "
        "(значение может быть `null`, но ключ должен присутствовать). Повторная "
        "отправка того же тела идемпотентна — возвращает тот же результат."
    ),
    responses={
        400: _VALIDATION_RESPONSE,
        401: _UNAUTHORIZED_RESPONSE,
        404: _NOT_FOUND_RESPONSE,
        500: _STORAGE_CORRUPTED_RESPONSE,
    },
)
def update_product(product_id: str, payload: ProductUpdate, _user: str = Depends(get_current_user)):
    products = load_products()
    for index, product in enumerate(products):
        if product["id"] == product_id:
            updated = {
                "id": product_id,
                "name": payload.name,
                "price": payload.price,
                "description": payload.description,
            }
            products[index] = updated
            save_products(products)
            return updated
    _not_found(product_id)


@router.delete(
    "/products/{product_id}",
    status_code=204,
    summary="Удалить товар",
    description="Удаляет товар по идентификатору.",
    responses={401: _UNAUTHORIZED_RESPONSE, 404: _NOT_FOUND_RESPONSE, 500: _STORAGE_CORRUPTED_RESPONSE},
)
def delete_product(product_id: str, _user: str = Depends(get_current_user)):
    products = load_products()
    for index, product in enumerate(products):
        if product["id"] == product_id:
            del products[index]
            save_products(products)
            return Response(status_code=204)
    _not_found(product_id)
