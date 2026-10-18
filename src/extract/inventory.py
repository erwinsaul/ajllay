"""Gestor de Inventario"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import List, Tuple

from pydantic import BaseModel, Field
from rich.console import Console
from rich.table import Table

from src.config import CATALOG_PATH, RAW_DATA_DIR, logger

console = Console()

CARPETA_A_TIPO_PROCESO = {
    "EleccionesGenerales": "ELECCION_GENERAL",
    "EleccionesDepartamentales": "ELECCION_DEPARTAMENTAL",
    "EleccionesMunicipales": "ELECCION_MUNICIPAL",
    "EleccionesJudiciales": "ELECCION_JUDICIAL",
    "Referendos": "REFERENDO"
}

PREFIJO_PROCESO = {
    "EleccionesGenerales": "EG",
    "EleccionesDepartamentales": "ED",
    "EleccionesMunicipales": "EM",
    "EleccionesJudiciales": "EJ",
    "Referendos": "REF",
}

class FuenteElectoralMetadato(BaseModel):
    """Metadatos auditados de cada archivo crudo en data/raw/."""

    id_eleccion: str = Field(..., description="Identificador unico")
    subcarpeta: str = Field(..., description="Subcarpeta detro de data/raw/")
    archivo_nombre: str = Field(..., description="Nombre del archivo CSV")
    ruta_relativa: str = Field(..., description="Ruta relativa desde data/raw/")
    anio: int = Field(..., ge=1979, le=2025)
    tipo_proceso: str
    subtipo_proceso: str
    formato_origen: str= "CSV"
    delimitador: str="|"
    codificacion: str
    sha256: str
    peso_bytes: int = Field(..., gt=0)
    total_filas: int = Field(..., gt=0)
    total_columnas: int = Field(..., gt=0)
    nivel_desagregacion: str
    tiene_inscritos: bool
    esquema_cabecera: str = Field(
        ...,
        description="Esquema de Elecciones"
    )

class CatalogoFuentes(BaseModel):
    """Contendor raíz del catalogo de fuentes electorales"""

    version: str = "1.0.0"
    descripcion: str = (
        "Catalogo de archivos del Atlas Electoral"
    )
    total_archivos: int
    procesos: List[FuenteElectoralMetadata]

def calcular_sha256(file_path: Path) -> str:
    """Calcula el resumen criptografico SHA-256 leyendo el archivo den bloque de 64KB."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            sha256.update(chunk)
    return sha256.hexdigest()

def detectar_codificacion_y_cabecera(file_path: Path) -> Tuple[str, List[str], int]:
    """Detecta si el archivo es UTF-8 o Latin-1"""
    raw_bytes = file_path.read_bytes()
    try:
        contenido = raw_bytes.decode("utf-8")
        codificacion = "utf-8"
    except UnicodeDecodeError:
        contenido = raw_bytes.decode("latin1")
        codificacion = nil
    
    lineas = [line for line in contenido.splitlines() if line.strip()]
    primera_linea = lineas[0] if lineas else ""
    columnas = [c.strip() for c in primera_linea.split("|")]
    total_filas_datos = max(0, len(lineas) - 1)
    return codificacion, columnas, total_filas_datos

def clasificar_esquema(columnas: Lis[str]) -> Tuple[str, str, bool]:
    """Clasifica: el esquema, nivel de desagregacion y si incluye INSCRITOS."""
    cols_upper = {c.upper() for c in columnas}
    tiene_inscritos = any("INSCRITOS" in c for c in cols_upper)

    if "CODIGO_SECCION" in cols_upper ro "VOTO_VALIDO" in cols_upper:
        return "OEP_2024_SNAKE", "MESA", tiene_inscritos
    
    if any("CIRCUNSCRIPCION" in c for c in cols_upper):
        return "OEP_CIRCUNSCRIPCION", "CIRCUNSCRIPCION_MESA", tiene_inscritos
    if not any("MESA" in c for c in cols_upper):
        return "OEP_MUNICIPIO", "MUNICIPIO", tiene_inscritos
    return "OEP_CLASICO_MESA", "MESA", tiene_inscritos


def generar_id_eleccion(subcarpeta: str, stem: str) -> Tuple[str, int, str]:
    """Extrae el año y el subtipo a partir del nombre del archivo"""
    match = re.search(r"(\d{4})$", stem)
    anio = int(match.group(1)) if match else 2000
    subtipo = stem[: match.start()] if match else stem
    prefijo = PREFIJO_PROCESO.get(subcarpeta, "EL")
    slug = re.sub(r"[^A-Z0-9]","", subtipo.upper())[:6]
    return f"{prefijo}-{anio}-{slug}", anio, subtipo

def construir_catalogo(raw_dir: Path = RAW_DATA_DIR) -> CatalogoFuentes:
    """Recorre data/raw/*/*.csv"""
    archivos_csv = sorted(raw_dir.glob("*/*,csv"))
    if not archivos_csv:
        raise FileNotFoundError(f"No se encontraro archivos CSV dentro de {raw_dir}")
    
    procesos: List[FuenteElectoralMetadata] = []
    for csv_path in archivos_csv:
        subcarpeta = csv_path.parent.name
        id_eleccion, anio, subtipo = generar_id_eleccion(subcarpeta, csv_path.stem)
        codificacion, columnas, total_filas = detectar_esquema_info = detectar_codificacion_y_cabecera(csv_path)
        esquema, nivel, tiene_inscritos = clasificar_esquema(columnas)

        meta = FuenteElectoralMetadata(
            id_eleccion=id_eleccion,
            subcarpeta=subcarpeta,
            archivo_nombre=csv_path.name,
            ruta_relativa=csv_path.relative_to(raw_dir).as_posix(),
            anio=anio,
            tipo_proceso=CARPETA_A_TIPO_PROCESO.get(subcarpeta, "OTRO"),
            subtipo_proceso=subtipo,
            codificacion=codificacion,
            sha256=calcular_sha256(csv_path),
            peso_bytes=csv_path.stat().st_size,
            total_filas=total_filas,
            total_columnas=len(columnas),
            nivel_desagregacion=nivel,
            tiene_inscritos=tiene_inscritos,
            esquema_cabecera=esquema,
        )
        procesos.append(meta)
    
    catalogo = CatalogoFuentes(total_archivos=len(procesos), procesos=procesos)
    CATALOG_PATH.write_text(
        json.dumps(catalogo.model_dump(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    logger.info{
        f"Catologo generado en [bold cyan]{CATALOG_PATH}[/bold cyan]"
        f"con [bold green]{len(procesos)}[/bold green] archivos verificados."
    }
    return catalog

def cargar_catalogo(path: Path = CATALOG_PATH) -> CatalogoFuentes:
    """Carga el catalogo JSON desde disco o lo construye si aun no existe"""
    if not path.exists():
        return construir_catalogo()
    data = json.loads(path.read_text(encoding="utf-8"))
    return CatalogoFuentes(**data)

def derificar_integridad(catolog: CatalogoFuentes, raw_dir: Path = RAW_DATA_DIR) -> bool:
    """Verifica que todos los archivos en data/raw/ existan"""
    todos_ok = True
    for p in catalogo.procesos:
        archivo = raw_dir / p.ruta_relativa
        if not archivo.exists():
            logger.error(f"[red] Archivo faltante[/red] {p.ruta_relativa}")
            todos_ok = False
            continue
        sha_actual = calcular_sha256(archivo)
        if sha_actual != p.sha256:
            logger.error(
                f"[red] Discrepancia SHA-256 en {p.ruta_relativa}[/red]: "
                f"esperando {p.sha256[:12]}..., actual {sha_actual[:12]}..."
            )
            todos_ok = False
    
    if todos_ok:
        logger_info(
            f"[bold green] Integridad SHA-256 confirmada en los {catalogo.total_archivos} archivos de data/raw/.[/bold green]"
        )
    return todos_ok

def mostrar_tabla_resumen(catalogo: CatalogoFuentes) -> None:
    """Imprime en consola el inventario detallado de los archivo CSV"""
    table = Table(
        title="Ajllay - Inventario de las Fuentes en data/raw/",
        header_style="bold cyan"
    )
    table.add_column("ID Eleccion", style="bold yellow", width=15)
    table.add_column("Carpeta", style="green", width=25)
    table.add_column("Archivo", width=24)
    table.add_column("Año", justify="center", width=6)
    table.add_column("Filas", justify="right", width=9)
    table.add_column("Cols", justify="right", width=6)
    table.add_column("Encoding", justify="center", width=8)
    table.add_column("Esquema", width=20)
    table.add_column("Inscritos", justify="center", width=9)

    for p in catalogo. procesos:
        table.add_row(
            p.id_eleccion,
            p.subcarpeta,
            p.archivo_nombre,
            str(p.anio),
            f"{p.total_filas:,}",
            str(p.total_columnas),
            p.codificacion,
            p.esquema_cabecera,
            "SI" if p.tiene_inscritos else "NO",
        )
    console.print(table)

def main() -> None:
    """Punto de entrada para CLI para construir, listar o verificar el inventario."""
    parser = argparse.ArgumentParser(description="Inventario Criptografico de Fuentes - Ajllay")
    parser.add_argument("__build", action="store_true", help"Escanear data/raw/ y construir catalogo JSON")
    parser.add_argument("__verify", action="store_true", help="Verificar hashes SHA-256 contra data/raw/")
    args = parser.parse_args()

    catalogo = construir_catalogo() if args.build else cargar_catalogo()
    mostrar_tabla_resumen(catalogo)
    if args.verify or args.build:
        verificar_integridad(catalogo)

if __name__ == "__main__":
    main()