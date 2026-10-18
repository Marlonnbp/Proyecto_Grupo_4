# Proyecto Grupo 4 - SASPe

Simulador en Python de la red de sensores sísmicos del Perú.

## Requisitos
- Python 3.12.10
- Git o GitHub Desktop

## Preparar el entorno (Windows, PowerShell)
1. Clonar el repositorio.
2. Crear el entorno virtual: `py -3.12 -m venv .venv`
3. Activarlo: `.venv\Scripts\activate`
   Si sale un error de scripts deshabilitados: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`
4. Instalar las librerías: `pip install -r requirements.txt`
5. Correr las pruebas: `python -m unittest discover pruebas`

## Estructura
- `codigo_fuente/`: código del programa, un archivo por estructura o algoritmo.
- `pruebas/`: pruebas unitarias.
- `datos/`: archivos CSV y modelo guardado.

## Reglas de trabajo
- Una rama por integrante.
- Nadie sube cambios directo a `main`.
- Los cambios entran por pull request, revisado por otro integrante.