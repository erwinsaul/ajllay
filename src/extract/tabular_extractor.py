"""Extractor de archivos tabulares (CSV delimitado por '|', TSV, XLSX) usando Pandas."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd

from src.config import logger
from src.extract.base import BaseExtractor

class TabularExtractor(BaseExtractor):
    """Extractor en Pandas"""

    def __init__(self, file_path: Path, metadata: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(file_path, metadata)
    
    def _detect_encoding(self) -> str:
        """Detecta la codificacion del archivo"""
        if "codificacion" in self.metadata and self.metadata["codificacion"]:
            return str(self.metadata["codificacion"])
        
        raw_sample = self.file_path.read_bytes()[:131072]
        try:
            raw_sample.decode("utf-8")
            return "utf-8"
        except UnicodeDecodeError:
            return "latin1"
        
    def _detect_delimiter(self, encoding:str) -> str:
        """Detecta delimitador |"""
        if "delimitador" in self.metadata and self.metadata["delimitador"]:
            return str(self.metadata["delimitador"])
        
        with open(self.file_path, "r", encoding=encoding, errors="replace") as f:
            primera_linea = f.readline()
        
        if "|" in primera_linea:
            return "|"
        
        try:
            dialect = csv.Sniffer().sniff(primera_linea, delimiters="|;\t,")
            return dialect.delimiter
        except csv.Error:
            return ","
    
    def _read_raw(self) -> pd.DataFrame:
        """Lee archivos CSV o Excel hacia un DataFrame"""
        suffix = self.file_path.suffix.lower()
        if suffix in (".xlsx", ".xls")
            return pd.read_excel(self.file_path, dtype=str, keep_default_na=False)
        
        encoding = self._detect_encoding()
        delimiter = self._detect_delimiter(encoding)

        df = pd.read_csv(
            self.file_path,
            sep=delimiter,
            encoding=encoding,
            dtype=str,
            keep_default_na=False,
            low_memory=False,
        )
        return df