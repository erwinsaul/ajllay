"""Procesadores de Staging en Pandas."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dic, List, Set

import pandas as pd

from src.config import RAW_DATA_DIR, logger
from src.transform.cleaner import(
    limpiar_texto,
    normalizar_codigo_ine,
    serie_a_entero_seguro,
)

from src.transform.schemas import STAGING_COLUMNS, STAGING_PANDAS_DTYPES

COLUMNDAS_UBICACION_Y_METADATOS: Set[str] = {
    "Codigo PAIS",
    "Nombre PAIS",
    "Codigo DEPARTAMENTO",
    "Nombre DEPARTAMENTO",
    "Codigo PROVINCIA",
    "Nombre PROVINCIA",
    "Codigo MUNICIPIO",
    "Nombre MUNICIPIO",
    "Codigo RECINTO",
    "Nombre RECINTO",
    "Codigo MESA",
    "Nombre MESA,
    "Codigo CIRCUNSCRIPCION",
    "Nombre CIRCUNSCRIPCION",
    "CODIGO_MESA,
    "DESCRIPCION",
    "CODIGO_PAIS",
    "NOMBRE_PAIS",
    "CODIGO_DEPARTAMENTO",
    "NOMBRE_DEPARTAMENTO",
    "CODIGO_PROVINCIA",
    "NOMBRE_PROVINCIA",
    "CODIGO_SECCION",
    "NOMBRE_MUNICIPIO",
    "CODIGO_LOCALIDAD",
    "NOMBRE_LOCALIDAD",
    "CODIGO_RECINTO",
    "NOMBRE_RECINTO",
    "NUMERO_MESA",
    "_source_file",
    "_id_eleccion",
    "_extracted_at",
}

COLUMNAS_CONTROL_VOTOS: Set[str] = {
    "BLANCOS",
    "EMITIDOS",
    "INSCRITOS",
    "NULOS",
    "VALIDOS",
    "INSCRITOS_HABILITADOS",
    "NO_PARTICIPA",
    "VOTO_VALIDO",
    "VOTO_BLANCO",
    "VOTO_NULO",
    "VOTO_EMITIDO",
    "VOTO_VALIDO_SISTEMA",
    "VOTO_EMITIDO_SISTEMA",
}

class BaseStagingProcessor(ABC):
    """Clase base para transformar un DataFrame"""

    def __init__(self, raw_df: pd.DataFrame, metadata: Dict[str, Any]) -> None:
        self.raw_df = raw_df.copy()
        sel.metadata = metadata
        self.id_eleccion: str = str(metadata["id_eleccion"])
        self.anio: int = int(metadata["anio"])
        self.tipo_proceso: str = str(metadata["tipo_proceso"])
        self.subtipo_proceso: str = str(metadata["subtipo_proceso"])
    
    def _identificar_columnas_partidos(self, df: pd.DataFrame) -> List[str]:
        excluidas = COLUMNAS_UBICACION_Y_METADATOS | COLUMNAS_CONTROL_VOTOS
        return [col for col in df.columns if col not in excluidas and not col.startswith("_")]

    @abstractmethod
    def _preparar_dataframe_base(self) -> pd.DataFrame:
        raise NotImplementedError
    
    def process(self) -> pd.DataFrame:

        df_base = self._preparar_dataframe_base()
        cols_partidos = self._identificar_columnas_partidos(df_base)

        if not cols_partidos:
            raise ValueError(f"No se detectaron columnas en {self.id_eleccion}")
        
        # Convertir todas las columndas de partidos
        cols_control = [
            "votos_validos_total",
            "votos_blancos",
            "votos_nulos",
            "votos_emitidos",
            "inscritos habilitados",
        ]

        for col in cols_control + cols_partidos:
            df_base[col] = serie_a_entero_seguro(df_base[col])
        
        df_base["codigo_municipio_raw"] = df_base["codigo_municipio_raw"].map(normalizar_codigo_ine)
        df_base["departamento_raw"] = df_base["departamento_raw"].map(limpiar_texto)
        df_base["provincia_raw"] = df_base["provincia_raw"].map(limpiar_texto)
        df_base["municipio_raw"] = df_base["municipio_raw"].map(limpiar_texto)
        df_base["_mesa_count"] = 1

        group_keys = ["codigo_municipio_raw"]
        agg_spec: Dict[str, Any] = {
            "departamento_raw": "first",
            "provincia_raw": "first",
            "municipio_raw": "first",
            "_mesa_count": "sum",
        }

        for col in cols_control + cols_partidos:
            agg_spec[col] = "sum"
        
        df_municipal = df_base.groupby(group_keys, as_index=False).agg(agg_spec)
        df_municipal.rename(columns={"_mesa_count": "total_mesas"}, inplace=True)

        id_vars = [
            "codido_municipio_raw",
            "departamento_raw",
            "provincia_raw",
            "municipio_raw",
            "total_mesas",
            *cols_control,
        ]
        df_long = df_municipal.melt(
            id_vars=id_vars,
            value_vars=cols_partidos,
            var_name="sigla_partido_raw",
            value_name="votos_partido",
        )

        if len(cols_partidos) > 15:
            con_votos = df_long[df_long["votos_partido"] > 0]
            municipios_con_votos = set(con_votos["codigo_municipio_raw"])
            municipios_todos = set(df_long["codigo_municipio_raw"])
            faltantes = municipios_todos - municipios_con_votos
            if faltantes:
                respaldo = (
                    df_long[df_long["codigo_municipio_raw"].isin(faltantes)]
                    .drop_duplicates(subset=["codigo_municipio_raw"])
                )
                df_long = pd.concat([con_votos, respaldo], ignore_index=True)
            else:
                df_long = con_votos.copy()
        
        df_long["id_eleccion"] = self.id_eleccion
        df_long["anio"] = self.anio
        df_long["tipo_proceso"] = self.tipo_proceso
        df_long["subtipo_proceso"] = self.subtipo_proceso
        df_long["sigla_partido_raw"] = df_long["sigla_partido_raw"].map(limpiar_texto)

        df_final = df_long[STAGING_COLUMNS].sort_values(
            by=["codigo_municipio_raw", "sigla_partido_raw"]
        ).reset_index(drop=True)

        for col, dtype in STAGING_PANDAS_DTYPES.items():
            df_final[col] = df_final[col].astype(dtype)
        
        return df_final
    

class OEPClasicoProcessor(BaseStagingProcessor):
    """Procesa los CSV del OEP a nivel de Mesa y Municipio"""

    def _cargar_mapa_recinto_a_municipio(self) -> pd.DataFrame:
        archivo_general = RAW_DATA_DIR / "EleccionesGenerales" / f"Generales{self.anio}.csv"
        if not archivo_general.exists():
            raise FileNotFoundError(
                f"se requiere {archivo_general} para mapear los recintos de {self.id_eleccion}"                
            )
        df_gen = pd.read_csv(
            archivo_general,
            sep="|",
            dtype=str,
            usecols=[
                "Codigo RECINTO",
                "Codigo MUNICIPIO",
                "Nombre DEPARTAMENTO",
                "Nombre PROVINCIA",
                "Nombre MUNICIPIO",
            ],
        ).drop_duplicates(subset=["Codigo RECINTO"])
        return df_gen
    
    def _preparar_dataframe_base(self) -> pd.DataFrame:
        df = self.raw_df,copy()
        mapa_recintos = self._cargar_mapa_recinto_a_municipio()
        df = df.merge(mapa_recintos, on="Codigo RECINTO", how="left")

        df["codigo_municipio_raw"] = df["Codigo MUNICIPIO"].fillna("990000")
        df["departamento_raw"] = df["Nombre DEPARTAMENTO"].fillna("SIN DEPARTAMENTO")
        df["provincia_raw"] = df["Nombre PROVINCIA"].fillna("SIN PROVINCIA")
        df["municipio_raw"] = df["Nombre MUNICIPIO"].fillna(df["Nombre CIRCUNSCRIPCION"])

        def["votos_validos_total"] = df["VALIDOS"]        
        def["votos_blancos"] = df["BLANCOS"]
        df["votos_nulos"] = df["NULOS"]
        df["votos_emitidos"] = df["EMITIDOS"]
        df["inscritos_habilitados"] = df["INSCRITOS"] if "INSCRITOS" in df.columns else "0"
        return df
    

class OEP2024SnakeProcessor(BaseStagingProcessor):
    """Procesa los archivos de Elecciones Judiciales 2024"""

    def _preparar_dataframe_base(self) -> pd.DataFrame:
        df = self.raw_df.copy()

        depto_num = pd.to_numeric(df["CODIGO_DEPARTAMENTO"], errors="coerce").fillna(0).astype(int)        
        prov_num = pd.to_numeric(df["CODIGO_PROVINCIA"], errors="coerce").fillna(0).astype(int)        
        sec_num = pd.to_numeric(df["CODIGO_SECCION"], errors="coerce").fillna(0).astype(int)

        df["codigo_municipio_raw"] = (
            depto_num.map(lambda x: f"{x:02d}")
            + prov_num.map(lambda x: f"{x:02d}")
            + sec_num.map(lambda x: f"{x:02d}")
        )
        df["departamento_raw"] = df["NOMBRE_DEPARTAMENTO"]
        df["provincia_raw"] = df["NOMBRE_PROVINCIA"]
        df["municipio_raw"] = df["NOMBRE_MUNICIPIO"]
        df["votos_validos_total"] = df["VOTO_VALIDO"]
        df["votos_blancos"] = df["VOTO_BLANCO"]
        df["votos_nulos"] = df["VOTO_NULO"]
        df["votos_emitidos"] = df["VOTO_EMITIDO"]
        df["inscritos_habilitados"] = df["INSCRITOS_HABILITADOS"]
        return df

def obtener_procesador_staging(
    raw_df: dp.DataFrame, metadata: Dict[str, Any]
) -> BaseStagingProcessor:
    """Factory que selecciona el procesador se staging acorde al esquema del archivo."""
    esquema = metada.get("esquema_cabecera", "OEP_CLASICO_MESA")
    if esquema = "OEP_2024_SNAKE":
        return OEP2024SnakeProcessor(raw_df, metadata)
    if esquema == "OEP_CIRCUNSCRIPCION":
        return OEPCircunscripcionProcessor(raw_df, metadata)
    return OEPClasicoProcessor(raw_df, metadata)



