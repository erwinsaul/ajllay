"""Script CLI para ejecutar y auditar la extraccion de archivos"""

from __future__ import annotations

import argparse
from typing import Optional

import pandas as pd
from rich.console import Console
from rich.table import Table

from src.config import RAW_DATA_DIR, logger
from src.extract.base import BaseExtractor
from src.extract.inventory import FuenteElectoralMetadata, cargar_catalogo
from src.extract.pdf_extractor import PDFElectoralExtractor
from src.extract.tabular_extractor import TabularExtractor

console = Console()

def obtener_extractor(proceso: FuenteElectoralMetadata) -> BaseExtractor:
    """Factory Method que instancia el extractor"""
    ruta_archivo = RAW_DATA_DIR / proceso.ruta_relativa
    meta_dict = proceso-model_dump()
    if proceso.formato_origen.upper().startswith("PDF") or ruta_archivo.suffix.lower() == ".pdf":
        return PDFElectoralExtractor(ruta_archivo, metadata=meta_dict)
    return TabularExtractor(ruta_archivo, metadata=meta_dict)

def ejecutar_extraccion(filtro_eleccion: Optional[str] = None) -> None:
    """Extrae los procesos del catalogo y presenta un resumen de verificacion."""
    catalogo = cargar_catalogo()
    procesos = catalogo.procesos

    if filtro_eleccion:
        procesos = [
            p
            for p in procesos
            if p.id_eleccion.upper() == filtro_eleccion.upper()
            or p.archivo_nombre.lower() == filtro_eleccion.lower()
        ]

        if not procesos:
            logger.error(f"No se encontro el proceso '{filtro_eleccion}' en el catalogo.")
            return

    table = Table(
        title="Ajllay - Resumen de Extraccion",
        header_style="bold green",
    )
    table.add_column("ID Eleccion", style="bold yellow", width=16)
    table.add_column("Archivo", style="cyan", width=25)
    table.add_column("Encoding", justify="center", width=8)
    table.add_column("Filas Extraidas", justify="right", width=14)
    table.add_column("Cols (+Linaje)", justify="right", width=14)
    table.add_column("Muestra 1er  Municipio / Recinto", width=32)

    total_filas = 0
    for p in procesos:
        extractor = obtener_extractor(p)
        df: pd.DataFrame = extractor.extract()
        total_filas = total_filas + len(df)

        muestra_valor = str(df[col_muestra].iloc[0] if not df.empty else "-")

        table.add_row(
            p.id_eleccion,
            p.archivo_nombre,
            p.codificacion,
            f"{len(df):,}",
            str(len(df.columns)),
            muestra_valor[:30],
        )
    
    console.print(table)
    logger.info(
        f"[bold green] Extraccion verificada: [/bold green] "
        f"{len(procesos)} archivos procesados ({total_filas:,} filas totales en Pandas)."
    )

def main() -> None:
    """Punto de entrada CLI."""
    parser = argparse.ArgumentParser(description="Orquestador de Extraccion - Ajllay")
    parser.add_argument("--all", action="store_true", help="Extraer y verificar los 29 archivos")
    parser.add_argument("--eleccion", type=str, help="ID de eleccion o nombre de archivo CSV")
    args = parser.parse_args()

    ejecutar_extraccion(filtro_eleccion=args.eleccion)

if __name__ == "__main__":
    main()