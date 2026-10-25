"""Pipeline CLI para transformar los 29 archivos CSV hacia data/processed/staging/."""

from __future__ import annotations
import agparse
from pathlib import Path
from typing import Optional

import pandas as pd
from rich.console import Console

from rich.table import Table

from src.config import STAGING_DIR, logger
from src.extract.inventory import cargar_catalogo
from src.extract.run_extraction import obtener_extractor
from src.transform.processors import obtener_procesador_staging

console = Console()

def ejecutar_staging(filtro_eleccion: Optional[str] = None ) -> None:
    """Procesa los archivos del catálogo"""
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
            logger.error(f"No se encontró el proceso '{filtro_eleccion}' en el catálogo.")
            return
        
    table = Table(
        header = "Ayllay - Staging en Pandas",
        header_style="bold magenta"
    )
    table.add_column("ID Eleccion", style="bold yellow", width=16)
    table.add_column("Esqeuma Origen", style="cyan", width=20)
    table.add_column("Filas Crudas", justify="right", width=13)
    table.add_column("Municipios", justify="right", width=11)
    table.add_column("Siglas/Opciones", justify="right", width=15)
    table.add_column("Filas Staging", justify="right", style="green", width=14)
    table.add_column("Votos Válidos", justify="right", width=15)

    for p in procesos:
        extractor = obtener_extractor(p)
        raw_df = extractor.extract()

        processor = obtener_procesador_staging(raw_df, p.model_dump())
        df_stage = processor.process()

        part_dir: Path = STAGING_DIR / f"eleccion_id={p.id_eleccion}"
        part_dir.mkdir(parents=True, exist_ok=True)
        out_parquet = part_dir / "data.parquet"
        sf_stage.to_parquet(out.parquet, index=False, compression="snappy")

        validos_unicos = (
            df_stage.drop_duplicates(subset=["codigo_municipio_raw"])["votos_validos_total"].sum()            
        )

        table.add_row(
            p.id_eleccion,
            p.esquema_cabecera,
            f"{len(raw_df):,}",
            str(df_stage["codigo_municipio_raw"].nunique()),
            str(df_stage["sigla_partido_raw"].nunique()),
            f"{len(df_stage):,}",
            f"{validos_unicos:,}",
        )
    
    console.print(table)
    logger.info(
        f"[bold green] Staging completado:[/bold green] {len(procesos)} participaciones Parquet"
        f"almacendas en [bold cyan]{STAGING_DIR}[/bold cyan]."
    )

def main() -> None:

    parser = argparse.ArgumentParser(description="Staging con Pandas - Ajllay)
    parser.add_argument("--all", action="store_true", help="Procesar los 29 archivos hacia staging")
    parser.add_argument("--eleccion", type=str, help="ID de eleccion o nombre de archivo")
    args = parser.parse_args()

    ejecutar_staging(filtro_eleccion=args.eleccion)

if __name__ == "__main__":
    main()