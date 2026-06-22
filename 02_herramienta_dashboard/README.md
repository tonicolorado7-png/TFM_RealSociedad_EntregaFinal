TFM - Herramienta de análisis de juego aplicada a la Real Sociedad

Este repositorio contiene la herramienta desarrollada para el Trabajo Fin de Máster en Big Data Deportivo.

El proyecto consiste en una aplicación interactiva de análisis de juego aplicada a la Real Sociedad durante la temporada 2025/2026.

El objetivo principal es transformar datos deportivos en información visual e interpretable para un contexto técnico, permitiendo analizar el modelo de juego del equipo, su contexto competitivo, jugadores, rivales e informes pre-partido y post-partido.

Contenido de la carpeta

La carpeta 02_herramienta_dashboard contiene los archivos necesarios para ejecutar la herramienta final:

app_dash_REAL_FINAL.py: archivo principal de la aplicación Dash.
data/: carpeta con los archivos CSV procesados utilizados por la herramienta.
assets/: carpeta con recursos visuales, como el escudo de la Real Sociedad.
requirements.txt: librerías necesarias para ejecutar la aplicación.
README.md: explicación del proyecto y modo de uso.
Módulos principales de la herramienta

La herramienta está organizada en diferentes bloques de análisis:

Contexto competitivo de la Real Sociedad.
Modelo de juego del equipo.
Análisis de KPIs e índices por fases del juego.
Análisis de jugadores de la Real Sociedad.
Comparación de perfiles de jugadores de LaLiga.
Análisis de rivales.
Informes pre-partido y post-partido de cinco encuentros seleccionados.
Datos utilizados

Los datos han sido tratados y transformados previamente para generar métricas interpretables.

La carpeta data/ contiene los archivos CSV necesarios para alimentar los diferentes módulos del dashboard.

Entre los datos incluidos se encuentran:

KPIs de equipo.
Métricas de jugadores.
Rankings internos y comparativos.
Información de rivales.
Datos de partidos seleccionados.
Métricas pre-partido y post-partido.
Cómo ejecutar la herramienta

Primero hay que instalar las librerías necesarias:

pip install -r requirements.txt

Después, ejecutar el archivo principal:

python app_dash_REAL_FINAL.py

Una vez ejecutado, la herramienta se abre en el navegador en:

http://127.0.0.1:8051
Librerías principales utilizadas

La herramienta se ha desarrollado con Python y utiliza principalmente:

Dash
Plotly
Pandas
NumPy

Estas librerías permiten construir la aplicación interactiva, cargar datos procesados y generar visualizaciones.

Uso de la herramienta

La herramienta sirve como apoyo al análisis técnico de la Real Sociedad.

Permite consultar de forma visual:

Contexto competitivo.
Modelo de juego.
Fortalezas y alertas del equipo.
Rendimiento de jugadores.
Comparación de perfiles de LaLiga.
Perfil táctico de rivales.
Informes pre-partido y post-partido.
Informes pre-partido y post-partido

El informe pre-partido permite identificar el perfil del rival, sus principales amenazas y posibles planes de actuación.

El informe post-partido permite comparar lo previsto con lo ocurrido realmente en el partido, interpretando métricas como posesión, xG, tiros, ocasiones, presencia en área, rendimiento del portero y resistencia defensiva.

Autor

Antonio Martín Colorado.

Trabajo Fin de Máster - Máster en Big Data Deportivo.

Temporada analizada: 2025/2026.