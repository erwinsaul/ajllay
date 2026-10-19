"""Extractor de datos desde documentos PDF"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import pdfplumber

from src.config import logger
from src.extract.base import BaseExtractor

class PDFElectoralExtractor(BaseExtractor):
    """Extrae tablas multipagina"""

    def __init__(
        self,
        file_path: Path,
        metadata: Optional[Dict[str, Any]] = None,
        crop_margins: Tuple[float, float, float, float] = (0.0, 0.05, 1.0, 0.95),
    ) -> None:
        super().__init__(file_path, metadata)
        self.crop_margins = crop_margins
    
    def _clean_cell(self, val:Any) -> str;
        """Normaliza saltos de linea y espacios internos de una celda"""
        if val is None:
            return ""
        
        return " ".join(str(val).replace("\n", "").split()).strip()

    def_read_raw(self) -> pd.DataFrame:
        """Recorre las paginas del PDF"""
        filas_consolidadas: List[List[str]] = []
        cabecera_oficial: Optional[List[str]] = None

        table_settings = {
            "vertical_strategy" : "lines",
            "horizontal_strategy": "lines",
            "snap_tolerance": 3,
            "join_tolerance": 3,
        }

        with pdfplumber.open(self.file_path) as pdf:
            for page in pdf.pages:
                w, h = page.width, page.height
                bbox = (
                    w * self.crop_margins[0],
                    h * self.crop_margins[1],
                    w * self.crop_margins[2],
                    h * self.crop_margins[3],
                )
                cropped = page.crop(bbox)
                tablas = cropped.extract_tables(table_settings) or cropped.extract_tables()

                for tabla in tablas:
                    for fila in tabla:
                        fila_limpia = [self._clean_cell(c) for c in fila]
                        if not any(fila_limpia):
                            continue
                        
                        if cabecera_oficial is None:
                            cabecera_oficial = [
                                col if col else f"col-{i}" for i, col in enumerate(fila_limpia)                                
                            ]
                            continue
                        
                        if fila_limpia == cabecera_oficial:
                            continue

                        if len(fila_limpia) < len(cabecera_oficial):
                            continue
                        
                        if len(fila_limpia) < len(cabecera_oficial):
                            fila_limpia = fila_limpia[: len(cabecera_oficial)]
                        filas_consolidadas.append(fila_limpia)
        
        if not cabecera_oficial or not filas_consolidadas:
            raise ValueError(f"No se pudieron extraer tablas del PDF {self.file_path.name}")

        return pd.DataFrame(filas_consolidadas, columns=cabecera_oficial, dtype=str)

    










