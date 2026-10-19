"""Contrato base para los extractores"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd

from src.config import logger

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd

from src.config import logger

class BaseExtractor(ABC):
    """Clase abstracta que define el flujo de extraccion hacia Pandas"""

    def __init__(self,file_path: Path, metadata: Optional[Dict[str, Any]] = None) -> None:
        self.file_path = file_path
        self.metadata = metadata or {}

    def validate_source(self) -> None:
        """Verifica que el archivo fuente exista en disco y no este vacio."""
        if not self.file_path.exists():
            raise FileNotFoundError(f"No existe el archivo fuente: {self.file_path}")
        if self.file_path.stat().st_size == 0:
            raise ValueError(f"El archivo fuente esta vacio (0 bytes): {self.file_path}")
        
    @abstractmethod
    def _read_raw(self) -> pd.DataFrame:
        raise NotImplementedError
    
    def extract(self) -> pd.DataFrame:
        self.validate_source()
        df = self._read_raw()
    
        if df.empty:
            raise ValueError(f"La extraccion produjo un DataFrame Vacio para {self.file_path.name}")
        
        df.columns = [str(col).strip() for col in df.columns]

        df = df.copy()
        df["_source_file"] = self.file_path.name
        df["_id_eleccion"] = self.metadata.get("id_eleccion", self.file_path.stem)
        df["_extracted_at"] = datetime.now(timezone.utc).isoformat()

        logger.debug(
            f"Extraido [bold cyan]{self.file_path.name}[/bold cyan]"
            f"{len(df):,} filas x {len(df.columns)} columnas"
        )
        return df