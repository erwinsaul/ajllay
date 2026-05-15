# Ajllay: Análisis Electoral de Bolivia 1979–2025
*Ajllay* (del quechua, *elegir*) es un proyecto de código abierto que busca analizar el comportamiento electoral boliviano desde 1979 hasta 2025. El objetivo es analizar la evolución de la democracia en Bolivia, los datos fueron obtenidos del Atlas Electoral de Bolivia.
## 1. Estructura de Datos
Los datos se encuentran en el directorio `datos/`, estan organizados en archivo `.csv`, segun el tipo de eleccion y los resultados obtenidos:
Por ahora tenemos:
* **EleccionesGenerales/**: Resultados de elecciones de Presidencia y Asamblea Legislativa
* **EleccionesDepartamentales/**: Resultados de elecciones para gobernadores y Asambleas Departamentales
* **EleccionesMunicipales/**: Resultados de Alcaldes y Concejales
* **EleccionesJudiciales/**: Resultados de elecciones para magistrados.
* **Referendos/**: Resultados de consultas populares y constituyentes.

## 2. Diccionario de Datos
La mayoría de los archivos CSV mantienen la siguiente estructura:
- `Codigo DEPARTAMENTO/MUNICIPIO`: Identificadores de los municipios y departamentos
- `Nombre RECINTO/MESA`: Ubicación de los recintos y las mesas de sufragio.
- `Votos VALIDOS`: El conteo de votos válidos por eleccion.
- `Votos BLANCOS / NULOS`: El conteo de votos en blanco o nulo por eleccion.
- `Votos INSCRITOS`: El total de ciudadanos inscritos en la elección.

## 3. Fuente de Información
Los datos provienen del Atlas Electoral de Bolivia.

## 4. Requisitos y Configuración
Para trabahar con estos datos, se requiere:
1. Clonar el repositorio con ´git clone https://github.com/ajllay/ajllay.git´
2. Instalar las dependencias con ´pip install -r requirements.txt´

## 5. Estado del Proyecto
- [x] Recopilacion de Datos
- [] Preparación de Datos
- [] Análisis de Datos
- [] Publicación de Datos
