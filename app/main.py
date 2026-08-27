from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse

from app.errors import AppError
from app.routes import router
from app.storage import StorageCorruptedError, ensure_storage


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_storage()
    yield


app = FastAPI(
    title="Витрина товаров",
    description=(
        "Учебный API витрины товаров: список с фильтром/сортировкой/пагинацией, "
        "получение, создание, полное обновление и удаление товара. "
        "Хранилище — локальный JSON-файл, без базы данных."
    ),
    version="0.1.0",
    lifespan=lifespan,
)
app.include_router(router)


def _custom_openapi() -> dict:
    # FastAPI по умолчанию документирует 422 для эндпоинтов с валидацией, но наш
    # validation_error_handler всегда превращает такие ошибки в 400 (см. SPEC.md) —
    # 422 в реальности не возвращается никогда, убираем его из схемы, чтобы Swagger
    # не расходился с фактическим поведением.
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    for path_item in schema.get("paths", {}).values():
        for operation in path_item.values():
            operation.get("responses", {}).pop("422", None)
    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = _custom_openapi

_VALIDATION_TYPE_TO_CODE = {
    "missing": "MISSING_FIELD",
    "extra_forbidden": "UNKNOWN_FIELD",
}


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.code, "message": exc.message, "field": exc.field},
    )


@app.exception_handler(StorageCorruptedError)
async def storage_corrupted_handler(request: Request, exc: StorageCorruptedError) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={
            "code": "STORAGE_CORRUPTED",
            "message": f"Storage file is corrupted: {exc}",
            "field": None,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    first = exc.errors()[0]
    loc = [part for part in first["loc"] if part not in ("body", "query", "path")]
    field = ".".join(str(part) for part in loc) if loc else None

    code = _VALIDATION_TYPE_TO_CODE.get(first["type"], "VALIDATION_ERROR")

    message = first.get("msg", "validation error")
    prefix = "Value error, "
    if message.startswith(prefix):
        message = message[len(prefix) :]

    return JSONResponse(status_code=400, content={"code": code, "message": message, "field": field})
