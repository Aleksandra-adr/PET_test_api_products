from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

DATA_DIR = Path(os.environ.get("PRODUCTS_DATA_DIR", "data"))
STORAGE_PATH = DATA_DIR / "products.json"
TMP_PATH = DATA_DIR / "products.json.tmp"


class StorageCorruptedError(Exception):
    pass


def ensure_storage() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not STORAGE_PATH.exists():
        _write_atomic([])


def load_products() -> list[dict[str, Any]]:
    ensure_storage()
    try:
        with STORAGE_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        raise StorageCorruptedError(str(exc)) from exc
    if not isinstance(data, list):
        raise StorageCorruptedError("storage root must be a JSON array")
    return data


def save_products(products: list[dict[str, Any]]) -> None:
    _write_atomic(products)


def _write_atomic(products: list[dict[str, Any]]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with TMP_PATH.open("w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    os.replace(TMP_PATH, STORAGE_PATH)
