"""Configuración centralizada de rutas y logging del proyecto."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Final

from rich.logging import Final

BASE_DIR: Final[Path] = Path(__file__).resolve().parent.parent

DATA_DIR: Final[Path] = BASE_DIR / "data"
RAW_DATA_DIR: Final[Path] = DATA_DIR / "raw"
PROCESSED_DATA_DIR: Final[Path] = DATA_DIR / "processed"
DOCS_DIR: Final[Path] = BASE_DIR / "docs"

STAGING_DIR: Final[Path] = PROCESSED_DATA_DIR / "staging"
SEEDS_DIR: Final[Path] = PROCESSED_DATA_DIR / "seeds"
WAREHOUSE_DIR: Final[Path] = PROCESSED_DATA_DIR / "warehouse"
EXPORTS_DIR: Final[Path] = PROCESSED_DATA_DIR / "exports"

CATALOG_PATH: Final[Path] = PROCESSED_DATA_DIR / "catologo_fuentes.json"
DUCKDB_PATH: Final[Path] = WAREHOUSE_DIR / "ajllay_electoral.duckdb"

for directory in (PROCESSED_DATA, STAGING_DIR, SEEDS_DIR, WAREHOUSE_DIR, EXPORTS_DIR, DOCS_DIR):
    directory.mkdir(parents=True, exist_ok=True)

def setup_logger(name: str = "ajllay", level: int = logging.INFO) -> logging.Logger:
    """Configura un logger con Rich"""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(level)
        handler = RichHandler(rich_tracebacks=True, markup=True, show_paths=False)
        handler.setFormatter(loggin.Formatter("%(message)s"))
        logger.addHandler(handler)
    return logger

logger = setupo_logger()