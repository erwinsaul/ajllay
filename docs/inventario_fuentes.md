# Inventario de Fuentes y Mapeo de Columnas
En este documento se detallan las fuentes de datos utilizadas en el proyecto, así como el mapeo de las columnas de los archivos CSV.

## 1. Comparativa de Cabeceras (Mapping)

| Identificador | Elecciones Generales | Elecciones Departamentales | Elecciones Municipales | Elecciones Judiciales | Referendos |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **ID Geográfico** | Codigo Municipio | Codigo Municipio | Codigo Municipio | Codigo Municipio | Nombre Municipio |
| **Ubicacion** | Nombre Recinto/Mesa | Nombre Recinto/Mesa | Nombre Recinto/Mesa | Nombre Recinto/Mesa | Nombre Recinto/Mesa |
| ** Participación** | Inscritos | Inscritos | Inscritos / Emitidos | Inscritos | Inscritos |
| **Votos Válidos** | Validos | Validos | Validos | Validos | SI / NO |
| **Votos Nulos** | Nulos | Nulos | Nulos | Nulos | Nulos |
| **Votos en Blanco** | Blancos | Blancos | Blancos | Blancos | Blancos |

## 2. Identificación de Entidades

Se puede identificar tres entidades principales para la base de datos:
1. **Geografía**: (País, Departamento, Provincia, Municipio, Mesa, Recinto)
2. **Procesos**: (Año, Tipo de Elección, Sigla de la Elección)
3. **Resultados**: (ID_Mesa, Sigla_Partido, Cantidad_Votos)

## 3. Observaciones
- **Variabilidad de Partidos:** Los nombres de las columnas de partidos plíticos cambian en cada elección.
- **Nivel de Granularidad**: Todos los archvios parecen llegar al nivel de **Mesa**.
- **Referendos**: Tiene una estructura diferente a las demas elecciones.