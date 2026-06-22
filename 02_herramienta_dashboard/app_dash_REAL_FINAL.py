# ============================================================
# DASH TFM — REAL SOCIEDAD
# Análisis de juego | Temporada 2025/26
# Versión visual PRO — modelo + 5 partidos + rival + metodología
# ============================================================

import os
import numpy as np
import pandas as pd

from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import plotly.graph_objects as go


# ============================================================
# RUTAS
# ============================================================

BASE_APP = os.path.dirname(os.path.abspath(__file__))
BASE_TFM = os.path.dirname(BASE_APP)

CARPETA_DATOS = os.path.join(BASE_APP, "data")
CARPETA_ASSETS = os.path.join(BASE_APP, "assets")
CARPETA_CONFIG = os.path.join(BASE_APP, "config")

RUTA_DASHBOARD = os.path.join(CARPETA_DATOS, "datos_dashboard_real_sociedad.csv")
RUTA_MODELO_5 = os.path.join(CARPETA_DATOS, "tabla_modelo_real_sociedad.csv")
RUTA_CONTEXTO_30 = os.path.join(CARPETA_DATOS, "contexto_30_partidos_real_sociedad.csv")
RUTA_COMPARATIVA_5_30 = os.path.join(CARPETA_DATOS, "comparativa_5_partidos_vs_media_30.csv")
RUTA_RESUMEN_PROFUNDO = os.path.join(CARPETA_DATOS, "resumen_analisis_profundo_5_partidos.csv")
RUTA_LECTURA_5 = os.path.join(CARPETA_DATOS, "lectura_contextual_5_partidos.csv")
RUTA_TABLA_FICHAS = os.path.join(CARPETA_DATOS, "tabla_resumen_fichas_partido.csv")

RUTA_PERFIL_RIVALES = os.path.join(CARPETA_DATOS, "perfil_tactico_rivales_5_partidos.csv")
RUTA_INTERPRETACION_RIVALES = os.path.join(CARPETA_DATOS, "interpretacion_tactica_rivales_5_partidos.csv")
RUTA_RESUMEN_PREPARTIDO = os.path.join(CARPETA_DATOS, "resumen_prepartido_rivales_5_partidos.csv")

RUTA_ESCUDO = "/assets/escudo_real_sociedad.png?v=4"


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def leer_csv_seguro(ruta):
    if not os.path.exists(ruta):
        return pd.DataFrame()

    for enc in ["utf-8-sig", "utf-8", "latin1"]:
        try:
            return pd.read_csv(ruta, encoding=enc)
        except Exception:
            pass

    try:
        return pd.read_csv(ruta)
    except Exception:
        return pd.DataFrame()


def buscar_columna(df, opciones):
    for col in opciones:
        if col in df.columns:
            return col
    return None


def num(x, default=0):
    try:
        valor = pd.to_numeric(x, errors="coerce")
        if pd.isna(valor):
            return default
        return float(valor)
    except Exception:
        return default


def serie_num(df, col):
    if col is None or col not in df.columns:
        return pd.Series(dtype=float)
    return pd.to_numeric(df[col], errors="coerce")


def formato_valor(valor, decimales=2, sufijo=""):
    try:
        valor = float(valor)
        if abs(valor - round(valor)) < 0.001:
            return f"{int(round(valor))}{sufijo}"
        return f"{valor:.{decimales}f}{sufijo}"
    except Exception:
        return f"{valor}"


def texto_corto(valor, max_len=260):
    if pd.isna(valor):
        return ""
    valor = str(valor)
    if len(valor) <= max_len:
        return valor
    return valor[:max_len] + "..."


def limpiar_nombre_rival(partido):
    partido = str(partido)
    partido = partido.replace("Real Sociedad vs ", "")
    partido = partido.replace("Real Sociedad - ", "")
    partido = partido.replace(" vs Real Sociedad", "")
    partido = partido.replace(" - Real Sociedad", "")
    return partido.strip()


def estado_carga(nombre, df):
    if df.empty:
        return f"⚠️ {nombre}: no cargado"
    return f"✅ {nombre}: cargado ({df.shape[0]} filas, {df.shape[1]} columnas)"


# ============================================================
# CARGA DE DATOS
# ============================================================

df_dashboard = leer_csv_seguro(RUTA_DASHBOARD)
df_modelo_5 = leer_csv_seguro(RUTA_MODELO_5)
df_contexto_30 = leer_csv_seguro(RUTA_CONTEXTO_30)
df_comparativa_5_30 = leer_csv_seguro(RUTA_COMPARATIVA_5_30)
df_resumen_profundo = leer_csv_seguro(RUTA_RESUMEN_PROFUNDO)
df_lectura_5 = leer_csv_seguro(RUTA_LECTURA_5)
df_tabla_fichas = leer_csv_seguro(RUTA_TABLA_FICHAS)

df_perfil_rivales = leer_csv_seguro(RUTA_PERFIL_RIVALES)
df_interpretacion_rivales = leer_csv_seguro(RUTA_INTERPRETACION_RIVALES)
df_resumen_prepartido = leer_csv_seguro(RUTA_RESUMEN_PREPARTIDO)

# ============================================================
# PRE/POST FINAL 5 PARTIDOS TFM
# ============================================================

RUTA_PREPOST_FINAL_TFM = os.path.join(os.path.dirname(__file__), "data", "prepost_5_partidos_tfm_final.csv")
df_prepost_final_tfm = leer_csv_seguro(RUTA_PREPOST_FINAL_TFM)




# ============================================================
# DATOS NUEVOS NOTEBOOK 2 — JUGADORES REAL SOCIEDAD / LALIGA
# ============================================================

BASE_TFM_ABS = BASE_TFM
CARPETA_APP_ABS = BASE_APP
CARPETA_DATA_APP_ABS = CARPETA_DATOS
CARPETA_CONFIG_APP_ABS = CARPETA_CONFIG
CARPETA_DATOS_PROCESADOS_ABS = os.path.join(BASE_TFM_ABS, "04_datosprocesados")
CARPETA_GRAFICOS_TFM_ABS = CARPETA_DATOS

def buscar_csv_tfm(grupos_tokens):
    """
    Busca un CSV dentro de carpetas seguras del TFM.
    grupos_tokens: lista de listas. Ejemplo:
    [["jugadores", "real", "sociedad"], ["ranking", "total", "jugadores"]]
    """
    carpetas = [
        CARPETA_DATA_APP_ABS,
        CARPETA_CONFIG_APP_ABS,
        CARPETA_DATOS_PROCESADOS_ABS,
        CARPETA_GRAFICOS_TFM_ABS,
        BASE_TFM_ABS
    ]

    candidatos = []

    for carpeta in carpetas:
        if not os.path.exists(carpeta):
            continue

        for root, dirs, files in os.walk(carpeta):
            # evitar carpetas pesadas o de backups
            root_low = root.lower()
            if "backups_app" in root_low or ".ipynb_checkpoints" in root_low:
                continue

            for f in files:
                if not f.lower().endswith(".csv"):
                    continue

                nombre = f.lower()
                ruta = os.path.join(root, f)

                for tokens in grupos_tokens:
                    ok = True
                    for t in tokens:
                        if str(t).lower() not in nombre:
                            ok = False
                            break
                    if ok:
                        candidatos.append(ruta)

    if not candidatos:
        return None

    # preferimos archivos de dashboard/data o nombres más claros
    candidatos = sorted(
        candidatos,
        key=lambda x: (
            0 if "dashboard_app/data" in x else 1,
            len(os.path.basename(x))
        )
    )
    return candidatos[0]


RUTA_JUGADORES_RS_N2 = buscar_csv_tfm([
    ["jugadores", "real", "sociedad", "dashboard"],
    ["jugadores", "real", "sociedad"],
    ["ranking", "total", "jugadores", "real", "sociedad"],
    ["real_sociedad", "jugadores"],
])

RUTA_JUGADORES_LALIGA_N2 = buscar_csv_tfm([
    ["jugadores", "laliga", "dashboard"],
    ["jugadores", "laliga"],
    ["ranking", "jugadores", "laliga"],
    ["df_jugadores_laliga"],
])


# Forzar CSV bueno de jugadores Real Sociedad generado para la app
RUTA_RS_FORZADA_APP = os.path.join(CARPETA_DATOS, "jugadores_real_sociedad_app.csv")
if os.path.exists(RUTA_RS_FORZADA_APP):
    RUTA_JUGADORES_RS_N2 = RUTA_RS_FORZADA_APP

df_jugadores_rs = leer_csv_seguro(RUTA_JUGADORES_RS_N2) if RUTA_JUGADORES_RS_N2 else pd.DataFrame()

df_jugadores_laliga = leer_csv_seguro(RUTA_JUGADORES_LALIGA_N2) if RUTA_JUGADORES_LALIGA_N2 else pd.DataFrame()

# Si no se encuentra un CSV específico de la Real, filtramos de LaLiga
if df_jugadores_rs.empty and not df_jugadores_laliga.empty:
    col_equipo_tmp = buscar_columna(df_jugadores_laliga, ["equipo", "team", "Equipo", "Team"])
    if col_equipo_tmp:
        df_jugadores_rs = df_jugadores_laliga[
            df_jugadores_laliga[col_equipo_tmp].astype(str).str.contains("Real Sociedad", case=False, na=False)
        ].copy()


def preparar_df_jugadores(df):
    df = df.copy()

    if df.empty:
        return df

    col_nombre = buscar_columna(df, ["jugador", "player", "name", "nombre", "Player", "Name"])
    col_equipo = buscar_columna(df, ["equipo", "team", "Equipo", "Team"])
    col_posicion = buscar_columna(df, ["position", "posicion", "posición", "Position", "demarcacion", "demarcación"])
    col_minutos = buscar_columna(df, ["minutos", "minutes", "Minutes", "mins"])
    col_partidos = buscar_columna(df, ["partidos", "matches", "appearances", "Apps"])
    col_total = buscar_columna(df, ["indice_total_jugador", "indice_total", "indice_global", "score_total", "total_score"])
    col_of = buscar_columna(df, ["indice_ofensivo", "indice_amenaza", "ofensivo", "attacking_score"])
    col_prog = buscar_columna(df, ["indice_progresion", "indice_progresión", "progresion", "progression_score"])
    col_def = buscar_columna(df, ["indice_defensivo", "defensivo", "defensive_score"])

    if col_nombre and col_nombre != "jugador_app":
        df["jugador_app"] = df[col_nombre].astype(str)
    elif "jugador_app" not in df.columns:
        df["jugador_app"] = [f"Jugador {i+1}" for i in range(len(df))]

    if col_equipo and col_equipo != "equipo_app":
        df["equipo_app"] = df[col_equipo].astype(str)
    elif "equipo_app" not in df.columns:
        df["equipo_app"] = "No disponible"

    if col_posicion and col_posicion != "posicion_app":
        df["posicion_app"] = df[col_posicion].astype(str)
    elif "posicion_app" not in df.columns:
        df["posicion_app"] = "Sin posición"

    if col_minutos:
        df["minutos_app"] = pd.to_numeric(df[col_minutos], errors="coerce").fillna(0)
    else:
        df["minutos_app"] = 0

    if col_partidos:
        df["partidos_app"] = pd.to_numeric(df[col_partidos], errors="coerce").fillna(0)
    else:
        df["partidos_app"] = 0

    if col_total:
        df["indice_total_app"] = pd.to_numeric(df[col_total], errors="coerce").fillna(0)
    else:
        # si no existe índice total, lo aproximamos con lo disponible
        posibles = []
        for c in [col_of, col_prog, col_def]:
            if c:
                posibles.append(pd.to_numeric(df[c], errors="coerce").fillna(0))
        if posibles:
            df["indice_total_app"] = sum(posibles) / len(posibles)
        else:
            df["indice_total_app"] = 0

    if col_of:
        df["indice_ofensivo_app"] = pd.to_numeric(df[col_of], errors="coerce").fillna(0)
    else:
        df["indice_ofensivo_app"] = 0

    if col_prog:
        df["indice_progresion_app"] = pd.to_numeric(df[col_prog], errors="coerce").fillna(0)
    else:
        df["indice_progresion_app"] = 0

    if col_def:
        df["indice_defensivo_app"] = pd.to_numeric(df[col_def], errors="coerce").fillna(0)
    else:
        df["indice_defensivo_app"] = 0

    return df


df_jugadores_rs = preparar_df_jugadores(df_jugadores_rs)
df_jugadores_laliga = preparar_df_jugadores(df_jugadores_laliga)

# Forzar nombre de equipo en la pestaña de jugadores Real Sociedad
if not df_jugadores_rs.empty:
    df_jugadores_rs["equipo_app"] = "Real Sociedad"




# ============================================================
# SELECCIÓN DE DATAFRAME BASE DE 5 PARTIDOS
# ============================================================

if not df_dashboard.empty:
    df_partidos = df_dashboard.copy()
elif not df_modelo_5.empty:
    df_partidos = df_modelo_5.copy()
elif not df_tabla_fichas.empty:
    df_partidos = df_tabla_fichas.copy()
else:
    df_partidos = pd.DataFrame([
        {
            "partido": "Real Sociedad vs Osasuna",
            "rival": "Osasuna",
            "local": "Local",
            "nivel_rival": "Medio",
            "pases_totales": 491,
            "precision_pase": 82.48,
            "pases_campo_rival_%": 41.96,
            "pases_zona_peligrosa": 35,
            "eventos_por_minuto": 9.11,
            "diferencia": 9.92,
            "modelo_partido": "Dominante",
            "tipo_rendimiento": "Muy eficiente",
        },
        {
            "partido": "Athletic Club vs Real Sociedad",
            "rival": "Athletic Club",
            "local": "Visitante",
            "nivel_rival": "Alto",
            "pases_totales": 398,
            "precision_pase": 74.62,
            "pases_campo_rival_%": 31.41,
            "pases_zona_peligrosa": 16,
            "eventos_por_minuto": 9.01,
            "diferencia": 2.44,
            "modelo_partido": "Vertical eficiente",
            "tipo_rendimiento": "Eficiente",
        }
    ])


# ============================================================
# NORMALIZACIÓN DE COLUMNAS BASE
# ============================================================

if "partido" not in df_partidos.columns:
    df_partidos["partido"] = [f"Partido {i+1}" for i in range(len(df_partidos))]

if "rival" not in df_partidos.columns:
    df_partidos["rival"] = df_partidos["partido"].apply(limpiar_nombre_rival)

if "local" not in df_partidos.columns and "condicion" in df_partidos.columns:
    df_partidos["local"] = df_partidos["condicion"]

if "local" not in df_partidos.columns:
    df_partidos["local"] = "No disponible"

if "nivel_rival" not in df_partidos.columns:
    df_partidos["nivel_rival"] = "Medio"

if "modelo_partido" not in df_partidos.columns:
    if "modelo_tactico" in df_partidos.columns:
        df_partidos["modelo_partido"] = df_partidos["modelo_tactico"]
    else:
        df_partidos["modelo_partido"] = "No clasificado"

if "tipo_rendimiento" not in df_partidos.columns:
    if "rendimiento" in df_partidos.columns:
        df_partidos["tipo_rendimiento"] = df_partidos["rendimiento"]
    else:
        df_partidos["tipo_rendimiento"] = "No clasificado"



# ============================================================
# FIX TFM — Forzar bloque oficial de 5 partidos
# ============================================================

partidos_tfm_oficiales = [
    {
        "partido": "Real Sociedad vs FC Barcelona",
        "rival": "FC Barcelona",
        "local": "Local",
        "nivel_rival": "Muy alto",
        "modelo_partido": "Rival dominante ofensivo",
        "tipo_rendimiento": "Pre-partido / alta exigencia",
        "pases_totales": media_pases if "media_pases" in globals() and media_pases else 445,
        "precision_pase": media_precision if "media_precision" in globals() and media_precision else 78.5,
        "pases_campo_rival_%": media_campo if "media_campo" in globals() and media_campo else 39.0,
        "pases_zona_peligrosa": media_zona if "media_zona" in globals() and media_zona else 25.5,
        "eventos_por_minuto": media_eventos if "media_eventos" in globals() and media_eventos else 9.0,
        "diferencia": 0,
    },
    {
        "partido": "Real Sociedad vs Real Club Celta de Vigo",
        "rival": "Real Club Celta de Vigo",
        "local": "Local",
        "nivel_rival": "Medio-alto",
        "modelo_partido": "Rival con capacidad de progresión",
        "tipo_rendimiento": "Pre-partido / control de progresión rival",
        "pases_totales": media_pases if "media_pases" in globals() and media_pases else 445,
        "precision_pase": media_precision if "media_precision" in globals() and media_precision else 78.5,
        "pases_campo_rival_%": media_campo if "media_campo" in globals() and media_campo else 39.0,
        "pases_zona_peligrosa": media_zona if "media_zona" in globals() and media_zona else 25.5,
        "eventos_por_minuto": media_eventos if "media_eventos" in globals() and media_eventos else 9.0,
        "diferencia": 0,
    },
    {
        "partido": "Athletic Club vs Real Sociedad",
        "rival": "Athletic Club",
        "local": "Visitante",
        "nivel_rival": "Alto",
        "modelo_partido": "Rival de presión e intensidad",
        "tipo_rendimiento": "Partido de ritmo alto",
        "pases_totales": 398,
        "precision_pase": 74.62,
        "pases_campo_rival_%": 31.41,
        "pases_zona_peligrosa": 16,
        "eventos_por_minuto": 9.01,
        "diferencia": 2.44,
    },
    {
        "partido": "Real Sociedad vs Real Club Deportivo Mallorca",
        "rival": "Real Club Deportivo Mallorca",
        "local": "Local",
        "nivel_rival": "Medio",
        "modelo_partido": "Rival reactivo / juego directo",
        "tipo_rendimiento": "Pre-partido / control de área y centros",
        "pases_totales": media_pases if "media_pases" in globals() and media_pases else 445,
        "precision_pase": media_precision if "media_precision" in globals() and media_precision else 78.5,
        "pases_campo_rival_%": media_campo if "media_campo" in globals() and media_campo else 39.0,
        "pases_zona_peligrosa": media_zona if "media_zona" in globals() and media_zona else 25.5,
        "eventos_por_minuto": media_eventos if "media_eventos" in globals() and media_eventos else 9.0,
        "diferencia": 0,
    },
    {
        "partido": "Real Sociedad vs Osasuna",
        "rival": "Osasuna",
        "local": "Local",
        "nivel_rival": "Medio",
        "modelo_partido": "Dominante",
        "tipo_rendimiento": "Muy eficiente",
        "pases_totales": 491,
        "precision_pase": 82.48,
        "pases_campo_rival_%": 41.96,
        "pases_zona_peligrosa": 35,
        "eventos_por_minuto": 9.11,
        "diferencia": 9.92,
    },
]

df_partidos_oficial = pd.DataFrame(partidos_tfm_oficiales)

# ============================================================
# FIX FINAL TFM — FICHA DE PARTIDO SOLO 5 PARTIDOS OFICIALES
# ============================================================

orden_partidos_tfm = [
    "Real Sociedad vs FC Barcelona",
    "Real Sociedad vs Real Club Celta de Vigo",
    "Athletic Club vs Real Sociedad",
    "Real Sociedad vs Real Club Deportivo Mallorca",
    "Real Sociedad vs Osasuna",
]

# Nos quedamos únicamente con los 5 partidos oficiales del TFM.
# Esto evita que en la pestaña "Ficha de partido" aparezcan partidos antiguos,
# duplicados o con nombres alternativos procedentes de otros CSV.
df_partidos = df_partidos_oficial.copy()

df_partidos["orden_tfm"] = df_partidos["partido"].apply(
    lambda x: orden_partidos_tfm.index(x) if x in orden_partidos_tfm else 999
)

df_partidos = (
    df_partidos
    .sort_values("orden_tfm")
    .drop(columns=["orden_tfm"])
    .reset_index(drop=True)
)



col_pases = buscar_columna(df_partidos, ["pases_totales", "Pases totales", "Total Passes", "total_passes"])
col_precision = buscar_columna(df_partidos, ["precision_pase", "precision", "Precisión", "Pass Accuracy", "Pass Accuracy Calculated"])
col_campo = buscar_columna(df_partidos, ["pases_campo_rival_%", "campo_rival", "Campo rival", "Passing % Opp Half"])
col_zona = buscar_columna(df_partidos, ["pases_zona_peligrosa", "zona_peligrosa", "Zona peligrosa"])
col_eventos = buscar_columna(df_partidos, ["eventos_por_minuto", "eventos_min", "Eventos/min"])
col_diferencia = buscar_columna(df_partidos, ["diferencia", "diferencia_contextual", "Diferencia"])


media_pases = serie_num(df_partidos, col_pases).mean() if col_pases else 0
media_precision = serie_num(df_partidos, col_precision).mean() if col_precision else 0
media_campo = serie_num(df_partidos, col_campo).mean() if col_campo else 0
media_zona = serie_num(df_partidos, col_zona).mean() if col_zona else 0
media_eventos = serie_num(df_partidos, col_eventos).mean() if col_eventos else 0
media_diferencia = serie_num(df_partidos, col_diferencia).mean() if col_diferencia else 0


# ============================================================
# CONTEXTO 30 PARTIDOS
# ============================================================

if df_contexto_30.empty:
    df_contexto_30 = df_partidos.copy()
    df_contexto_30["jornada"] = range(1, len(df_contexto_30) + 1)

if "partido" not in df_contexto_30.columns:
    df_contexto_30["partido"] = [f"Partido {i+1}" for i in range(len(df_contexto_30))]

if "jornada" not in df_contexto_30.columns:
    df_contexto_30["jornada"] = range(1, len(df_contexto_30) + 1)


col30_pases = buscar_columna(df_contexto_30, ["pases_totales", "Pases totales", "Total Passes", "total_passes"])
col30_precision = buscar_columna(df_contexto_30, ["precision_pase", "precision", "Precisión", "Pass Accuracy", "Pass Accuracy Calculated"])
col30_campo = buscar_columna(df_contexto_30, ["pases_campo_rival_%", "campo_rival", "Campo rival", "Passing % Opp Half"])
col30_zona = buscar_columna(df_contexto_30, ["pases_zona_peligrosa", "zona_peligrosa", "Zona peligrosa"])
col30_eventos = buscar_columna(df_contexto_30, ["eventos_por_minuto", "eventos_min", "Eventos/min"])


# ============================================================
# PERFIL RIVALES
# ============================================================

if df_perfil_rivales.empty:
    df_perfil_rivales = pd.DataFrame([
        {
            "codigo": "BCN",
            "equipo": "FC Barcelona",
            "Possession Percentage": 68.3,
            "Total Passes": 19491,
            "Pass Accuracy Calculated": 89.68,
            "Passing % Opp Half": 86.87,
            "Total Shots": 431,
            "Shots On Target ( inc goals )": 216,
            "Goal Conversion": 18.56,
            "Total Goals": 80,
            "Aerial Duel Win %": 58.8,
            "Ground Duel Win %": 52.8,
            "PPDA": 8.6,
            "Defensive Activity": 821,
            "Total Shots Conceded": 274,
            "Shots Conceded per Defensive Action": 0.33,
            "Recoveries": 1426,
            "Interceptions": 234,
            "Total Clearances": 527,
            "Set Piece Threat": 23,
            "Yellow Cards": 44,
        },
        {
            "codigo": "CLT",
            "equipo": "Real Club Celta de Vigo",
            "Possession Percentage": 50.8,
            "Total Passes": 14945,
            "Pass Accuracy Calculated": 86.15,
            "Passing % Opp Half": 81.25,
            "Total Shots": 244,
            "Shots On Target ( inc goals )": 125,
            "Goal Conversion": 18.03,
            "Total Goals": 44,
            "Aerial Duel Win %": 47.4,
            "Ground Duel Win %": 49.77,
            "PPDA": 14.3,
            "Defensive Activity": 682,
            "Total Shots Conceded": 362,
            "Shots Conceded per Defensive Action": 0.53,
            "Recoveries": 1336,
            "Interceptions": 215,
            "Total Clearances": 739,
            "Set Piece Threat": 5,
            "Yellow Cards": 56,
        },
        {
            "codigo": "MLL",
            "equipo": "Real Club Deportivo Mallorca",
            "Possession Percentage": 45.0,
            "Total Passes": 11467,
            "Pass Accuracy Calculated": 80.19,
            "Passing % Opp Half": 71.98,
            "Total Shots": 247,
            "Shots On Target ( inc goals )": 119,
            "Goal Conversion": 14.57,
            "Total Goals": 36,
            "Aerial Duel Win %": 52.0,
            "Ground Duel Win %": 49.24,
            "PPDA": 14.3,
            "Defensive Activity": 677,
            "Total Shots Conceded": 450,
            "Shots Conceded per Defensive Action": 0.66,
            "Recoveries": 1315,
            "Interceptions": 219,
            "Total Clearances": 882,
            "Set Piece Threat": 8,
            "Yellow Cards": 67,
        },
        {
            "codigo": "ATH",
            "equipo": "Athletic Club",
            "Possession Percentage": 48.8,
            "Total Passes": 12382,
            "Pass Accuracy Calculated": 80.33,
            "Passing % Opp Half": 73.89,
            "Total Shots": 292,
            "Shots On Target ( inc goals )": 136,
            "Goal Conversion": 10.96,
            "Total Goals": 32,
            "Aerial Duel Win %": 49.0,
            "Ground Duel Win %": 45.08,
            "PPDA": 11.0,
            "Defensive Activity": 1002,
            "Total Shots Conceded": 289,
            "Shots Conceded per Defensive Action": 0.29,
            "Recoveries": 1577,
            "Interceptions": 268,
            "Total Clearances": 657,
            "Set Piece Threat": 2,
            "Yellow Cards": 63,
        },
        {
            "codigo": "OSAS",
            "equipo": "CA Osasuna",
            "Possession Percentage": 45.5,
            "Total Passes": 11443,
            "Pass Accuracy Calculated": 80.17,
            "Passing % Opp Half": 72.49,
            "Total Shots": 254,
            "Shots On Target ( inc goals )": 112,
            "Goal Conversion": 14.17,
            "Total Goals": 36,
            "Aerial Duel Win %": 54.5,
            "Ground Duel Win %": 47.93,
            "PPDA": 13.4,
            "Defensive Activity": 743,
            "Total Shots Conceded": 384,
            "Shots Conceded per Defensive Action": 0.52,
            "Recoveries": 1424,
            "Interceptions": 241,
            "Total Clearances": 802,
            "Set Piece Threat": 16,
            "Yellow Cards": 72,
        },
    ])

if "equipo" not in df_perfil_rivales.columns:
    df_perfil_rivales["equipo"] = [f"Rival {i+1}" for i in range(len(df_perfil_rivales))]

if "codigo" not in df_perfil_rivales.columns:
    df_perfil_rivales["codigo"] = df_perfil_rivales["equipo"].astype(str).str[:4].str.upper()


if df_interpretacion_rivales.empty:
    df_interpretacion_rivales = pd.DataFrame([
        {
            "codigo": row["codigo"],
            "equipo": row["equipo"],
            "interpretacion_tactica": (
                "Perfil táctico interpretado a partir de los KPIs disponibles. "
                "El objetivo es preparar el partido combinando volumen ofensivo, presencia en campo rival, amenaza, presión y solidez defensiva."
            )
        }
        for _, row in df_perfil_rivales.iterrows()
    ])

if df_resumen_prepartido.empty:
    df_resumen_prepartido = pd.DataFrame([
        {
            "rival": row["equipo"],
            "perfil_ofensivo": "Perfil ofensivo contextual",
            "estilo_con_balon": "Estilo con balón analizado",
            "perfil_defensivo": "Perfil defensivo contextual",
            "amenaza_principal": "Amenaza principal según KPIs",
            "plan_para_real_sociedad": "Plan de partido orientado a controlar fortalezas del rival y potenciar ventajas propias."
        }
        for _, row in df_perfil_rivales.iterrows()
    ])


# ============================================================
# CLASIFICACIÓN LALIGA — CONTEXTO COMPETITIVO
# ============================================================

df_clasificacion_laliga = pd.DataFrame([
    {"Pos": 1, "Equipo": "FC Barcelona", "PJ": 38, "G": 31, "E": 1, "P": 6, "GF": 95, "GC": 36, "DG": 59, "Pts": 94},
    {"Pos": 2, "Equipo": "Real Madrid", "PJ": 38, "G": 27, "E": 5, "P": 6, "GF": 77, "GC": 35, "DG": 42, "Pts": 86},
    {"Pos": 3, "Equipo": "Villarreal", "PJ": 38, "G": 22, "E": 6, "P": 10, "GF": 72, "GC": 46, "DG": 26, "Pts": 72},
    {"Pos": 4, "Equipo": "Atlético de Madrid", "PJ": 38, "G": 21, "E": 6, "P": 11, "GF": 62, "GC": 44, "DG": 18, "Pts": 69},
    {"Pos": 5, "Equipo": "Real Betis", "PJ": 38, "G": 15, "E": 15, "P": 8, "GF": 59, "GC": 48, "DG": 11, "Pts": 60},
    {"Pos": 6, "Equipo": "Celta de Vigo", "PJ": 38, "G": 14, "E": 12, "P": 12, "GF": 53, "GC": 48, "DG": 5, "Pts": 54},
    {"Pos": 7, "Equipo": "Getafe", "PJ": 38, "G": 15, "E": 6, "P": 17, "GF": 32, "GC": 38, "DG": -6, "Pts": 51},
    {"Pos": 8, "Equipo": "Rayo Vallecano", "PJ": 38, "G": 12, "E": 14, "P": 12, "GF": 41, "GC": 44, "DG": -3, "Pts": 50},
    {"Pos": 9, "Equipo": "Valencia CF", "PJ": 38, "G": 13, "E": 10, "P": 15, "GF": 46, "GC": 55, "DG": -9, "Pts": 49},
    {"Pos": 10, "Equipo": "Real Sociedad", "PJ": 38, "G": 11, "E": 13, "P": 14, "GF": 59, "GC": 61, "DG": -2, "Pts": 46},
    {"Pos": 11, "Equipo": "RCD Espanyol", "PJ": 38, "G": 12, "E": 10, "P": 16, "GF": 43, "GC": 55, "DG": -12, "Pts": 46},
    {"Pos": 12, "Equipo": "Athletic Club", "PJ": 38, "G": 13, "E": 6, "P": 19, "GF": 43, "GC": 58, "DG": -15, "Pts": 45},
    {"Pos": 13, "Equipo": "Sevilla", "PJ": 38, "G": 12, "E": 7, "P": 19, "GF": 46, "GC": 60, "DG": -14, "Pts": 43},
    {"Pos": 14, "Equipo": "Alavés", "PJ": 38, "G": 11, "E": 10, "P": 17, "GF": 44, "GC": 56, "DG": -12, "Pts": 43},
    {"Pos": 15, "Equipo": "Elche CF", "PJ": 38, "G": 10, "E": 13, "P": 15, "GF": 49, "GC": 57, "DG": -8, "Pts": 43},
    {"Pos": 16, "Equipo": "Levante", "PJ": 38, "G": 11, "E": 9, "P": 18, "GF": 47, "GC": 61, "DG": -14, "Pts": 42},
    {"Pos": 17, "Equipo": "Osasuna", "PJ": 38, "G": 11, "E": 9, "P": 18, "GF": 44, "GC": 50, "DG": -6, "Pts": 42},
    {"Pos": 18, "Equipo": "RCD Mallorca", "PJ": 38, "G": 11, "E": 9, "P": 18, "GF": 47, "GC": 57, "DG": -10, "Pts": 42},
    {"Pos": 19, "Equipo": "Girona", "PJ": 38, "G": 9, "E": 14, "P": 15, "GF": 39, "GC": 55, "DG": -16, "Pts": 41},
    {"Pos": 20, "Equipo": "Real Oviedo", "PJ": 38, "G": 6, "E": 11, "P": 21, "GF": 26, "GC": 60, "DG": -34, "Pts": 29},
])




# ============================================================
# INTERPRETACIONES TÁCTICAS APP FINAL
# ============================================================

RUTA_INTERPRETACIONES_TACTICAS = os.path.join(CARPETA_DATOS, "interpretaciones_tacticas_app_final.csv")
df_interpretaciones_tacticas = leer_csv_seguro(RUTA_INTERPRETACIONES_TACTICAS)

def obtener_interpretacion(seccion, bloque=None):
    if df_interpretaciones_tacticas.empty:
        return {"titulo": seccion, "texto": "", "uso_presentacion": ""}

    df = df_interpretaciones_tacticas.copy()
    df = df[df["seccion"].astype(str).str.lower() == str(seccion).lower()]

    if bloque is not None and "bloque" in df.columns:
        df_bloque = df[df["bloque"].astype(str).str.lower() == str(bloque).lower()]
        if not df_bloque.empty:
            df = df_bloque

    if df.empty:
        return {"titulo": seccion, "texto": "", "uso_presentacion": ""}

    row = df.iloc[0]
    return {
        "titulo": str(row.get("titulo", seccion)),
        "texto": str(row.get("texto", "")),
        "uso_presentacion": str(row.get("uso_presentacion", ""))
    }


def bloque_lectura_tactica(seccion, bloque=None):
    info = obtener_interpretacion(seccion, bloque)

    return html.Div(
        className="grid-2",
        children=[
            html.Div(
                className="chart-card",
                children=[
                    html.H2(info["titulo"]),
                    html.P(info["texto"]),
                ]
            ),
            html.Div(
                className="chart-card",
                children=[
                    html.H2("Uso en presentación"),
                    html.P(info["uso_presentacion"]),
                    html.Div([
                        html.Span("Qué miro", className="pill"),
                        html.Span("Qué significa", className="pill"),
                        html.Span("Qué decisión saco", className="pill"),
                    ])
                ]
            )
        ]
    )


# ============================================================
# FIGURAS
# ============================================================

def aplicar_layout(fig, titulo=None, height=520, dark=False):
    if dark:
        fig.update_layout(
            template="plotly_dark",
            title=titulo,
            height=height,
            font=dict(family="Arial", size=15, color="#f4f8ff"),
            title_font=dict(size=24, color="#ffffff"),
            plot_bgcolor="#111827",
            paper_bgcolor="#111827",
            margin=dict(l=55, r=35, t=75, b=55),
            hoverlabel=dict(bgcolor="#ffffff", font_size=14, font_color="#08213f"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
    else:
        fig.update_layout(
            template="plotly_white",
            title=titulo,
            height=height,
            font=dict(family="Arial", size=15, color="#08213f"),
            title_font=dict(size=24, color="#08213f"),
            plot_bgcolor="white",
            paper_bgcolor="white",
            margin=dict(l=55, r=35, t=75, b=55),
            hoverlabel=dict(bgcolor="white", font_size=14, font_color="#08213f"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
    return fig


def fig_modelo_radar():
    categorias = ["Volumen pase", "Precisión", "Campo rival", "Zona peligrosa", "Ritmo", "Diferencia"]
    valores_raw = [media_pases, media_precision, media_campo, media_zona, media_eventos, media_diferencia]

    maximos = [
        max(media_pases * 1.25, 1),
        100,
        100,
        max(media_zona * 1.6, 1),
        max(media_eventos * 1.6, 1),
        max(abs(media_diferencia) * 1.8, 1)
    ]

    valores_norm = []
    for v, m in zip(valores_raw, maximos):
        v = 0 if pd.isna(v) else float(v)
        valores_norm.append(min(max(abs(v) / m, 0), 1))

    valores_norm += [valores_norm[0]]
    categorias_cerradas = categorias + [categorias[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=valores_norm,
        theta=categorias_cerradas,
        fill="toself",
        line=dict(color="#00a3ff", width=4),
        fillcolor="rgba(0,163,255,0.26)",
        name="Real Sociedad"
    ))

    fig.update_layout(
        polar=dict(
            bgcolor="rgba(8,33,63,0.08)",
            radialaxis=dict(visible=True, range=[0, 1], tickfont=dict(size=11), gridcolor="#d7e4f1"),
            angularaxis=dict(tickfont=dict(size=15, color="#08213f"), gridcolor="#d7e4f1")
        ),
        showlegend=False
    )

    return aplicar_layout(fig, "Radar del modelo ofensivo — Real Sociedad", height=560)


def fig_modelo_barras():
    df = pd.DataFrame({
        "KPI": ["Pases", "Precisión", "Campo rival", "Zona peligrosa", "Eventos/min", "Diferencia"],
        "Valor": [
            round(media_pases, 2),
            round(media_precision, 2),
            round(media_campo, 2),
            round(media_zona, 2),
            round(media_eventos, 2),
            round(media_diferencia, 2),
        ],
        "Bloque": ["Volumen", "Calidad", "Progresión", "Amenaza", "Ritmo", "Contexto"]
    })

    fig = px.bar(
        df,
        x="KPI",
        y="Valor",
        color="Bloque",
        text="Valor",
        color_discrete_sequence=["#005baa", "#00a3ff", "#1ca86a", "#f5a000", "#6c63ff", "#10243e"],
        title="KPIs base del modelo ofensivo"
    )

    fig.update_traces(textposition="outside")
    fig.update_layout(
        xaxis_title="KPI",
        yaxis_title="Valor medio",
        legend_title=""
    )

    return aplicar_layout(fig, height=500)


def fig_evolucion_30():
    df = df_contexto_30.copy()
    df["orden"] = range(1, len(df) + 1)

    fig = go.Figure()

    if col30_precision:
        fig.add_trace(go.Scatter(
            x=df["orden"],
            y=serie_num(df, col30_precision),
            mode="lines+markers",
            name="Precisión pase",
            line=dict(width=3, color="#005baa")
        ))

    if col30_campo:
        fig.add_trace(go.Scatter(
            x=df["orden"],
            y=serie_num(df, col30_campo),
            mode="lines+markers",
            name="Campo rival",
            line=dict(width=3, color="#1ca86a")
        ))

    if col30_zona:
        fig.add_trace(go.Scatter(
            x=df["orden"],
            y=serie_num(df, col30_zona),
            mode="lines+markers",
            name="Zona peligrosa",
            line=dict(width=3, color="#f5a000")
        ))

    if len(fig.data) == 0:
        fig.add_trace(go.Scatter(
            x=df["orden"],
            y=np.zeros(len(df)),
            mode="markers",
            name="Sin KPIs detectados"
        ))

    fig.update_layout(
        xaxis_title="Partido de la muestra",
        yaxis_title="Valor KPI",
        legend_title=""
    )

    return aplicar_layout(fig, "Evolución ofensiva — muestra de 30 partidos", height=540)


def fig_30_burbujas():
    df = df_contexto_30.copy()

    x_col = col30_campo
    y_col = col30_zona
    size_col = col30_pases

    if x_col is None:
        df["x_aux"] = range(1, len(df) + 1)
        x_col = "x_aux"

    if y_col is None:
        df["y_aux"] = range(1, len(df) + 1)
        y_col = "y_aux"

    fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        size=size_col if size_col else None,
        hover_name="partido",
        color="local_visitante" if "local_visitante" in df.columns else None,
        title="Mapa contextual de partidos: campo rival vs zona peligrosa",
        color_discrete_sequence=["#005baa", "#1ca86a", "#f5a000"]
    )

    fig.add_vline(
        x=pd.to_numeric(df[x_col], errors="coerce").mean(),
        line_dash="dash",
        line_color="#f5a000",
        annotation_text="Media campo rival"
    )

    fig.add_hline(
        y=pd.to_numeric(df[y_col], errors="coerce").mean(),
        line_dash="dash",
        line_color="#f5a000",
        annotation_text="Media zona peligrosa"
    )

    fig.update_traces(marker=dict(opacity=0.82, line=dict(width=1, color="white")))
    fig.update_layout(
        xaxis_title="Presencia en campo rival (%)",
        yaxis_title="Pases / acciones en zona peligrosa",
        legend_title=""
    )

    return aplicar_layout(fig, height=560)


def fig_comparativa_5_vs_30():
    if not df_comparativa_5_30.empty:
        df = df_comparativa_5_30.copy()

        metricas = [
            ("Pases", "pases_totales", "dif_pases_totales"),
            ("Precisión", "precision_pase", "dif_precision_pase"),
            ("Campo rival", "pases_campo_rival_%", "dif_pases_campo_rival_%"),
            ("Zona peligrosa", "pases_zona_peligrosa", "dif_pases_zona_peligrosa"),
            ("Eventos/min", "eventos_por_minuto", "dif_eventos_por_minuto"),
        ]

        datos = []

        for nombre, col_valor, col_dif in metricas:
            if col_valor in df.columns:
                datos.append({
                    "KPI": nombre,
                    "Valor medio 5 partidos": pd.to_numeric(df[col_valor], errors="coerce").mean(),
                    "Diferencia vs media 30": pd.to_numeric(df[col_dif], errors="coerce").mean() if col_dif in df.columns else 0
                })

        df_fig = pd.DataFrame(datos)

        if not df_fig.empty:
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df_fig["KPI"],
                y=df_fig["Valor medio 5 partidos"],
                name="Media 5 partidos",
                text=df_fig["Valor medio 5 partidos"].round(2),
                textposition="outside",
                marker_color="#005baa"
            ))
            fig.add_trace(go.Bar(
                x=df_fig["KPI"],
                y=df_fig["Diferencia vs media 30"],
                name="Diferencia vs 30",
                text=df_fig["Diferencia vs media 30"].round(2),
                textposition="outside",
                marker_color="#f5a000"
            ))

            fig.update_layout(
                barmode="group",
                xaxis_title="KPI",
                yaxis_title="Valor",
                legend_title=""
            )

            return aplicar_layout(fig, "Bloque de 5 partidos: rendimiento y diferencia vs muestra 30", height=560)

    df = df_partidos.copy()
    data = []

    metricas = [
        ("Pases", col_pases),
        ("Precisión", col_precision),
        ("Campo rival", col_campo),
        ("Zona peligrosa", col_zona),
        ("Eventos/min", col_eventos),
        ("Diferencia", col_diferencia)
    ]

    for nombre, col in metricas:
        if col:
            data.append({"KPI": nombre, "Muestra": "Media 5 partidos", "Valor": serie_num(df, col).mean()})

    df_fig = pd.DataFrame(data)

    if df_fig.empty:
        df_fig = pd.DataFrame({"KPI": ["Sin datos"], "Muestra": ["Sin datos"], "Valor": [0]})

    fig = px.bar(
        df_fig,
        x="KPI",
        y="Valor",
        color="Muestra",
        text=df_fig["Valor"].round(2),
        title="Comparativa contextual: bloque de 5 partidos"
    )

    fig.update_traces(textposition="outside")
    fig.update_layout(
        xaxis_title="KPI",
        yaxis_title="Valor medio",
        legend_title=""
    )

    return aplicar_layout(fig, height=560)


def fig_partido_kpis(partido):
    df = df_partidos.copy()
    fila = df[df["partido"] == partido]
    if fila.empty:
        fila = df.iloc[[0]]
    fila = fila.iloc[0]

    datos = []
    for nombre, col in [
        ("Pases", col_pases),
        ("Precisión", col_precision),
        ("Campo rival", col_campo),
        ("Zona peligrosa", col_zona),
        ("Eventos/min", col_eventos),
        ("Diferencia", col_diferencia)
    ]:
        if col:
            datos.append({
                "KPI": nombre,
                "Partido": num(fila[col]),
                "Media 5 partidos": serie_num(df, col).mean()
            })

    if not datos:
        datos = [{"KPI": "Sin datos", "Partido": 0, "Media 5 partidos": 0}]

    df_fig = pd.DataFrame(datos)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_fig["KPI"],
        y=df_fig["Partido"],
        name="Partido",
        text=df_fig["Partido"].round(2),
        textposition="outside",
        marker_color="#005baa"
    ))

    fig.add_trace(go.Bar(
        x=df_fig["KPI"],
        y=df_fig["Media 5 partidos"],
        name="Media 5 partidos",
        text=df_fig["Media 5 partidos"].round(2),
        textposition="outside",
        marker_color="#9fb6d5"
    ))

    fig.update_layout(
        barmode="group",
        xaxis_title="KPI",
        yaxis_title="Valor",
        legend_title=""
    )

    return aplicar_layout(fig, f"Ficha KPI — {partido}", height=540)


def fig_partido_campo(partido):
    df = df_partidos.copy()
    fila = df[df["partido"] == partido]
    if fila.empty:
        fila = df.iloc[[0]]
    fila = fila.iloc[0]

    campo = num(fila.get(col_campo, 0)) if col_campo else 0
    zona = num(fila.get(col_zona, 0)) if col_zona else 0
    precision = num(fila.get(col_precision, 0)) if col_precision else 0

    fig = go.Figure()

    fig.add_shape(type="rect", x0=0, y0=0, x1=100, y1=68, line=dict(color="#ffffff", width=2), fillcolor="#1e6b3a")
    fig.add_shape(type="line", x0=50, y0=0, x1=50, y1=68, line=dict(color="#ffffff", width=2))
    fig.add_shape(type="circle", x0=41.5, y0=25.5, x1=58.5, y1=42.5, line=dict(color="#ffffff", width=2))
    fig.add_shape(type="rect", x0=0, y0=13.84, x1=16.5, y1=54.16, line=dict(color="#ffffff", width=2))
    fig.add_shape(type="rect", x0=83.5, y0=13.84, x1=100, y1=54.16, line=dict(color="#ffffff", width=2))
    fig.add_shape(type="rect", x0=75, y0=0, x1=100, y1=68, line=dict(color="rgba(255,255,255,0.15)", width=1), fillcolor="rgba(245,160,0,0.18)")
    fig.add_shape(type="rect", x0=50, y0=0, x1=100, y1=68, line=dict(color="rgba(255,255,255,0.10)", width=1), fillcolor="rgba(0,91,170,0.12)")

    fig.add_trace(go.Scatter(
        x=[65],
        y=[34],
        mode="markers+text",
        marker=dict(size=max(24, zona * 1.2), color="#f5a000", line=dict(color="white", width=2)),
        text=[f"Zona peligrosa<br>{formato_valor(zona)}"],
        textposition="middle center",
        textfont=dict(color="white", size=14),
        name="Zona peligrosa"
    ))

    fig.add_trace(go.Scatter(
        x=[campo],
        y=[16],
        mode="markers+text",
        marker=dict(size=24, color="#00a3ff", line=dict(color="white", width=2)),
        text=[f"Campo rival<br>{formato_valor(campo, sufijo='%')}"],
        textposition="top center",
        textfont=dict(color="white", size=13),
        name="Campo rival"
    ))

    fig.add_trace(go.Scatter(
        x=[precision],
        y=[52],
        mode="markers+text",
        marker=dict(size=22, color="#18a84f", line=dict(color="white", width=2)),
        text=[f"Precisión<br>{formato_valor(precision, sufijo='%')}"],
        textposition="top center",
        textfont=dict(color="white", size=13),
        name="Precisión"
    ))

    fig.update_xaxes(visible=False, range=[0, 100])
    fig.update_yaxes(visible=False, range=[0, 68], scaleanchor="x", scaleratio=1)

    fig.update_layout(showlegend=False)

    return aplicar_layout(fig, f"Mapa conceptual ofensivo — {partido}", height=520, dark=True)


def normalizar(valor, serie, invertir=False):
    serie = pd.to_numeric(serie, errors="coerce")
    valor = num(valor)
    minimo = serie.min()
    maximo = serie.max()

    if pd.isna(minimo) or pd.isna(maximo) or maximo == minimo:
        return 0.5

    base = (valor - minimo) / (maximo - minimo)
    if invertir:
        base = 1 - base

    return max(0, min(1, base))


def fig_radar_rival(equipo):
    fila = df_perfil_rivales[df_perfil_rivales["equipo"] == equipo]

    if fila.empty:
        return aplicar_layout(go.Figure(), "Radar táctico del rival")

    fila = fila.iloc[0]

    metricas = {
        "Posesión": ("Possession Percentage", False),
        "Volumen pase": ("Total Passes", False),
        "Precisión": ("Pass Accuracy Calculated", False),
        "Campo rival": ("Passing % Opp Half", False),
        "Remate": ("Total Shots", False),
        "Eficacia": ("Goal Conversion", False),
        "Duelos suelo": ("Ground Duel Win %", False),
        "Duelos aéreos": ("Aerial Duel Win %", False),
        "Presión": ("PPDA", True),
        "ABP": ("Set Piece Threat", False),
    }

    labels = []
    valores = []

    for label, (col, invertir) in metricas.items():
        if col in df_perfil_rivales.columns:
            labels.append(label)
            valores.append(normalizar(fila[col], df_perfil_rivales[col], invertir=invertir))

    if not valores:
        valores = [0]
        labels = ["Sin datos"]

    valores = valores + [valores[0]]
    labels = labels + [labels[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=valores,
        theta=labels,
        fill="toself",
        line=dict(color="#00a3ff", width=4),
        fillcolor="rgba(0,163,255,0.24)",
        name=equipo
    ))

    fig.update_layout(
        polar=dict(
            bgcolor="rgba(8,33,63,0.08)",
            radialaxis=dict(visible=True, range=[0, 1], gridcolor="#d7e4f1"),
            angularaxis=dict(gridcolor="#d7e4f1")
        ),
        showlegend=False
    )

    return aplicar_layout(fig, f"Radar táctico del rival — {equipo}", height=570)


def quadrant(df, x_col, y_col, size_col, titulo, x_title, y_title, invertir_y=False):
    df = df.copy()

    if x_col not in df.columns or y_col not in df.columns:
        return aplicar_layout(go.Figure(), titulo, height=560)

    fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        size=size_col if size_col in df.columns else None,
        text="codigo",
        hover_name="equipo",
        title=titulo,
        color_discrete_sequence=["#005baa"]
    )

    fig.add_vline(
        x=pd.to_numeric(df[x_col], errors="coerce").mean(),
        line_dash="dash",
        line_color="#f5a000",
        annotation_text="Media",
        annotation_position="top"
    )

    fig.add_hline(
        y=pd.to_numeric(df[y_col], errors="coerce").mean(),
        line_dash="dash",
        line_color="#f5a000",
        annotation_text="Media",
        annotation_position="left"
    )

    fig.update_traces(
        marker=dict(color="#005baa", opacity=0.78, line=dict(width=1, color="white")),
        textposition="top center"
    )

    fig.update_layout(
        xaxis_title=x_title,
        yaxis_title=y_title
    )

    if invertir_y:
        fig.update_yaxes(autorange="reversed")

    return aplicar_layout(fig, height=560)


def fig_quadrant_ofensivo():
    return quadrant(
        df_perfil_rivales,
        "Total Shots",
        "Goal Conversion",
        "Total Goals",
        "Perfil ofensivo rival: remate vs eficacia",
        "Remates totales",
        "Conversión de gol (%)"
    )


def fig_quadrant_estilo():
    return quadrant(
        df_perfil_rivales,
        "Possession Percentage",
        "Passing % Opp Half",
        "Total Passes",
        "Estilo con balón: posesión vs presencia en campo rival",
        "Posesión media (%)",
        "% pases en campo rival"
    )


def fig_quadrant_defensivo():
    return quadrant(
        df_perfil_rivales,
        "Defensive Activity",
        "Shots Conceded per Defensive Action",
        "Total Shots Conceded",
        "Perfil defensivo rival: actividad vs concesión",
        "Actividad defensiva",
        "Remates concedidos por acción defensiva"
    )


def fig_barras_rival(equipo):
    fila = df_perfil_rivales[df_perfil_rivales["equipo"] == equipo]
    if fila.empty:
        return aplicar_layout(go.Figure(), "KPIs del rival")

    fila = fila.iloc[0]

    metricas = [
        ("Posesión", "Possession Percentage"),
        ("Precisión", "Pass Accuracy Calculated"),
        ("Campo rival", "Passing % Opp Half"),
        ("Remates", "Total Shots"),
        ("Goles", "Total Goals"),
        ("PPDA", "PPDA"),
        ("Act. def.", "Defensive Activity"),
        ("ABP", "Set Piece Threat"),
    ]

    data = []
    for nombre, col in metricas:
        if col in df_perfil_rivales.columns:
            data.append({"KPI": nombre, "Valor": num(fila[col])})

    df_fig = pd.DataFrame(data)

    fig = px.bar(
        df_fig,
        x="KPI",
        y="Valor",
        text="Valor",
        title=f"Resumen de KPIs — {equipo}",
        color="KPI",
        color_discrete_sequence=["#005baa", "#00a3ff", "#1ca86a", "#f5a000", "#6c63ff", "#10243e"]
    )

    fig.update_traces(textposition="outside")
    fig.update_layout(xaxis_title="", yaxis_title="Valor", showlegend=False)

    return aplicar_layout(fig, height=480)


def fig_clasificacion_barras():
    df = df_clasificacion_laliga.copy()
    df["Grupo"] = np.where(df["Equipo"] == "Real Sociedad", "Real Sociedad", "Resto")

    fig = px.bar(
        df.sort_values("Pts", ascending=True),
        x="Pts",
        y="Equipo",
        orientation="h",
        color="Grupo",
        text="Pts",
        title="Puntos por equipo — clasificación final",
        color_discrete_map={"Real Sociedad": "#005baa", "Resto": "#9fb6d5"}
    )

    fig.update_traces(textposition="outside")
    fig.update_layout(
        xaxis_title="Puntos",
        yaxis_title="Equipo",
        legend_title=""
    )

    return aplicar_layout(fig, height=720)






# ============================================================
# INTERPRETACIONES TÁCTICAS APP FINAL
# ============================================================

RUTA_INTERPRETACIONES_TACTICAS = os.path.join(CARPETA_DATOS, "interpretaciones_tacticas_app_final.csv")
df_interpretaciones_tacticas = leer_csv_seguro(RUTA_INTERPRETACIONES_TACTICAS)

def obtener_interpretacion(seccion, bloque=None):
    if df_interpretaciones_tacticas.empty:
        return {"titulo": seccion, "texto": "", "uso_presentacion": ""}

    df = df_interpretaciones_tacticas.copy()
    df = df[df["seccion"].astype(str).str.lower() == str(seccion).lower()]

    if bloque is not None and "bloque" in df.columns:
        df_bloque = df[df["bloque"].astype(str).str.lower() == str(bloque).lower()]
        if not df_bloque.empty:
            df = df_bloque

    if df.empty:
        return {"titulo": seccion, "texto": "", "uso_presentacion": ""}

    row = df.iloc[0]
    return {
        "titulo": str(row.get("titulo", seccion)),
        "texto": str(row.get("texto", "")),
        "uso_presentacion": str(row.get("uso_presentacion", ""))
    }


def bloque_lectura_tactica(seccion, bloque=None):
    info = obtener_interpretacion(seccion, bloque)

    return html.Div(
        className="grid-2",
        children=[
            html.Div(
                className="chart-card",
                children=[
                    html.H2(info["titulo"]),
                    html.P(info["texto"]),
                ]
            ),
            html.Div(
                className="chart-card",
                children=[
                    html.H2("Uso en presentación"),
                    html.P(info["uso_presentacion"]),
                    html.Div([
                        html.Span("Qué miro", className="pill"),
                        html.Span("Qué significa", className="pill"),
                        html.Span("Qué decisión saco", className="pill"),
                    ])
                ]
            )
        ]
    )


# ============================================================
# FIGURAS Y COMPONENTES — JUGADORES
# ============================================================

def fig_ranking_jugadores(df, titulo, top=12, metrica="indice_total_app"):
    if df.empty or metrica not in df.columns:
        fig = go.Figure()
        return aplicar_layout(fig, titulo, height=520)

    df_plot = df.copy()
    df_plot[metrica] = pd.to_numeric(df_plot[metrica], errors="coerce").fillna(0)
    df_plot = df_plot.sort_values(metrica, ascending=False).head(top)
    df_plot = df_plot.sort_values(metrica, ascending=True)

    fig = px.bar(
        df_plot,
        x=metrica,
        y="jugador_app",
        orientation="h",
        color="posicion_app",
        hover_data=["equipo_app", "posicion_app", "minutos_app", "partidos_app"],
        text=df_plot[metrica].round(2),
        title=titulo,
        color_discrete_sequence=["#005baa", "#00a3ff", "#1ca86a", "#f5a000", "#6c63ff", "#10243e"]
    )

    fig.update_traces(textposition="outside")
    fig.update_layout(
        xaxis_title="Valor del índice",
        yaxis_title="Jugador",
        legend_title="Posición"
    )

    return aplicar_layout(fig, height=620)


def fig_perfil_fases_jugadores_rs():
    if df_jugadores_rs.empty:
        return aplicar_layout(go.Figure(), "Perfil por fases — Real Sociedad", height=520)

    metricas = [
        ("Ofensivo", "indice_ofensivo_app"),
        ("Progresión", "indice_progresion_app"),
        ("Defensivo", "indice_defensivo_app"),
        ("Total", "indice_total_app")
    ]

    datos = []
    for nombre, col in metricas:
        if col in df_jugadores_rs.columns:
            top = df_jugadores_rs.sort_values(col, ascending=False).head(1)
            if not top.empty:
                datos.append({
                    "Fase": nombre,
                    "Jugador": top.iloc[0]["jugador_app"],
                    "Valor": float(top.iloc[0][col])
                })

    df_fig = pd.DataFrame(datos)

    if df_fig.empty:
        return aplicar_layout(go.Figure(), "Perfil por fases — Real Sociedad", height=520)

    fig = px.bar(
        df_fig,
        x="Valor",
        y="Fase",
        orientation="h",
        text="Jugador",
        color="Fase",
        title="Líderes internos por fase táctica — Real Sociedad",
        color_discrete_sequence=["#005baa", "#00a3ff", "#1ca86a", "#f5a000"]
    )

    fig.update_traces(textposition="outside")
    fig.update_layout(
        xaxis_title="Valor del indicador",
        yaxis_title="Fase táctica",
        showlegend=False
    )

    return aplicar_layout(fig, height=500)


def fig_mapa_jugadores_laliga(df=None):
    if df is None:
        df = df_jugadores_laliga.copy()

    if df.empty:
        return aplicar_layout(go.Figure(), "Mapa de perfiles individuales — LaLiga", height=560)

    df_plot = df.copy()

    x_col = "indice_ofensivo_app"
    y_col = "indice_defensivo_app"
    size_col = "indice_total_app"

    fig = px.scatter(
        df_plot,
        x=x_col,
        y=y_col,
        size=size_col if size_col in df_plot.columns else None,
        color="posicion_app",
        hover_name="jugador_app",
        hover_data=["equipo_app", "posicion_app", "minutos_app", "partidos_app"],
        title="Mapa de perfiles individuales — LaLiga",
        color_discrete_sequence=["#005baa", "#00a3ff", "#1ca86a", "#f5a000", "#6c63ff", "#10243e"]
    )

    fig.add_vline(
        x=pd.to_numeric(df_plot[x_col], errors="coerce").mean(),
        line_dash="dash",
        line_color="#f5a000",
        annotation_text="Media ofensiva"
    )

    fig.add_hline(
        y=pd.to_numeric(df_plot[y_col], errors="coerce").mean(),
        line_dash="dash",
        line_color="#f5a000",
        annotation_text="Media defensiva"
    )

    fig.update_traces(marker=dict(opacity=0.75, line=dict(width=1, color="white")))
    fig.update_layout(
        xaxis_title="Índice ofensivo",
        yaxis_title="Índice defensivo",
        legend_title="Posición"
    )

    return aplicar_layout(fig, height=620)


def resumen_cards_jugadores_rs():
    if df_jugadores_rs.empty:
        return html.Div(className="chart-card", children=[
            html.H2("Jugadores Real Sociedad"),
            html.P("No se han encontrado todavía los datos de jugadores de la Real Sociedad.")
        ])

    total_jugadores = len(df_jugadores_rs)
    top_total = df_jugadores_rs.sort_values("indice_total_app", ascending=False).head(1).iloc[0]
    top_of = df_jugadores_rs.sort_values("indice_ofensivo_app", ascending=False).head(1).iloc[0]
    top_prog = df_jugadores_rs.sort_values("indice_progresion_app", ascending=False).head(1).iloc[0]
    top_def = df_jugadores_rs.sort_values("indice_defensivo_app", ascending=False).head(1).iloc[0]

    return html.Div(className="kpi-row", children=[
        card("Jugadores analizados", str(total_jugadores), "Plantilla Real Sociedad"),
        card("Perfil global", str(top_total["jugador_app"]), f"Índice total: {formato_valor(top_total['indice_total_app'])}", "verde"),
        card("Amenaza ofensiva", str(top_of["jugador_app"]), f"Índice ofensivo: {formato_valor(top_of['indice_ofensivo_app'])}", "verde"),
        card("Equilibrio defensivo", str(top_def["jugador_app"]), f"Índice defensivo: {formato_valor(top_def['indice_defensivo_app'])}", "verde"),
    ])


def tabla_jugadores_simple(df, top=20):
    if df.empty:
        return html.Div("No hay datos de jugadores disponibles.")

    cols = ["jugador_app", "equipo_app", "posicion_app", "minutos_app", "partidos_app",
            "indice_ofensivo_app", "indice_progresion_app", "indice_defensivo_app", "indice_total_app"]

    cols = [c for c in cols if c in df.columns]

    df_show = df.copy()
    if "indice_total_app" in df_show.columns:
        df_show = df_show.sort_values("indice_total_app", ascending=False)

    df_show = df_show[cols].head(top).copy()

    filas = []
    for _, row in df_show.iterrows():
        filas.append(html.Tr([
            html.Td(row.get("jugador_app", "")),
            html.Td(row.get("equipo_app", "")),
            html.Td(row.get("posicion_app", "")),
            html.Td(formato_valor(row.get("minutos_app", ""))),
            html.Td(formato_valor(row.get("partidos_app", ""))),
            html.Td(formato_valor(row.get("indice_ofensivo_app", ""))),
            html.Td(formato_valor(row.get("indice_progresion_app", ""))),
            html.Td(formato_valor(row.get("indice_defensivo_app", ""))),
            html.Td(formato_valor(row.get("indice_total_app", ""))),
        ]))

    return html.Div(
        className="tabla-wrap",
        children=[
            html.Table(
                className="tabla-clasificacion tabla-partidos",
                children=[
                    html.Thead(html.Tr([
                        html.Th("Jugador"),
                        html.Th("Equipo"),
                        html.Th("Posición"),
                        html.Th("Min."),
                        html.Th("Part."),
                        html.Th("Of."),
                        html.Th("Prog."),
                        html.Th("Def."),
                        html.Th("Total"),
                    ])),
                    html.Tbody(filas)
                ]
            )
        ]
    )






# ============================================================
# POSTPARTIDO COMPLEMENTARIO — SOFASCORE/FOTMOB
# ============================================================

RUTA_POSTPARTIDO_COMPLEMENTARIO = os.path.join(CARPETA_DATOS, "postpartido_complementario_5_partidos.csv")
df_postpartido_complementario = leer_csv_seguro(RUTA_POSTPARTIDO_COMPLEMENTARIO)


def buscar_postpartido_complementario(partido):
    if df_postpartido_complementario.empty:
        return None

    df = df_postpartido_complementario.copy()

    partido_txt = str(partido).lower()

    # 1) coincidencia exacta
    exacta = df[df["partido"].astype(str).str.lower() == partido_txt]
    if not exacta.empty:
        return exacta.iloc[0]

    # 2) coincidencia por rival/palabra clave
    claves = {
        "barcelona": "FC Barcelona",
        "barça": "FC Barcelona",
        "celta": "Real Club Celta de Vigo",
        "athletic": "Athletic Club",
        "mallorca": "RCD Mallorca",
        "osasuna": "CA Osasuna",
    }

    for clave, rival in claves.items():
        if clave in partido_txt:
            fila = df[df["rival"].astype(str).str.lower().str.contains(rival.lower().split()[0], na=False)]
            if not fila.empty:
                return fila.iloc[0]

    return None


def valor_post(row, col, default="No disponible"):
    try:
        val = row.get(col, default)
        if pd.isna(val):
            return default
        return val
    except Exception:
        return default


def card_metric_post(titulo, rs, rival, sufijo=""):
    try:
        rs_txt = f"{float(rs):.2f}{sufijo}" if rs != "No disponible" else "No disponible"
    except Exception:
        rs_txt = str(rs)

    try:
        rival_txt = f"Rival: {float(rival):.2f}{sufijo}" if rival != "No disponible" else "Rival: No disponible"
    except Exception:
        rival_txt = f"Rival: {rival}"

    return card(titulo, rs_txt, rival_txt)


def fig_postpartido_complementario(row):
    datos = []

    pares = [
        ("Posesión", "posesion_rs", "posesion_rival"),
        ("xG", "xg_rs", "xg_rival"),
        ("Tiros", "tiros_rs", "tiros_rival"),
        ("Ocasiones claras", "ocasiones_claras_rs", "ocasiones_claras_rival"),
        ("Toques área", "toques_area_rs", "toques_area_rival"),
    ]

    for nombre, col_rs, col_rival in pares:
        rs = valor_post(row, col_rs, None)
        rv = valor_post(row, col_rival, None)

        try:
            rs = float(rs)
            rv = float(rv)
        except Exception:
            continue

        datos.append({"Métrica": nombre, "Equipo": "Real Sociedad", "Valor": rs})
        datos.append({"Métrica": nombre, "Equipo": "Rival", "Valor": rv})

    df_fig = pd.DataFrame(datos)

    if df_fig.empty:
        return aplicar_layout(go.Figure(), "Comparativa postpartido", height=520)

    fig = px.bar(
        df_fig,
        x="Métrica",
        y="Valor",
        color="Equipo",
        barmode="group",
        text=df_fig["Valor"].round(2),
        title="Métricas complementarias postpartido",
        color_discrete_map={
            "Real Sociedad": "#005baa",
            "Rival": "#b8c7d9"
        }
    )

    fig.update_traces(textposition="outside")
    fig.update_layout(
        xaxis_title="Métrica",
        yaxis_title="Valor",
        legend_title=""
    )

    return aplicar_layout(fig, height=560)


def bloque_postpartido_complementario(partido):
    row = buscar_postpartido_complementario(partido)

    if row is None:
        return html.Div(className="chart-card", children=[
            html.H2("Lectura postpartido complementaria"),
            html.P("No se han encontrado métricas complementarias para este partido.")
        ])

    partido_txt = valor_post(row, "partido")
    rival = valor_post(row, "rival")
    resultado = valor_post(row, "resultado")
    tipo = valor_post(row, "tipo_partido")
    insight = valor_post(row, "insight_postpartido")
    lectura_auto = valor_post(row, "lectura_automatica")

    posesion_rs = valor_post(row, "posesion_rs")
    posesion_rival = valor_post(row, "posesion_rival")
    xg_rs = valor_post(row, "xg_rs")
    xg_rival = valor_post(row, "xg_rival")
    tiros_rs = valor_post(row, "tiros_rs")
    tiros_rival = valor_post(row, "tiros_rival")
    ocasiones_rs = valor_post(row, "ocasiones_claras_rs")
    ocasiones_rival = valor_post(row, "ocasiones_claras_rival")

    sistema_rs = valor_post(row, "sistema_real_sociedad")
    sistema_rival = valor_post(row, "sistema_rival")

    paradas_remiro = valor_post(row, "paradas_remiro")
    goles_evitados = valor_post(row, "goles_evitados_remiro")

    bloque_remiro = None

    if paradas_remiro != "No disponible" or goles_evitados != "No disponible":
        bloque_remiro = html.Div(className="chart-card", children=[
            html.H2("Factor diferencial: portero"),
            html.P(
                f"En este partido, Remiro registra {paradas_remiro} paradas y {goles_evitados} goles evitados. "
                "Este dato ayuda a explicar cómo la Real Sociedad pudo sostener el resultado pese a la superioridad rival en volumen ofensivo."
            ),
            html.Div([
                html.Span("Paradas", className="pill"),
                html.Span("Goles evitados", className="pill"),
                html.Span("Resistencia defensiva", className="pill"),
            ])
        ])

    children = [
        html.Div(className="method-card", children=[
            html.H2("Lectura postpartido con métricas complementarias"),
            html.P(
                "Estas métricas proceden de fuentes externas como SofaScore/FotMob y se utilizan como apoyo contextual. "
                "No sustituyen a la base propia del TFM, sino que enriquecen la interpretación posterior al partido."
            )
        ]),

        html.Div(className="kpi-row", children=[
            card("Resultado", str(resultado), str(partido_txt)),
            card("Tipo de partido", str(tipo), f"Rival: {rival}", "verde"),
            card("Sistema RS", str(sistema_rs), f"Rival: {sistema_rival}"),
            card("Uso", "Postpartido", "Contextualizar el rendimiento", "verde"),
        ]),

        html.Div(className="grid-2", children=[
            html.Div(className="chart-card", children=[
                dcc.Graph(figure=fig_postpartido_complementario(row))
            ]),
            html.Div(className="chart-card", children=[
                html.H2("Insight táctico"),
                html.P(str(insight)),
                html.H2("Lectura automática"),
                html.P(str(lectura_auto)),
                html.Div([
                    html.Span("Resultado", className="pill"),
                    html.Span("xG", className="pill"),
                    html.Span("Tiros", className="pill"),
                    html.Span("Área", className="pill"),
                ])
            ])
        ]),

        html.Div(className="grid-3", children=[
            html.Div(className="chart-card", children=[
                html.H2("1. Control del juego"),
                html.P(
                    f"La posesión fue {posesion_rs}% para la Real Sociedad frente a {posesion_rival}% del rival. "
                    "Este dato permite interpretar si la Real llevó la iniciativa o compitió desde un escenario más reactivo."
                )
            ]),
            html.Div(className="chart-card", children=[
                html.H2("2. Calidad de ocasiones"),
                html.P(
                    f"El xG fue {xg_rs} para la Real Sociedad y {xg_rival} para el rival. "
                    "La comparación ayuda a distinguir entre volumen ofensivo y calidad real de las oportunidades."
                )
            ]),
            html.Div(className="chart-card", children=[
                html.H2("3. Volumen ofensivo"),
                html.P(
                    f"El partido registró {tiros_rs} tiros de la Real Sociedad y {tiros_rival} del rival, "
                    f"con {ocasiones_rs} ocasiones claras para la Real y {ocasiones_rival} para el rival."
                )
            ]),
        ])
    ]

    if bloque_remiro is not None:
        children.append(bloque_remiro)

    children.append(
        html.Div(className="method-card", children=[
            html.H2("Conclusión postpartido"),
            html.P(
                "Este bloque permite cerrar el ciclo de análisis: se compara el plan previo con lo que ocurrió realmente en el partido. "
                "Así, el postpartido no se limita al resultado, sino que interpreta posesión, xG, volumen ofensivo, presencia en área y factores diferenciales."
            )
        ])
    )

    return html.Div(children)


# ============================================================
# COMPONENTE PRE/POST FINAL
# ============================================================

def bloque_prepost_final(partido):
    if df_prepost_final_tfm.empty:
        return html.Div(className="chart-card", children=[
            html.H2("Informe Pre/Post partido"),
            html.P("No se ha encontrado la tabla final de informes Pre/Post.")
        ])

    fila = df_prepost_final_tfm[df_prepost_final_tfm["partido"] == partido]

    if fila.empty:
        return html.Div(className="chart-card", children=[
            html.H2("Informe Pre/Post partido"),
            html.P("No hay ficha táctica para este partido.")
        ])

    row = fila.iloc[0]
    rival = row["rival"]

    return html.Div([
        html.Div(className="kpi-row", children=[
            card("Partido", str(row["partido"]), f"Jornada {row['jornada']}"),
            card("Rival", str(rival), str(row["perfil_rival"]), "verde"),
            card("Jugador clave", str(row["jugador_clave"]), "Amenaza individual"),
            card("Uso técnico", "Pre + Post", "Preparar, ejecutar y evaluar", "verde"),
        ]),

        html.Div(className="grid-2", children=[
            html.Div(className="chart-card", children=[
                html.H2("Contexto del partido"),
                html.P(str(row["contexto"])),
                html.Div([
                    html.Span(str(row["perfil_rival"]), className="pill"),
                    html.Span("Informe pre-partido", className="pill"),
                    html.Span("Evaluación post-partido", className="pill"),
                ])
            ]),
            html.Div(className="chart-card", children=[
                html.H2("Radar táctico del rival"),
                dcc.Graph(figure=fig_radar_rival(rival))
            ])
        ]),

        html.Div(className="grid-3", children=[
            html.Div(className="chart-card", children=[
                html.H2("1. Amenaza principal"),
                html.P(str(row["amenaza_principal"])),
            ]),
            html.Div(className="chart-card", children=[
                html.H2("2. Plan con balón"),
                html.P(str(row["plan_con_balon"])),
            ]),
            html.Div(className="chart-card", children=[
                html.H2("3. Plan sin balón"),
                html.P(str(row["plan_sin_balon"])),
            ]),
        ]),

        html.Div(className="grid-2", children=[
            html.Div(className="chart-card", children=[
                html.H2("Qué mirar en vídeo"),
                html.P(str(row["que_mirar_video"])),
                html.P("Este bloque ayuda a convertir el dato en tareas concretas de observación para el analista.")
            ]),
            html.Div(className="chart-card", children=[
                html.H2("Mensaje para cuerpo técnico"),
                html.P(str(row["mensaje_staff"])),
                html.P("Lectura breve para conectar el informe con decisiones de partido.")
            ]),
        ]),

        html.Div(className="grid-2", children=[
            html.Div(className="chart-card", children=[
                html.H2("Post-partido: cumplimiento del plan"),
                html.P(str(row["post_cumplimiento"])),
            ]),
            html.Div(className="chart-card", children=[
                html.H2("Post-partido: aprendizaje táctico"),
                html.P(str(row["post_aprendizaje"])),
            ]),
        ]),

        bloque_postpartido_complementario(partido),

        html.Div(className="method-card", children=[
            html.H2("Ciclo de análisis"),
            html.Ul([
                html.Li("Pre-partido: identificar perfil, amenaza y plan."),
                html.Li("Partido: observar si aparecen los comportamientos previstos."),
                html.Li("Post-partido: evaluar cumplimiento y extraer aprendizaje."),
                html.Li("Siguiente rival: ajustar el modelo de preparación.")
            ])
        ])
    ])


# ============================================================
# COMPONENTES HTML
# ============================================================

def card(titulo, valor, subtitulo, color="azul"):
    return html.Div(
        className=f"kpi-card {color}",
        children=[
            html.H4(titulo),
            html.H2(valor),
            html.P(subtitulo)
        ]
    )


def seccion(titulo, texto):
    return html.Div(
        className="section-intro",
        children=[
            html.H2(titulo),
            html.P(texto)
        ]
    )


def tabla_clasificacion():
    filas = []

    for _, row in df_clasificacion_laliga.iterrows():
        clase = "fila-real" if row["Equipo"] == "Real Sociedad" else ""
        zona = ""

        if row["Pos"] <= 4:
            zona = "champions"
        elif row["Pos"] <= 7:
            zona = "europa"
        elif row["Pos"] >= 18:
            zona = "descenso"

        filas.append(
            html.Tr(
                className=f"{clase} {zona}",
                children=[
                    html.Td(row["Pos"]),
                    html.Td(row["Equipo"], className="equipo-tabla"),
                    html.Td(row["PJ"]),
                    html.Td(row["G"]),
                    html.Td(row["E"]),
                    html.Td(row["P"]),
                    html.Td(row["GF"]),
                    html.Td(row["GC"]),
                    html.Td(row["DG"]),
                    html.Td(row["Pts"], className="pts-tabla"),
                ]
            )
        )

    return html.Div(
        className="tabla-wrap",
        children=[
            html.Table(
                className="tabla-clasificacion",
                children=[
                    html.Thead(html.Tr([
                        html.Th("Pos"),
                        html.Th("Equipo"),
                        html.Th("PJ"),
                        html.Th("G"),
                        html.Th("E"),
                        html.Th("P"),
                        html.Th("GF"),
                        html.Th("GC"),
                        html.Th("DG"),
                        html.Th("Pts"),
                    ])),
                    html.Tbody(filas)
                ]
            )
        ]
    )


def tabla_partidos():
    filas = []

    for _, row in df_partidos.iterrows():
        filas.append(
            html.Tr([
                html.Td(row.get("partido", "")),
                html.Td(row.get("rival", "")),
                html.Td(row.get("local", "")),
                html.Td(row.get("nivel_rival", "")),
                html.Td(formato_valor(row.get(col_pases, "")) if col_pases else ""),
                html.Td(formato_valor(row.get(col_precision, ""), sufijo="%") if col_precision else ""),
                html.Td(formato_valor(row.get(col_campo, ""), sufijo="%") if col_campo else ""),
                html.Td(formato_valor(row.get(col_zona, "")) if col_zona else ""),
                html.Td(formato_valor(row.get(col_diferencia, "")) if col_diferencia else ""),
            ])
        )

    return html.Div(
        className="tabla-wrap",
        children=[
            html.Table(
                className="tabla-clasificacion tabla-partidos",
                children=[
                    html.Thead(html.Tr([
                        html.Th("Partido"),
                        html.Th("Rival"),
                        html.Th("Condición"),
                        html.Th("Nivel"),
                        html.Th("Pases"),
                        html.Th("Precisión"),
                        html.Th("Campo rival"),
                        html.Th("Zona peligrosa"),
                        html.Th("Dif."),
                    ])),
                    html.Tbody(filas)
                ]
            )
        ]
    )


def tarjetas_partidos():
    cards = []

    for _, row in df_partidos.iterrows():
        cards.append(
            html.Div(
                className="match-card",
                children=[
                    html.H3(row.get("partido", "")),
                    html.P(f"Rival: {row.get('rival', '')} | {row.get('local', '')} | Nivel: {row.get('nivel_rival', '')}"),
                    html.Div(
                        className="match-kpis",
                        children=[
                            html.Div([html.B(formato_valor(row.get(col_pases, "-")) if col_pases else "-"), html.Span("Pases")]),
                            html.Div([html.B(formato_valor(row.get(col_precision, "-"), sufijo="%") if col_precision else "-"), html.Span("Precisión")]),
                            html.Div([html.B(formato_valor(row.get(col_campo, "-"), sufijo="%") if col_campo else "-"), html.Span("Campo rival")]),
                            html.Div([html.B(formato_valor(row.get(col_zona, "-")) if col_zona else "-"), html.Span("Zona peligrosa")]),
                        ]
                    )
                ]
            )
        )

    return html.Div(className="match-grid", children=cards)


def ranking_rivales():
    columnas = [
        ("codigo", "Código"),
        ("equipo", "Equipo"),
        ("Possession Percentage", "Posesión"),
        ("Total Passes", "Pases"),
        ("Pass Accuracy Calculated", "Precisión"),
        ("Passing % Opp Half", "% campo rival"),
        ("Total Shots", "Remates"),
        ("Goal Conversion", "Conversión"),
        ("Total Goals", "Goles"),
        ("PPDA", "PPDA"),
        ("Defensive Activity", "Act. def."),
        ("Total Shots Conceded", "Rem. conc."),
        ("Shots Conceded per Defensive Action", "Rem./act."),
        ("Set Piece Threat", "ABP"),
    ]

    cols_ok = [(c, n) for c, n in columnas if c in df_perfil_rivales.columns]

    filas = []
    for _, row in df_perfil_rivales.iterrows():
        filas.append(
            html.Tr([
                html.Td(round(num(row[c]), 2) if c not in ["codigo", "equipo"] else row[c])
                for c, _ in cols_ok
            ])
        )

    return html.Div(
        className="ranking-dark",
        children=[
            html.H2("Ranking de KPIs — rivales analizados"),
            html.P(
                "Comparativa rápida de perfiles ofensivos, estilo con balón, presión, solidez defensiva y amenaza a balón parado."
            ),
            html.Div(
                className="tabla-wrap",
                children=[
                    html.Table(
                        className="tabla-ranking",
                        children=[
                            html.Thead(html.Tr([html.Th(n) for _, n in cols_ok])),
                            html.Tbody(filas)
                        ]
                    )
                ]
            )
        ]
    )


def bloque_metodologia_archivos():
    datos = [
        ("5 partidos / dashboard", RUTA_DASHBOARD, df_dashboard),
        ("Modelo 5 partidos", RUTA_MODELO_5, df_modelo_5),
        ("Contexto 30 partidos", RUTA_CONTEXTO_30, df_contexto_30),
        ("Comparativa 5 vs 30", RUTA_COMPARATIVA_5_30, df_comparativa_5_30),
        ("Perfil táctico rivales", RUTA_PERFIL_RIVALES, df_perfil_rivales),
        ("Interpretación rivales", RUTA_INTERPRETACION_RIVALES, df_interpretacion_rivales),
        ("Resumen pre-partido rivales", RUTA_RESUMEN_PREPARTIDO, df_resumen_prepartido),
    ]

    filas = []
    for nombre, ruta, df in datos:
        filas.append(html.Tr([
            html.Td(nombre),
            html.Td(ruta),
            html.Td("Sí" if os.path.exists(ruta) else "No"),
            html.Td(f"{df.shape[0]} x {df.shape[1]}" if not df.empty else "0 x 0")
        ]))

    return html.Div(
        className="tabla-wrap",
        children=[
            html.Table(
                className="tabla-clasificacion",
                children=[
                    html.Thead(html.Tr([
                        html.Th("Bloque"),
                        html.Th("Archivo"),
                        html.Th("Existe"),
                        html.Th("Dimensiones"),
                    ])),
                    html.Tbody(filas)
                ]
            )
        ]
    )


# ============================================================
# APP
# ============================================================

app = Dash(__name__, suppress_callback_exceptions=True)
server = app.server


app.index_string = """
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>TFM Real Sociedad</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                margin: 0;
                background: #edf4fa;
                font-family: Arial, sans-serif;
                color: #08213f;
            }

            .app-container {
                max-width: 1540px;
                margin: 0 auto;
                padding: 26px;
            }

            .hero {
                border-radius: 30px;
                background:
                    radial-gradient(circle at 82% 18%, rgba(255,255,255,0.18), transparent 28%),
                    linear-gradient(135deg, #06182f 0%, #003f7f 45%, #006fd6 100%);
                color: white;
                padding: 34px 42px;
                box-shadow: 0 18px 42px rgba(0, 44, 90, 0.24);
                display: grid;
                grid-template-columns: 0.18fr 1.05fr 0.82fr;
                gap: 28px;
                align-items: center;
                margin-bottom: 22px;
                min-height: 185px;
            }

            .hero-logo {
                width: 110px;
                height: 110px;
                object-fit: contain;
                background: rgba(255,255,255,0.95);
                padding: 14px;
                border-radius: 24px;
                box-shadow: 0 12px 24px rgba(0,0,0,0.22);
            }

            .hero h1 {
                margin: 0;
                font-size: 42px;
                line-height: 1.05;
                letter-spacing: -1px;
            }

            .hero p {
                font-size: 18px;
                color: rgba(255,255,255,0.86);
                margin: 14px 0 0 0;
            }

            .hero-badges {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 12px;
            }

            .hero-badge {
                background: rgba(255,255,255,0.14);
                border: 1px solid rgba(255,255,255,0.24);
                border-radius: 18px;
                padding: 16px 12px;
                text-align: center;
            }

            .hero-badge span {
                display: block;
                font-size: 30px;
                font-weight: 900;
            }

            .hero-badge small {
                display: block;
                color: rgba(255,255,255,0.78);
                font-size: 13px;
                margin-top: 5px;
            }

            .identity-row {
                display: grid;
                grid-template-columns: 1.2fr 1fr 1fr;
                gap: 20px;
                margin: 22px 0;
            }

            .info-card,
            .section-intro,
            .chart-card,
            .selector-box,
            .kpi-card,
            .match-card {
                background: white;
                border-radius: 24px;
                border: 1px solid rgba(8,43,85,0.08);
                box-shadow: 0 9px 28px rgba(5,35,70,0.08);
            }

            .info-card {
                padding: 26px;
            }

            .info-card h2 {
                margin: 0 0 12px 0;
                font-size: 28px;
                color: #08213f;
            }

            .info-card p {
                font-size: 17px;
                line-height: 1.55;
                color: #60708c;
                margin: 0;
            }

            .mini-kpis {
                display: grid;
                grid-template-columns: repeat(5, 1fr);
                gap: 10px;
                margin-top: 20px;
            }

            .mini-kpi {
                background: #082b55;
                border-radius: 15px;
                padding: 13px 8px;
                color: white;
                text-align: center;
            }

            .mini-kpi b {
                font-size: 25px;
                display: block;
            }

            .mini-kpi span {
                font-size: 12px;
                color: rgba(255,255,255,0.75);
            }

            .kpi-row {
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 18px;
                margin: 22px 0;
            }

            .kpi-card {
                padding: 24px;
                position: relative;
                overflow: hidden;
            }

            .kpi-card:after {
                content: "";
                position: absolute;
                right: -30px;
                top: -30px;
                width: 95px;
                height: 95px;
                border-radius: 50%;
                background: rgba(0,91,170,0.08);
            }

            .kpi-card h4 {
                margin: 0 0 14px 0;
                font-size: 17px;
                color: #60708c;
            }

            .kpi-card h2 {
                margin: 0;
                font-size: 39px;
                color: #082b55;
            }

            .kpi-card p {
                margin: 10px 0 0 0;
                color: #60708c;
                font-size: 16px;
            }

            .kpi-card.verde h2 {
                color: #18a84f;
            }

            .kpi-card.rojo h2 {
                color: #d94141;
            }

            .section-intro {
                padding: 30px;
                margin: 26px 0 20px 0;
            }

            .section-intro h2 {
                font-size: 34px;
                margin: 0 0 10px 0;
            }

            .section-intro p {
                margin: 0;
                color: #60708c;
                font-size: 19px;
                line-height: 1.55;
            }

            .chart-card {
                padding: 28px;
                margin: 20px 0;
            }

            .chart-card h2 {
                font-size: 30px;
                margin: 0 0 12px 0;
            }

            .chart-card h3 {
                font-size: 23px;
                margin: 20px 0 8px 0;
            }

            .chart-card p {
                font-size: 17px;
                line-height: 1.55;
                color: #60708c;
            }

            .grid-2 {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
            }

            .grid-3 {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 20px;
            }

            .selector-box {
                padding: 22px;
                margin: 20px 0;
            }

            .selector-box h3 {
                margin: 0 0 12px 0;
                font-size: 22px;
            }

            .tabs {
                margin-top: 24px;
            }

            .tabla-wrap {
                width: 100%;
                overflow-x: auto;
                margin-top: 20px;
            }

            .tabla-clasificacion {
                width: 100%;
                border-collapse: collapse;
                font-size: 15px;
                background: white;
                border-radius: 18px;
                overflow: hidden;
            }

            .tabla-clasificacion th {
                background: #082b55;
                color: white;
                padding: 14px 12px;
                text-align: left;
            }

            .tabla-clasificacion td {
                padding: 13px 12px;
                border-bottom: 1px solid #e2eaf3;
                color: #10243e;
            }

            .tabla-clasificacion tbody tr:nth-child(even) {
                background: #f3f8fc;
            }

            .fila-real {
                background: #dceeff !important;
                border-left: 6px solid #005baa;
                font-weight: 900;
            }

            .champions {
                border-left: 4px solid #1aa65b;
            }

            .europa {
                border-left: 4px solid #f5a000;
            }

            .descenso {
                border-left: 4px solid #d94141;
            }

            .equipo-tabla {
                font-weight: 700;
            }

            .pts-tabla {
                font-weight: 900;
                color: #005baa !important;
            }

            .ranking-dark {
                background: #101827;
                color: white;
                border-radius: 26px;
                padding: 32px;
                margin: 26px 0;
                box-shadow: 0 12px 34px rgba(0,0,0,0.22);
            }

            .ranking-dark h2 {
                margin: 0 0 12px 0;
                font-size: 34px;
                color: white;
            }

            .ranking-dark p {
                font-size: 17px;
                color: #c8d2e3;
                line-height: 1.5;
            }

            .tabla-ranking {
                width: 100%;
                border-collapse: collapse;
                font-size: 14px;
            }

            .tabla-ranking th {
                text-align: left;
                padding: 13px;
                background: #0b1220;
                color: white;
                border-bottom: 1px solid #2a3548;
            }

            .tabla-ranking td {
                padding: 13px;
                color: #dce6f3;
                border-bottom: 1px solid #2a3548;
            }

            .tabla-ranking tbody tr:nth-child(even) {
                background: #172236;
            }

            .pill {
                display: inline-block;
                padding: 9px 14px;
                border-radius: 999px;
                background: #e8f1fb;
                color: #005baa;
                font-weight: 800;
                margin-right: 8px;
                margin-bottom: 8px;
            }

            .badge-dif {
                background: #18a84f;
                color: white;
                border-radius: 20px;
                padding: 20px 28px;
                text-align: center;
                min-width: 150px;
            }

            .badge-dif span {
                display: block;
                font-size: 38px;
                font-weight: 900;
            }

            .badge-dif small {
                font-size: 14px;
                opacity: 0.85;
            }

            .match-grid {
                display: grid;
                grid-template-columns: repeat(5, 1fr);
                gap: 16px;
                margin: 22px 0;
            }

            .match-card {
                padding: 20px;
            }

            .match-card h3 {
                margin: 0 0 10px 0;
                font-size: 20px;
            }

            .match-card p {
                margin: 0 0 14px 0;
                color: #60708c;
                font-size: 15px;
                line-height: 1.4;
            }

            .match-kpis {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 8px;
            }

            .match-kpis div {
                background: #edf4fa;
                border-radius: 12px;
                padding: 10px;
            }

            .match-kpis b {
                display: block;
                color: #082b55;
                font-size: 20px;
            }

            .match-kpis span {
                color: #60708c;
                font-size: 12px;
            }

            .method-card {
                background: #101827;
                color: white;
                border-radius: 26px;
                padding: 30px;
                margin: 20px 0;
            }

            .method-card h2 {
                margin: 0 0 12px 0;
                color: white;
                font-size: 32px;
            }

            .method-card p,
            .method-card li {
                color: #c8d2e3;
                font-size: 17px;
                line-height: 1.55;
            }


            .rival-headline {
                display: grid;
                grid-template-columns: 1.05fr 1fr;
                gap: 20px;
                margin: 20px 0;
            }

            .rival-panel {
                background:
                    radial-gradient(circle at 95% 10%, rgba(0,163,255,0.18), transparent 26%),
                    linear-gradient(135deg, #0b1424 0%, #10243e 60%, #073b70 100%);
                color: white;
                border-radius: 26px;
                padding: 28px;
                box-shadow: 0 14px 34px rgba(4,25,50,0.22);
                min-height: 310px;
            }

            .rival-panel h2 {
                color: white;
                margin: 0 0 12px 0;
                font-size: 31px;
            }

            .rival-panel p {
                color: #d8e5f4;
                font-size: 17px;
                line-height: 1.55;
                margin: 0 0 14px 0;
            }

            .rival-panel .plan-box {
                margin-top: 18px;
                background: rgba(255,255,255,0.10);
                border: 1px solid rgba(255,255,255,0.16);
                border-radius: 18px;
                padding: 18px;
            }

            .rival-panel .plan-box h3 {
                color: white;
                margin: 0 0 8px 0;
                font-size: 22px;
            }

            .rival-summary-grid {
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 18px;
                margin: 20px 0;
            }

            .rival-summary-card {
                background: white;
                border-radius: 24px;
                padding: 22px;
                min-height: 150px;
                border: 1px solid rgba(8,43,85,0.08);
                box-shadow: 0 9px 28px rgba(5,35,70,0.08);
                position: relative;
                overflow: hidden;
            }

            .rival-summary-card:before {
                content: "";
                position: absolute;
                left: 0;
                top: 0;
                height: 5px;
                width: 100%;
                background: linear-gradient(90deg, #005baa, #00a3ff, #f5a000);
            }

            .rival-summary-card h3 {
                margin: 0 0 10px 0;
                font-size: 22px;
                color: #08213f;
            }

            .rival-summary-card p {
                margin: 0;
                color: #60708c;
                font-size: 16px;
                line-height: 1.45;
            }

            .rival-mini-kpi-grid {
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 14px;
                margin-top: 20px;
            }

            .rival-mini-kpi {
                background: rgba(255,255,255,0.11);
                border: 1px solid rgba(255,255,255,0.18);
                border-radius: 16px;
                padding: 14px 12px;
                text-align: center;
            }

            .rival-mini-kpi b {
                display: block;
                font-size: 25px;
                color: white;
                margin-bottom: 4px;
            }

            .rival-mini-kpi span {
                display: block;
                font-size: 12px;
                color: #d8e5f4;
            }

            .subsection-title {
                margin: 28px 0 10px 0;
                padding: 18px 24px;
                border-radius: 20px;
                background: linear-gradient(90deg, #ffffff, #e9f4ff);
                border: 1px solid rgba(8,43,85,0.08);
                box-shadow: 0 7px 22px rgba(5,35,70,0.06);
            }

            .subsection-title h2 {
                margin: 0;
                font-size: 29px;
                color: #08213f;
            }

            .subsection-title p {
                margin: 7px 0 0 0;
                color: #60708c;
                font-size: 16px;
                line-height: 1.45;
            }

            .rival-note {
                background: #fff7e6;
                border-left: 6px solid #f5a000;
                border-radius: 18px;
                padding: 18px 22px;
                margin: 18px 0;
                color: #6b4a00;
                font-size: 16px;
                line-height: 1.5;
            }


            @media (max-width: 1200px) {
                .hero {
                    grid-template-columns: 1fr;
                }

                .identity-row,
                .grid-2,
                .grid-3 {
                    grid-template-columns: 1fr;
                }

                .kpi-row,
                .match-grid {
                    grid-template-columns: 1fr 1fr;
                }
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
"""


app.layout = html.Div(
    className="app-container",
    children=[
        html.Div(
            className="hero",
            children=[
                html.Div([
                    html.Img(src=RUTA_ESCUDO, className="hero-logo")
                ]),
                html.Div([
                    html.H1("Análisis de juego — Real Sociedad"),
                    html.P("TFM | Temporada 2025/26 | Eventing + KPIs ofensivos | Herramienta de apoyo al cuerpo técnico")
                ]),
                html.Div(
                    className="hero-badges",
                    children=[
                        html.Div([html.Span("30"), html.Small("partidos referencia")], className="hero-badge"),
                        html.Div([html.Span("5"), html.Small("partidos profundizados")], className="hero-badge"),
                        html.Div([html.Span("10ª"), html.Small("posición final")], className="hero-badge"),
                        html.Div([html.Span(str(len(df_perfil_rivales))), html.Small("rivales analizados")], className="hero-badge"),
                    ]
                )
            ]
        ),

        html.Div(
            className="identity-row",
            children=[
                html.Div(
                    className="info-card",
                    children=[
                        html.H2("Contexto del proyecto"),
                        html.P(
                            "La herramienta analiza el comportamiento ofensivo de la Real Sociedad a partir de datos de eventing. "
                            "El objetivo es transformar eventos de partido en KPIs interpretables para estudiar modelo de juego, rendimiento contextual y preparación de rivales."
                        ),
                        html.Div(
                            className="mini-kpis",
                            children=[
                                html.Div([html.B("46"), html.Span("puntos")], className="mini-kpi"),
                                html.Div([html.B("59"), html.Span("GF")], className="mini-kpi"),
                                html.Div([html.B("61"), html.Span("GC")], className="mini-kpi"),
                                html.Div([html.B("-2"), html.Span("DG")], className="mini-kpi"),
                                html.Div([html.B("10ª"), html.Span("Liga")], className="mini-kpi"),
                            ]
                        )
                    ]
                ),
                html.Div(
                    className="info-card",
                    children=[
                        html.H2("Muestra y profundidad"),
                        html.P(
                            "El modelo se contextualiza con 30 partidos disponibles y se profundiza en un bloque de 5 partidos. "
                            "Así se separa la referencia general de la aplicación práctica pre/post partido."
                        )
                    ]
                ),
                html.Div(
                    className="info-card",
                    children=[
                        html.H2("Aplicación práctica"),
                        html.P(
                            "El dashboard permite revisar modelo de juego, ficha de partido, comparativa 5 vs 30, contexto competitivo, análisis de rivales, pre/post partido y conclusiones estratégicas."
                        )
                    ]
                ),
            ]
        ),

        html.Div(
            className="kpi-row",
            children=[
                card("Partidos referencia", "30", "Base contextual del modelo"),
                card("Media pases", f"{media_pases:.1f}", "Volumen medio en bloque profundo"),
                card("Precisión media", f"{media_precision:.2f}%", "Calidad de pase"),
                card("Zona peligrosa", f"{media_zona:.2f}", "Llegadas / pases de amenaza"),
            ]
        ),

        dcc.Tabs(
            id="tabs",
            value="modelo",
            className="tabs",
            children=[
                dcc.Tab(label="Modelo de juego", value="modelo"),
                dcc.Tab(label="Ficha de partido", value="ficha"),
                dcc.Tab(label="Comparativa 5 vs 30", value="comparativa"),
                dcc.Tab(label="Contexto temporada", value="contexto"),
                dcc.Tab(label="Jugadores Real Sociedad", value="jugadores_rs"),
                dcc.Tab(label="Jugadores LaLiga", value="jugadores_laliga"),
                dcc.Tab(label="Análisis rival", value="rival"),
                dcc.Tab(label="Pre/Post partido", value="prepost"),
                dcc.Tab(label="DAFO", value="dafo"),
                dcc.Tab(label="Metodología", value="metodologia"),
            ]
        ),

        html.Div(id="contenido-tab")
    ]
)






# ============================================================
# COMPARATIVA 5 vs 30 REAL
# ============================================================

RUTA_COMPARATIVA_5_30_REAL = os.path.join(CARPETA_DATOS, "comparativa_5_vs_30_real_app.csv")
df_comparativa_5_30_real = leer_csv_seguro(RUTA_COMPARATIVA_5_30_REAL)


# ============================================================
# FICHA DE PARTIDO PRO + COMPARATIVA 5 vs 30 PRO
# ============================================================

def valor_fila(row, col, default=0):
    try:
        if col in row.index:
            return row[col]
        return default
    except Exception:
        return default


def numero_seguro(x, default=0):
    try:
        return float(x)
    except Exception:
        return default


def texto_estado_diferencia(valor):
    try:
        valor = float(valor)
    except Exception:
        return "Sin dato"

    if valor > 5:
        return "Por encima del patrón"
    elif valor < -5:
        return "Por debajo del patrón"
    else:
        return "Similar al patrón"


def fig_kpis_partido_pro(row):
    metricas = [
        {"KPI": "Pases", "Valor": numero_seguro(valor_fila(row, "pases_totales", 0))},
        {"KPI": "Precisión", "Valor": numero_seguro(valor_fila(row, "precision_pase", 0))},
        {"KPI": "Campo rival", "Valor": numero_seguro(valor_fila(row, "pases_campo_rival_%", 0))},
        {"KPI": "Zona peligrosa", "Valor": numero_seguro(valor_fila(row, "pases_zona_peligrosa", 0))},
        {"KPI": "Eventos/min", "Valor": numero_seguro(valor_fila(row, "eventos_por_minuto", 0))},
    ]

    df_fig = pd.DataFrame(metricas)

    fig = px.bar(
        df_fig,
        x="KPI",
        y="Valor",
        text=df_fig["Valor"].round(2),
        title="KPIs principales del partido",
        color_discrete_sequence=["#005baa"]
    )

    fig.update_traces(textposition="outside")
    fig.update_layout(
        showlegend=False,
        xaxis_title="Indicador",
        yaxis_title="Valor",
    )

    return aplicar_layout(fig, height=520)


def lectura_ficha_partido(row):
    partido = str(valor_fila(row, "partido", "Partido"))
    rival = str(valor_fila(row, "rival", "Rival"))
    local = str(valor_fila(row, "local", "No disponible"))
    modelo = str(valor_fila(row, "modelo_partido", "No clasificado"))
    tipo = str(valor_fila(row, "tipo_rendimiento", "No clasificado"))

    pases = numero_seguro(valor_fila(row, "pases_totales", 0))
    precision = numero_seguro(valor_fila(row, "precision_pase", 0))
    campo = numero_seguro(valor_fila(row, "pases_campo_rival_%", 0))
    zona = numero_seguro(valor_fila(row, "pases_zona_peligrosa", 0))
    diferencia = numero_seguro(valor_fila(row, "diferencia", 0))

    texto = (
        f"El partido {partido} se interpreta como un contexto de análisis frente a {rival}. "
        f"La Real Sociedad registra {pases:.0f} pases, una precisión aproximada del {precision:.2f}% "
        f"y un {campo:.2f}% de pases en campo rival. La llegada a zona peligrosa se sitúa en {zona:.2f}, "
        f"lo que permite valorar si el dominio se transformó en amenaza real."
    )

    if diferencia > 5:
        texto += " El rendimiento del partido queda por encima del patrón habitual, lo que indica una actuación especialmente positiva dentro de la muestra."
    elif diferencia < -5:
        texto += " El rendimiento queda por debajo del patrón habitual, por lo que la ficha sirve para detectar qué fase del modelo no funcionó con normalidad."
    else:
        texto += " El rendimiento se mantiene cerca del patrón habitual, por lo que el partido ayuda a confirmar comportamientos estables del modelo."

    return texto


def layout_ficha_partido_pro(partido):
    if df_partidos.empty:
        return html.Div(className="chart-card", children=[
            html.H2("Ficha de partido"),
            html.P("No se han encontrado partidos para construir la ficha.")
        ])

    fila = df_partidos[df_partidos["partido"] == partido]

    if fila.empty:
        fila = df_partidos.head(1)

    row = fila.iloc[0]

    partido_nombre = str(valor_fila(row, "partido", partido))
    rival = str(valor_fila(row, "rival", "Rival no disponible"))
    local = str(valor_fila(row, "local", "No disponible"))
    modelo = str(valor_fila(row, "modelo_partido", "No clasificado"))
    tipo = str(valor_fila(row, "tipo_rendimiento", "No clasificado"))
    nivel = str(valor_fila(row, "nivel_rival", "No disponible"))

    pases = numero_seguro(valor_fila(row, "pases_totales", 0))
    precision = numero_seguro(valor_fila(row, "precision_pase", 0))
    campo = numero_seguro(valor_fila(row, "pases_campo_rival_%", 0))
    zona = numero_seguro(valor_fila(row, "pases_zona_peligrosa", 0))
    eventos = numero_seguro(valor_fila(row, "eventos_por_minuto", 0))
    diferencia = numero_seguro(valor_fila(row, "diferencia", 0))

    return html.Div([
        html.Div(className="selector-box", children=[
            html.H3("Selecciona un partido:"),
            dcc.Dropdown(
                id="dropdown-partido-pro",
                options=[{"label": p, "value": p} for p in df_partidos["partido"].tolist()],
                value=partido_nombre,
                clearable=False
            )
        ]),

        html.Div(className="kpi-row", children=[
            card("Partido", partido_nombre, f"{local} | Rival: {rival}"),
            card("Perfil del rival", modelo, f"Nivel rival: {nivel}", "verde"),
            card("Rendimiento", tipo, texto_estado_diferencia(diferencia)),
            card("Uso técnico", "Ficha de partido", "Del dato a la lectura táctica", "verde"),
        ]),

        html.Div(className="grid-2", children=[
            html.Div(className="chart-card", children=[
                html.H2("Lectura táctica del partido"),
                html.P(lectura_ficha_partido(row)),
                html.Div([
                    html.Span("Volumen", className="pill"),
                    html.Span("Precisión", className="pill"),
                    html.Span("Campo rival", className="pill"),
                    html.Span("Zona peligrosa", className="pill"),
                ])
            ]),
            html.Div(className="chart-card", children=[
                dcc.Graph(figure=fig_kpis_partido_pro(row))
            ])
        ]),

        html.Div(className="grid-3", children=[
            html.Div(className="chart-card", children=[
                html.H2("1. Construcción"),
                html.P(
                    f"El volumen de pase ({pases:.0f}) permite valorar si la Real fue capaz de sostener posesiones y construir ataques con continuidad."
                )
            ]),
            html.Div(className="chart-card", children=[
                html.H2("2. Progresión"),
                html.P(
                    f"El porcentaje de pases en campo rival ({campo:.2f}%) indica si la posesión se trasladó hacia zonas de mayor valor."
                )
            ]),
            html.Div(className="chart-card", children=[
                html.H2("3. Amenaza"),
                html.P(
                    f"Las acciones en zona peligrosa ({zona:.2f}) ayudan a interpretar si el dominio acabó generando situaciones ofensivas relevantes."
                )
            ]),
        ]),

        html.Div(className="grid-2", children=[
            html.Div(className="chart-card", children=[
                html.H2("Qué indica respecto al modelo"),
                html.P(
                    "Esta ficha conecta el partido concreto con el modelo general de la Real Sociedad. "
                    "No se interpreta solo el resultado, sino si el equipo fue capaz de construir, progresar, amenazar y protegerse según su patrón habitual."
                )
            ]),
            html.Div(className="chart-card", children=[
                html.H2("Uso para el analista"),
                html.P(
                    "La ficha permite preparar una revisión rápida del partido y decidir qué clips revisar después: "
                    "salida de balón, pérdidas, presencia en campo rival, llegada a zona peligrosa y respuesta tras pérdida."
                )
            ])
        ]),

        html.Div(className="method-card", children=[
            html.H2("Nota metodológica"),
            html.P(
                "El antiguo mapa conceptual ofensivo se deja de usar como evidencia principal cuando no representa acciones concretas. "
                "La ficha prioriza indicadores, lectura táctica y conexión con el modelo de juego."
            )
        ])
    ])


def medias_comparativa_pro():
    if "df_comparativa_5_30_real" in globals() and not df_comparativa_5_30_real.empty:
        df = df_comparativa_5_30_real.copy()
        for col in ["Muestra 30", "Bloque 5", "Diferencia"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        return df

    # Fallback solo si el CSV no carga
    return pd.DataFrame([
        {"KPI": "Pases", "Muestra 30": 421.6, "Bloque 5": 444.8, "Diferencia": 23.2},
        {"KPI": "Precisión", "Muestra 30": 77.01, "Bloque 5": 78.52, "Diferencia": 1.51},
        {"KPI": "Campo rival", "Muestra 30": 36.0, "Bloque 5": 38.07, "Diferencia": 2.07},
        {"KPI": "Zona peligrosa", "Muestra 30": 22.0, "Bloque 5": 25.5, "Diferencia": 3.5},
        {"KPI": "Eventos/min", "Muestra 30": 8.8, "Bloque 5": 9.02, "Diferencia": 0.22},
    ])


def fig_comparativa_5_30_pro():
    df_comp = medias_comparativa_pro()
    df_long = df_comp.melt(
        id_vars="KPI",
        value_vars=["Muestra 30", "Bloque 5"],
        var_name="Referencia",
        value_name="Valor"
    )

    fig = px.bar(
        df_long,
        x="KPI",
        y="Valor",
        color="Referencia",
        barmode="group",
        text=df_long["Valor"].round(2),
        title="Comparativa del bloque de 5 partidos frente a la muestra general",
        color_discrete_sequence=["#7aa7d9", "#005baa"]
    )

    fig.update_traces(textposition="outside")
    fig.update_layout(
        xaxis_title="KPI",
        yaxis_title="Valor medio",
        legend_title=""
    )

    return aplicar_layout(fig, height=560)


def layout_comparativa_5_30_pro():
    df_comp = medias_comparativa_pro()

    def card_diff(kpi):
        row = df_comp[df_comp["KPI"] == kpi].iloc[0]
        diff = row["Diferencia"]
        signo = "+" if diff >= 0 else ""
        texto = f"{signo}{diff:.2f} vs muestra 30"

        color = "verde" if diff >= 0 else "azul"

        return card(kpi, f"{row['Bloque 5']:.2f}", texto, color)

    lectura = (
        "Esta sección compara los cinco partidos profundizados con la referencia general de la temporada. "
        "El objetivo no es decir si la Real jugó mejor o peor solo por una media, sino detectar si el bloque analizado "
        "se comporta de forma similar al patrón habitual o si aparecen desviaciones relevantes en construcción, precisión, "
        "presencia en campo rival o amenaza."
    )

    return html.Div([
        seccion(
            "Comparativa 5 partidos vs muestra de 30",
            "Comparar el bloque de partidos profundizados frente al patrón general de la Real Sociedad."
        ),

        html.Div(className="kpi-row", children=[
            card_diff("Pases"),
            card_diff("Precisión"),
            card_diff("Campo rival"),
            card_diff("Zona peligrosa"),
        ]),

        html.Div(className="grid-2", children=[
            html.Div(className="chart-card", children=[
                dcc.Graph(figure=fig_comparativa_5_30_pro())
            ]),
            html.Div(className="chart-card", children=[
                html.H2("Lectura para cuerpo técnico"),
                html.P(lectura),
                html.P(
                    "Si el bloque de 5 partidos supera la referencia, puede indicar escenarios donde el equipo consigue activar mejor su modelo. "
                    "Si queda por debajo, ayuda a localizar fases donde el plan se deteriora."
                ),
                html.Div([
                    html.Span("Muestra 30", className="pill"),
                    html.Span("Bloque 5", className="pill"),
                    html.Span("Diferencia", className="pill"),
                    html.Span("Lectura táctica", className="pill"),
                ])
            ])
        ]),

        html.Div(className="chart-card", children=[
            html.H2("Tabla de diferencias"),
            html.P("Resumen numérico de la diferencia entre el bloque de partidos profundizados y el patrón general."),
            html.Div(
                className="tabla-wrap",
                children=[
                    html.Table(
                        className="tabla-clasificacion tabla-partidos",
                        children=[
                            html.Thead(html.Tr([
                                html.Th("KPI"),
                                html.Th("Muestra 30"),
                                html.Th("Bloque 5"),
                                html.Th("Diferencia"),
                                html.Th("Lectura")
                            ])),
                            html.Tbody([
                                html.Tr([
                                    html.Td(row["KPI"]),
                                    html.Td(formato_valor(row["Muestra 30"])),
                                    html.Td(formato_valor(row["Bloque 5"])),
                                    html.Td(formato_valor(row["Diferencia"])),
                                    html.Td(texto_estado_diferencia(row["Diferencia"]))
                                ])
                                for _, row in df_comp.iterrows()
                            ])
                        ]
                    )
                ]
            )
        ])
    ])




# ============================================================
# MODELO DE JUEGO PRO — REAL SOCIEDAD
# ============================================================

def obtener_numero_global(nombre_variable, fallback):
    try:
        if nombre_variable in globals():
            valor = globals()[nombre_variable]
            if valor is not None:
                return float(valor)
        return fallback
    except Exception:
        return fallback


def fig_modelo_juego_barras_pro():
    datos = pd.DataFrame([
        {
            "Fase": "Construcción",
            "Indicador": "Volumen de pase",
            "Valor": obtener_numero_global("media_pases", 421.6),
            "Lectura": "Capacidad para sostener posesiones y organizar ataques."
        },
        {
            "Fase": "Calidad",
            "Indicador": "Precisión",
            "Valor": obtener_numero_global("media_precision", 77.0),
            "Lectura": "Fiabilidad técnica para conservar y progresar."
        },
        {
            "Fase": "Progresión",
            "Indicador": "Campo rival",
            "Valor": obtener_numero_global("media_campo", 38.0),
            "Lectura": "Capacidad para llevar la posesión hacia zonas de mayor valor."
        },
        {
            "Fase": "Amenaza",
            "Indicador": "Zona peligrosa",
            "Valor": obtener_numero_global("media_zona", 22.0),
            "Lectura": "Llegadas o pases con potencial de generar ocasión."
        },
        {
            "Fase": "Ritmo",
            "Indicador": "Eventos/min",
            "Valor": obtener_numero_global("media_eventos", 9.0),
            "Lectura": "Actividad y ritmo general del partido."
        }
    ])

    fig = px.bar(
        datos,
        x="Fase",
        y="Valor",
        text=datos["Valor"].round(2),
        hover_data=["Indicador", "Lectura"],
        title="Modelo de juego — indicadores principales",
        color="Fase",
        color_discrete_sequence=["#005baa", "#00a3ff", "#1ca86a", "#f5a000", "#6c63ff"]
    )

    fig.update_traces(textposition="outside")
    fig.update_layout(
        showlegend=False,
        xaxis_title="Fase del juego",
        yaxis_title="Valor medio"
    )

    return aplicar_layout(fig, height=540)


def fig_modelo_juego_radar_pro():
    # Normalización visual simple para comparar fases en una escala 0-1
    pases = min(obtener_numero_global("media_pases", 421.6) / 550, 1)
    precision = min(obtener_numero_global("media_precision", 77.0) / 90, 1)
    campo = min(obtener_numero_global("media_campo", 38.0) / 60, 1)
    zona = min(obtener_numero_global("media_zona", 22.0) / 40, 1)
    eventos = min(obtener_numero_global("media_eventos", 9.0) / 12, 1)

    categorias = ["Construcción", "Precisión", "Campo rival", "Amenaza", "Ritmo"]
    valores = [pases, precision, campo, zona, eventos]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=valores + [valores[0]],
        theta=categorias + [categorias[0]],
        fill="toself",
        name="Real Sociedad",
        line=dict(color="#005baa", width=3),
        fillcolor="rgba(0, 91, 170, 0.25)"
    ))

    fig.update_layout(
        title="Perfil visual del modelo de juego",
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 1])
        ),
        showlegend=True
    )

    return aplicar_layout(fig, height=540)


def layout_modelo_juego_pro():
    pases = obtener_numero_global("media_pases", 421.6)
    precision = obtener_numero_global("media_precision", 77.0)
    campo = obtener_numero_global("media_campo", 38.0)
    zona = obtener_numero_global("media_zona", 22.0)

    return html.Div([
        seccion(
            "Modelo de juego Real Sociedad",
            "Lectura del equipo a partir de KPIs: cómo construye, cómo progresa, cómo amenaza y qué riesgos debe controlar."
        ),

        html.Div(className="kpi-row", children=[
            card("Construcción", f"{pases:.1f}", "Volumen medio de pase"),
            card("Precisión", f"{precision:.2f}%", "Calidad de circulación", "verde"),
            card("Campo rival", f"{campo:.2f}%", "Progresión territorial"),
            card("Zona peligrosa", f"{zona:.2f}", "Llegada a zonas de amenaza", "verde"),
        ]),

        html.Div(className="grid-2", children=[
            html.Div(className="chart-card", children=[
                dcc.Graph(figure=fig_modelo_juego_barras_pro())
            ]),
            html.Div(className="chart-card", children=[
                dcc.Graph(figure=fig_modelo_juego_radar_pro())
            ])
        ]),

        html.Div(className="grid-3", children=[
            html.Div(className="chart-card", children=[
                html.H2("1. Con balón"),
                html.P(
                    "La Real Sociedad busca sostener posesiones con volumen de pase y una estructura que permita progresar hacia campo rival. "
                    "El dato relevante no es solo pasar mucho, sino transformar esa circulación en avance y ventaja."
                ),
                html.Div([
                    html.Span("Volumen", className="pill"),
                    html.Span("Precisión", className="pill"),
                    html.Span("Campo rival", className="pill"),
                ])
            ]),
            html.Div(className="chart-card", children=[
                html.H2("2. Progresión y amenaza"),
                html.P(
                    "La progresión se interpreta mediante la presencia en campo rival y la llegada a zona peligrosa. "
                    "Cuando el equipo progresa pero no amenaza, aparece una alerta: dominio sin suficiente profundidad."
                ),
                html.Div([
                    html.Span("Progresión", className="pill"),
                    html.Span("Zona peligrosa", className="pill"),
                    html.Span("Eficacia", className="pill"),
                ])
            ]),
            html.Div(className="chart-card", children=[
                html.H2("3. Equilibrio tras pérdida"),
                html.P(
                    "El modelo debe valorar también cómo queda el equipo cuando pierde. "
                    "Atacar bien implica progresar con protección, evitar pérdidas interiores y poder activar presión tras pérdida."
                ),
                html.Div([
                    html.Span("Protección", className="pill"),
                    html.Span("Presión", className="pill"),
                    html.Span("Transición", className="pill"),
                ])
            ]),
        ]),

        html.Div(className="grid-2", children=[
            html.Div(className="chart-card", children=[
                html.H2("Lectura de analista"),
                html.P(
                    "La herramienta permite detectar si la Real Sociedad domina de forma productiva o si su posesión se queda en circulación sin amenaza. "
                    "La lectura clave es conectar volumen, precisión, campo rival y zona peligrosa para entender si el modelo genera valor real."
                ),
                html.P(
                    "En la defensa del TFM, esta sección sirve para presentar la identidad del equipo antes de entrar en jugadores, rivales y partidos concretos."
                )
            ]),
            html.Div(className="chart-card", children=[
                html.H2("Qué miraría el cuerpo técnico"),
                html.Ul([
                    html.Li("Si el equipo progresa con seguridad o arriesga en zonas interiores."),
                    html.Li("Si la posesión acaba en campo rival o se queda en zonas de bajo valor."),
                    html.Li("Si la llegada a zona peligrosa acompaña al volumen de pase."),
                    html.Li("Si tras pérdida el equipo queda preparado para presionar o expuesto a transición."),
                ])
            ])
        ]),

        html.Div(className="method-card", children=[
            html.H2("Conclusión del modelo"),
            html.P(
                "La Real Sociedad se analiza como un equipo que necesita equilibrar construcción, progresión y amenaza. "
                "Cuando estos tres elementos aparecen juntos, el modelo es más estable. Cuando existe volumen sin profundidad o amenaza sin protección, "
                "aparecen las principales alertas tácticas."
            )
        ])
    ])




# ============================================================
# CONTEXTO COMPETITIVO PRO — REAL SOCIEDAD
# ============================================================

def df_clasificacion_contexto_pro():
    datos = [
        {"Pos": 1, "Equipo": "FC Barcelona", "PJ": 38, "GF": 95, "GC": 36, "DG": 59, "Pts": 94},
        {"Pos": 2, "Equipo": "Real Madrid", "PJ": 38, "GF": 77, "GC": 35, "DG": 42, "Pts": 86},
        {"Pos": 3, "Equipo": "Villarreal", "PJ": 38, "GF": 72, "GC": 46, "DG": 26, "Pts": 72},
        {"Pos": 4, "Equipo": "Atlético de Madrid", "PJ": 38, "GF": 62, "GC": 44, "DG": 18, "Pts": 69},
        {"Pos": 5, "Equipo": "Real Betis", "PJ": 38, "GF": 59, "GC": 48, "DG": 11, "Pts": 60},
        {"Pos": 6, "Equipo": "Celta de Vigo", "PJ": 38, "GF": 53, "GC": 48, "DG": 5, "Pts": 54},
        {"Pos": 7, "Equipo": "Getafe", "PJ": 38, "GF": 32, "GC": 38, "DG": -6, "Pts": 51},
        {"Pos": 8, "Equipo": "Rayo Vallecano", "PJ": 38, "GF": 41, "GC": 44, "DG": -3, "Pts": 50},
        {"Pos": 9, "Equipo": "Valencia CF", "PJ": 38, "GF": 46, "GC": 55, "DG": -9, "Pts": 49},
        {"Pos": 10, "Equipo": "Real Sociedad", "PJ": 38, "GF": 59, "GC": 61, "DG": -2, "Pts": 46},
        {"Pos": 11, "Equipo": "RCD Espanyol", "PJ": 38, "GF": 43, "GC": 55, "DG": -12, "Pts": 46},
        {"Pos": 12, "Equipo": "Athletic Club", "PJ": 38, "GF": 43, "GC": 58, "DG": -15, "Pts": 45},
        {"Pos": 13, "Equipo": "Sevilla", "PJ": 38, "GF": 46, "GC": 60, "DG": -14, "Pts": 43},
        {"Pos": 14, "Equipo": "Alavés", "PJ": 38, "GF": 44, "GC": 56, "DG": -12, "Pts": 43},
        {"Pos": 15, "Equipo": "Elche CF", "PJ": 38, "GF": 49, "GC": 57, "DG": -8, "Pts": 43},
        {"Pos": 16, "Equipo": "Levante", "PJ": 38, "GF": 47, "GC": 61, "DG": -14, "Pts": 42},
        {"Pos": 17, "Equipo": "Osasuna", "PJ": 38, "GF": 44, "GC": 50, "DG": -6, "Pts": 42},
        {"Pos": 18, "Equipo": "RCD Mallorca", "PJ": 38, "GF": 47, "GC": 57, "DG": -10, "Pts": 42},
        {"Pos": 19, "Equipo": "Girona", "PJ": 38, "GF": 39, "GC": 55, "DG": -16, "Pts": 41},
        {"Pos": 20, "Equipo": "Real Oviedo", "PJ": 38, "GF": 26, "GC": 60, "DG": -34, "Pts": 29},
    ]
    return pd.DataFrame(datos)


def tabla_clasificacion_contexto_pro(df):
    filas = []

    for _, row in df.iterrows():
        equipo = str(row["Equipo"])
        clase = "fila-real" if equipo == "Real Sociedad" else ""

        filas.append(
            html.Tr(
                className=clase,
                children=[
                    html.Td(row["Pos"]),
                    html.Td(equipo),
                    html.Td(row["PJ"]),
                    html.Td(row["GF"]),
                    html.Td(row["GC"]),
                    html.Td(row["DG"]),
                    html.Td(row["Pts"]),
                ]
            )
        )

    return html.Div(
        className="tabla-wrap",
        children=[
            html.Table(
                className="tabla-clasificacion tabla-partidos",
                children=[
                    html.Thead(
                        html.Tr([
                            html.Th("Pos"),
                            html.Th("Equipo"),
                            html.Th("PJ"),
                            html.Th("GF"),
                            html.Th("GC"),
                            html.Th("DG"),
                            html.Th("Pts"),
                        ])
                    ),
                    html.Tbody(filas)
                ]
            )
        ]
    )


def fig_puntos_contexto_pro(df):
    df = df.sort_values("Pts", ascending=True).copy()
    df["Grupo"] = df["Equipo"].apply(lambda x: "Real Sociedad" if x == "Real Sociedad" else "Resto")

    fig = px.bar(
        df,
        x="Pts",
        y="Equipo",
        orientation="h",
        color="Grupo",
        text="Pts",
        title="Puntos por equipo — LaLiga 2025/26",
        color_discrete_map={
            "Real Sociedad": "#005baa",
            "Resto": "#b8c7d9"
        }
    )

    fig.update_traces(textposition="outside")
    fig.update_layout(
        xaxis_title="Puntos",
        yaxis_title="Equipo",
        legend_title="",
        showlegend=True
    )

    return aplicar_layout(fig, height=760)


def fig_balance_goles_contexto_pro(df):
    df = df.copy()
    df["Grupo"] = df["Equipo"].apply(lambda x: "Real Sociedad" if x == "Real Sociedad" else "Resto")

    fig = px.scatter(
        df,
        x="GF",
        y="GC",
        size="Pts",
        color="Grupo",
        hover_name="Equipo",
        text=df["Equipo"].where(df["Equipo"].isin(["Real Sociedad", "FC Barcelona", "Real Madrid", "Villarreal", "Real Betis", "Athletic Club"]), ""),
        title="Producción ofensiva vs goles encajados",
        color_discrete_map={
            "Real Sociedad": "#005baa",
            "Resto": "#9fb2c8"
        }
    )

    fig.add_vline(x=df["GF"].mean(), line_dash="dash", line_color="#d99940", annotation_text="Media GF")
    fig.add_hline(y=df["GC"].mean(), line_dash="dash", line_color="#d99940", annotation_text="Media GC")

    fig.update_traces(textposition="top center")
    fig.update_layout(
        xaxis_title="Goles a favor",
        yaxis_title="Goles en contra",
        legend_title=""
    )

    return aplicar_layout(fig, height=620)


def layout_contexto_competitivo_pro():
    df = df_clasificacion_contexto_pro()

    real = df[df["Equipo"] == "Real Sociedad"].iloc[0]
    media_pts = df["Pts"].mean()
    media_gf = df["GF"].mean()
    media_gc = df["GC"].mean()

    diff_pts = real["Pts"] - media_pts
    diff_gf = real["GF"] - media_gf
    diff_gc = real["GC"] - media_gc

    lectura = (
        f"La Real Sociedad termina 10ª con {int(real['Pts'])} puntos, {int(real['GF'])} goles a favor "
        f"y {int(real['GC'])} goles en contra. La lectura competitiva principal es clara: el equipo presenta "
        f"una producción ofensiva alta para su posición, pero queda condicionado por el volumen de goles encajados. "
        f"Por tanto, el análisis del modelo no debe centrarse solo en generar amenaza, sino en entender si esa amenaza "
        f"se sostiene con equilibrio defensivo."
    )

    lectura_goles = (
        f"Respecto a la media de LaLiga, la Real queda {diff_pts:.1f} puntos respecto al promedio, "
        f"{diff_gf:+.1f} goles a favor y {diff_gc:+.1f} goles encajados. "
        f"Esto sugiere un perfil de equipo capaz de producir, pero con margen claro en control defensivo y gestión de transiciones."
    )

    return html.Div([
        seccion(
            "Contexto competitivo de la temporada",
            "Diagnóstico de la Real Sociedad dentro de LaLiga: clasificación, producción ofensiva, goles encajados y lectura táctica."
        ),

        html.Div(className="kpi-row", children=[
            card("Posición", "10ª", "Clasificación final"),
            card("Puntos", str(int(real["Pts"])), f"{diff_pts:+.1f} vs media liga", "verde" if diff_pts >= 0 else "azul"),
            card("Goles a favor", str(int(real["GF"])), f"{diff_gf:+.1f} vs media liga", "verde"),
            card("Goles en contra", str(int(real["GC"])), f"{diff_gc:+.1f} vs media liga"),
            card("Diferencia", str(int(real["DG"])), "Balance competitivo"),
        ]),

        html.Div(className="grid-2", children=[
            html.Div(className="chart-card", children=[
                html.H2("Lectura competitiva"),
                html.P(lectura),
                html.Div([
                    html.Span("Contexto liga", className="pill"),
                    html.Span("Producción ofensiva", className="pill"),
                    html.Span("Alerta defensiva", className="pill"),
                ])
            ]),
            html.Div(className="chart-card", children=[
                html.H2("Muestra de trabajo"),
                html.P(
                    "La clasificación final se utiliza como marco competitivo. Los KPIs de eventing permiten analizar "
                    "el comportamiento del equipo, mientras que la tabla contextualiza el rendimiento en la realidad de LaLiga."
                ),
                html.P(
                    "Los 30 partidos sirven como referencia general del modelo. Los 5 partidos profundizados permiten aplicar "
                    "el análisis a rivales concretos y a situaciones de preparación pre/post partido."
                )
            ])
        ]),

        html.Div(className="chart-card", children=[
            html.H2("Clasificación final de LaLiga 2025/26"),
            html.P("La fila de la Real Sociedad aparece resaltada para ubicar rápidamente el contexto competitivo del equipo."),
            tabla_clasificacion_contexto_pro(df)
        ]),

        html.Div(className="grid-2", children=[
            html.Div(className="chart-card", children=[
                dcc.Graph(figure=fig_puntos_contexto_pro(df))
            ]),
            html.Div(className="chart-card", children=[
                dcc.Graph(figure=fig_balance_goles_contexto_pro(df))
            ])
        ]),

        html.Div(className="grid-3", children=[
            html.Div(className="chart-card", children=[
                html.H2("1. Qué dice la tabla"),
                html.P(
                    "La 10ª posición sitúa a la Real en una zona media de LaLiga. No es un equipo de descenso, "
                    "pero tampoco alcanza el rendimiento de los perfiles europeos de la competición."
                )
            ]),
            html.Div(className="chart-card", children=[
                html.H2("2. Fortaleza competitiva"),
                html.P(
                    "Los 59 goles a favor indican capacidad para generar o transformar ataques. Para una 10ª posición, "
                    "la producción ofensiva no es el principal problema competitivo."
                )
            ]),
            html.Div(className="chart-card", children=[
                html.H2("3. Alerta principal"),
                html.P(
                    "Los 61 goles encajados y la diferencia de -2 señalan una necesidad de mejorar el equilibrio del modelo: "
                    "cómo se protege el equipo cuando ataca y cómo gestiona pérdidas/transiciones."
                )
            ]),
        ]),

        html.Div(className="grid-2", children=[
            html.Div(className="chart-card", children=[
                html.H2("Lectura para el cuerpo técnico"),
                html.P(lectura_goles),
                html.P(
                    "El contexto competitivo ayuda a decidir qué debe priorizar el análisis posterior: no solo atacar mejor, "
                    "sino atacar quedando mejor preparado para defender."
                )
            ]),
            html.Div(className="chart-card", children=[
                html.H2("Cómo se usa en el TFM"),
                html.Ul([
                    html.Li("Primero se ubica la Real Sociedad dentro de LaLiga."),
                    html.Li("Después se analiza si sus KPIs explican esa posición competitiva."),
                    html.Li("Luego se baja al detalle: jugadores, rivales y cinco partidos profundizados."),
                    html.Li("La app convierte la tabla y los KPIs en una herramienta de diagnóstico.")
                ])
            ])
        ]),

        html.Div(className="method-card", children=[
            html.H2("Conclusión del contexto competitivo"),
            html.P(
                "La Real Sociedad combina una producción ofensiva interesante con una alerta clara en equilibrio defensivo. "
                "Esta lectura justifica que el TFM no se centre únicamente en posesión o ataque, sino en conectar modelo de juego, "
                "riesgo defensivo, perfiles de jugadores y preparación de rivales."
            )
        ])
    ])


# ============================================================
# CALLBACK PRINCIPAL
# ============================================================

@app.callback(
    Output("contenido-tab", "children"),
    Input("tabs", "value")
)
def render_tab(tab):

    if tab == "modelo":
        return layout_modelo_juego_pro()


    if tab == "ficha":
        partidos = df_partidos["partido"].tolist() if not df_partidos.empty else []
        partido_default = partidos[0] if partidos else None

        if partido_default is None:
            return html.Div([
                seccion("Ficha de partido", "No hay partidos disponibles para construir la ficha."),
                html.Div(className="chart-card", children=[
                    html.H2("Sin datos"),
                    html.P("No se han encontrado partidos en la base de datos.")
                ])
            ])

        return html.Div([
            seccion(
                "Ficha de partido",
                "Lectura visual de un partido concreto: KPIs, interpretación táctica y conexión con el modelo de juego."
            ),
            html.Div(id="bloque-ficha-pro", children=layout_ficha_partido_pro(partido_default))
        ])


    if tab == "comparativa":
        return layout_comparativa_5_30_pro()


    if tab == "contexto":
        return layout_contexto_competitivo_pro()


    if tab == "jugadores_rs":
        return html.Div([
            seccion(
                "Jugadores Real Sociedad",
                "Análisis interno de la plantilla: líderes por fase, perfiles individuales y conexión entre rendimiento del jugador y modelo de juego."
            ),

            resumen_cards_jugadores_rs(),

            html.Div(
                className="grid-2",
                children=[
                    html.Div(className="chart-card", children=[
                        dcc.Graph(figure=fig_perfil_fases_jugadores_rs())
                    ]),
                    html.Div(className="chart-card", children=[
                        html.H2("Lectura para cuerpo técnico"),
                        html.P(
                            "Esta sección permite identificar qué jugadores sostienen cada fase del modelo: amenaza ofensiva, progresión, defensa y perfil global."
                        ),
                        html.P(
                            "La idea no es valorar al jugador de forma aislada, sino entender qué aporta al funcionamiento colectivo de la Real Sociedad."
                        ),
                        html.Div([
                            html.Span("Amenaza", className="pill"),
                            html.Span("Progresión", className="pill"),
                            html.Span("Defensa", className="pill"),
                            html.Span("Perfil global", className="pill"),
                        ])
                    ])
                ]
            ),

            html.Div(className="chart-card", children=[
                dcc.Graph(figure=fig_ranking_jugadores(df_jugadores_rs, "Ranking interno — índice total jugador", top=14))
            ]),

            html.Div(className="grid-2", children=[
                html.Div(className="chart-card", children=[
                    dcc.Graph(figure=fig_ranking_jugadores(df_jugadores_rs, "Top perfiles ofensivos — Real Sociedad", top=10, metrica="indice_ofensivo_app"))
                ]),
                html.Div(className="chart-card", children=[
                    dcc.Graph(figure=fig_ranking_jugadores(df_jugadores_rs, "Top perfiles defensivos — Real Sociedad", top=10, metrica="indice_defensivo_app"))
                ]),
            ]),

            html.Div(className="chart-card", children=[
                html.H2("Tabla de apoyo — jugadores Real Sociedad"),
                html.P("Tabla resumida para consultar ranking interno. La parte visual es la prioritaria; la tabla queda como apoyo metodológico."),
                tabla_jugadores_simple(df_jugadores_rs, top=25)
            ])
        ])


    if tab == "jugadores_laliga":
        posiciones = []
        if not df_jugadores_laliga.empty and "posicion_app" in df_jugadores_laliga.columns:
            posiciones = sorted([p for p in df_jugadores_laliga["posicion_app"].dropna().astype(str).unique().tolist() if p.strip() != ""])

        opciones_pos = [{"label": "Todas las posiciones", "value": "TODAS"}] + [
            {"label": p, "value": p} for p in posiciones
        ]

        return html.Div([
            seccion(
                "Jugadores LaLiga",
                "Comparativa individual de jugadores de la competición para contextualizar perfiles propios y detectar referencias por posición."
            ),

            html.Div(className="kpi-row", children=[
                card("Jugadores analizados", str(len(df_jugadores_laliga)), "Muestra individual LaLiga"),
                card("Equipos", str(df_jugadores_laliga["equipo_app"].nunique() if not df_jugadores_laliga.empty else 0), "Clubes con datos"),
                card("Posiciones", str(len(posiciones)), "Perfiles posicionales"),
                card("Uso técnico", "Ranking + mapa", "Comparación de perfiles"),
            ]),

            html.Div(className="selector-box", children=[
                html.H3("Filtrar jugadores por posición"),
                dcc.Dropdown(
                    id="dropdown-posicion-laliga",
                    options=opciones_pos,
                    value="TODAS",
                    clearable=False
                )
            ]),

            html.Div(id="bloque-jugadores-laliga")
        ])


    if tab == "rival":
        rivales = df_perfil_rivales["equipo"].dropna().tolist()

        return html.Div([
            seccion(
                "Análisis del rival y enfoque pre-partido",
                "Bloque inspirado en informes de análisis de juego: radar táctico, quadrant plots, ranking de KPIs y lectura práctica para preparar el partido."
            ),

            html.Div(className="selector-box", children=[
                html.H3("Selecciona un rival:"),
                dcc.Dropdown(
                    id="dropdown-rival",
                    options=[{"label": r, "value": r} for r in rivales],
                    value=rivales[0],
                    clearable=False
                )
            ]),

            html.Div(id="bloque-rival")
        ])

    if tab == "prepost":
        partidos = df_prepost_final_tfm["partido"].tolist() if not df_prepost_final_tfm.empty else df_partidos["partido"].tolist()

        return html.Div([
            seccion(
                "Informe pre/post partido",
                "Este bloque conecta la herramienta con la aplicación práctica del análisis de juego: preparar el partido, evaluar lo ocurrido y extraer conclusiones útiles para el cuerpo técnico."
            ),

            html.Div(className="selector-box", children=[
                html.H3("Selecciona un partido:"),
                dcc.Dropdown(
                    id="dropdown-prepost",
                    options=[{"label": p, "value": p} for p in partidos],
                    value=partidos[0],
                    clearable=False
                )
            ]),

            html.Div(id="bloque-prepost")
        ])

    if tab == "dafo":
        return html.Div([
            seccion(
                "DAFO del proyecto",
                "Síntesis estratégica de la herramienta desarrollada: qué aporta, qué limitaciones tiene y cómo puede evolucionar."
            ),

            html.Div(className="grid-2", children=[
                html.Div(className="chart-card", children=[
                    html.H2("Fortalezas"),
                    html.P("Modelo claro y explicable, KPIs interpretables y conexión directa con el análisis táctico."),
                    html.P("Permite pasar de datos de eventos a una lectura útil para cuerpo técnico.")
                ]),
                html.Div(className="chart-card", children=[
                    html.H2("Debilidades"),
                    html.P("La calidad del análisis depende de la disponibilidad, limpieza y estructura de los datos."),
                    html.P("Algunas métricas son aproximaciones y deben complementarse con vídeo.")
                ]),
                html.Div(className="chart-card", children=[
                    html.H2("Oportunidades"),
                    html.P("Ampliar el modelo con métricas defensivas, redes de pase, mapas de tiros y datos físicos."),
                    html.P("Convertir la herramienta en un informe automatizado para staff técnico.")
                ]),
                html.Div(className="chart-card", children=[
                    html.H2("Amenazas"),
                    html.P("Cambios en las fuentes de datos, falta de contexto táctico o interpretación excesivamente automática."),
                    html.P("El dato debe apoyar al analista, no sustituir su criterio.")
                ]),
            ])
        ])

    if tab == "metodologia":
        return html.Div([
            seccion(
                "Metodología y trazabilidad del análisis",
                "Esta sección resume cómo se construye la herramienta: fuentes internas, KPIs utilizados, lógica de comparación y utilidad práctica para el TFM."
            ),

            html.Div(className="method-card", children=[
                html.H2("Flujo de trabajo"),
                html.Ul([
                    html.Li("1. Carga y limpieza de datos de eventing."),
                    html.Li("2. Transformación de eventos en KPIs ofensivos interpretables."),
                    html.Li("3. Construcción de una muestra general de 30 partidos para obtener una referencia estable."),
                    html.Li("4. Profundización en 5 partidos para aplicar el modelo con lectura pre/post partido."),
                    html.Li("5. Análisis de rivales mediante radar, quadrant plots, ranking de KPIs e interpretación táctica."),
                    html.Li("6. Visualización final en dashboard para facilitar la defensa del proyecto.")
                ])
            ]),

            html.Div(className="grid-2", children=[
                html.Div(className="chart-card", children=[
                    html.H2("KPIs principales"),
                    html.P("Pases totales: volumen de circulación del equipo."),
                    html.P("Precisión de pase: calidad técnica en la circulación."),
                    html.P("Campo rival: capacidad para instalarse en zonas avanzadas."),
                    html.P("Zona peligrosa: aproximación a zonas de amenaza."),
                    html.P("Eventos por minuto: ritmo de participación ofensiva."),
                    html.P("Diferencia contextual: desviación respecto al patrón esperado.")
                ]),
                html.Div(className="chart-card", children=[
                    html.H2("Lectura defendible"),
                    html.P(
                        "La herramienta no pretende sustituir al análisis de vídeo. Su función es ordenar el dato, detectar patrones y orientar la interpretación táctica."
                    ),
                    html.P(
                        "El valor del proyecto está en conectar datos, KPIs, visualizaciones e informes de partido dentro de un mismo flujo de análisis."
                    )
                ])
            ]),

            html.Div(className="chart-card", children=[
                html.H2("Archivos utilizados por la herramienta"),
                bloque_metodologia_archivos()
            ])
        ])

    return html.Div("Tab no encontrada.")


# ============================================================
# CALLBACK FICHA PARTIDO
# ============================================================

@app.callback(
    Output("bloque-partido", "children"),
    Input("dropdown-partido", "value")
)
def actualizar_partido(partido):
    fila = df_partidos[df_partidos["partido"] == partido]
    if fila.empty:
        fila = df_partidos.iloc[[0]]
    fila = fila.iloc[0]

    rival = fila.get("rival", "No disponible")
    condicion = fila.get("local", "No disponible")
    nivel = fila.get("nivel_rival", "Medio")
    modelo = fila.get("modelo_partido", "No clasificado")
    rendimiento = fila.get("tipo_rendimiento", "No clasificado")

    pases = fila.get(col_pases, "-") if col_pases else "-"
    precision = fila.get(col_precision, "-") if col_precision else "-"
    campo = fila.get(col_campo, "-") if col_campo else "-"
    zona = fila.get(col_zona, "-") if col_zona else "-"
    eventos = fila.get(col_eventos, "-") if col_eventos else "-"
    dif = fila.get(col_diferencia, "-") if col_diferencia else "-"

    return html.Div([
        html.Div(className="chart-card", children=[
            html.H2(partido),
            html.P(f"Rival: {rival} | Condición: {condicion} | Nivel del rival: {nivel}"),
        ]),

        html.Div(className="kpi-row", children=[
            card("Modelo táctico", str(modelo), "Clasificación del perfil de partido", "verde"),
            card("Rendimiento", str(rendimiento), "Lectura contextual", "verde"),
            card("Diferencia", formato_valor(dif), "Respecto al patrón esperado", "verde"),
            card("Ritmo", formato_valor(eventos), "Eventos por minuto"),
        ]),

        html.Div(className="kpi-row", children=[
            card("Pases totales", formato_valor(pases), "Volumen de circulación"),
            card("Precisión", formato_valor(precision, sufijo="%"), "Calidad en el pase"),
            card("Campo rival", formato_valor(campo, sufijo="%"), "Presencia ofensiva"),
            card("Zona peligrosa", formato_valor(zona), "Amenaza generada"),
        ]),

        html.Div(className="grid-2", children=[
            html.Div(className="chart-card", children=[
                dcc.Graph(figure=fig_partido_kpis(partido))
            ]),
            html.Div(className="chart-card", children=[
                dcc.Graph(figure=fig_partido_campo(partido))
            ]),
        ]),

        html.Div(className="grid-2", children=[
            html.Div(className="chart-card", children=[
                html.H2("Lectura ofensiva"),
                html.P(
                    "La ficha permite observar si el equipo sostuvo volumen de pase, progresó hacia campo rival y consiguió llegar a zonas de amenaza."
                ),
                html.P(
                    "Esta lectura debe complementarse con vídeo para identificar cómo se generaron esas situaciones."
                )
            ]),
            html.Div(className="chart-card", children=[
                html.H2("Aplicación táctica"),
                html.P(
                    "El partido se compara con la referencia media para detectar comportamientos por encima o por debajo del patrón habitual."
                ),
                html.P(
                    "El objetivo es explicar el rendimiento desde el modelo de juego, no solo desde el resultado."
                )
            ])
        ])
    ])


# ============================================================
# CALLBACK RIVAL
# ============================================================

@app.callback(
    Output("bloque-rival", "children"),
    Input("dropdown-rival", "value")
)
def actualizar_rival(equipo):
    interpretacion = df_interpretacion_rivales[df_interpretacion_rivales["equipo"] == equipo]

    if not interpretacion.empty and "interpretacion_tactica" in interpretacion.columns:
        texto_interpretacion = interpretacion.iloc[0]["interpretacion_tactica"]
    else:
        texto_interpretacion = "Lectura táctica del rival pendiente de completar."

    resumen = df_resumen_prepartido[df_resumen_prepartido["rival"] == equipo]

    if not resumen.empty:
        resumen = resumen.iloc[0]
        perfil_ofensivo = resumen.get("perfil_ofensivo", "No disponible")
        estilo = resumen.get("estilo_con_balon", "No disponible")
        perfil_defensivo = resumen.get("perfil_defensivo", "No disponible")
        amenaza = resumen.get("amenaza_principal", "No disponible")
        plan = resumen.get("plan_para_real_sociedad", "No disponible")
    else:
        perfil_ofensivo = "No disponible"
        estilo = "No disponible"
        perfil_defensivo = "No disponible"
        amenaza = "No disponible"
        plan = "No disponible"

    fila_rival = df_perfil_rivales[df_perfil_rivales["equipo"] == equipo]
    if fila_rival.empty:
        fila_rival = df_perfil_rivales.iloc[[0]]
    fila_rival = fila_rival.iloc[0]

    posesion = formato_valor(fila_rival.get("Possession Percentage", 0), sufijo="%")
    precision = formato_valor(fila_rival.get("Pass Accuracy Calculated", 0), sufijo="%")
    remates = formato_valor(fila_rival.get("Total Shots", 0))
    goles = formato_valor(fila_rival.get("Total Goals", 0))
    ppda = formato_valor(fila_rival.get("PPDA", 0))
    abp = formato_valor(fila_rival.get("Set Piece Threat", 0))
    act_def = formato_valor(fila_rival.get("Defensive Activity", 0))
    campo_rival = formato_valor(fila_rival.get("Passing % Opp Half", 0), sufijo="%")

    return html.Div([

        html.Div(
            className="rival-headline",
            children=[
                html.Div(className="chart-card", children=[
                    dcc.Graph(figure=fig_radar_rival(equipo))
                ]),

                html.Div(
                    className="rival-panel",
                    children=[
                        html.H2(f"Informe táctico — {equipo}"),
                        html.P(
                            texto_corto(texto_interpretacion, 520)
                        ),
                        html.Div(
                            className="rival-mini-kpi-grid",
                            children=[
                                html.Div([html.B(posesion), html.Span("posesión")], className="rival-mini-kpi"),
                                html.Div([html.B(precision), html.Span("precisión")], className="rival-mini-kpi"),
                                html.Div([html.B(remates), html.Span("remates")], className="rival-mini-kpi"),
                                html.Div([html.B(goles), html.Span("goles")], className="rival-mini-kpi"),
                                html.Div([html.B(campo_rival), html.Span("campo rival")], className="rival-mini-kpi"),
                                html.Div([html.B(ppda), html.Span("PPDA")], className="rival-mini-kpi"),
                                html.Div([html.B(act_def), html.Span("act. defensiva")], className="rival-mini-kpi"),
                                html.Div([html.B(abp), html.Span("ABP")], className="rival-mini-kpi"),
                            ]
                        ),
                        html.Div(
                            className="plan-box",
                            children=[
                                html.H3("Plan para la Real Sociedad"),
                                html.P(plan)
                            ]
                        )
                    ]
                )
            ]
        ),

        html.Div(
            className="rival-summary-grid",
            children=[
                html.Div(
                    className="rival-summary-card",
                    children=[
                        html.H3("Perfil ofensivo"),
                        html.P(perfil_ofensivo)
                    ]
                ),
                html.Div(
                    className="rival-summary-card",
                    children=[
                        html.H3("Estilo con balón"),
                        html.P(estilo)
                    ]
                ),
                html.Div(
                    className="rival-summary-card",
                    children=[
                        html.H3("Perfil defensivo"),
                        html.P(perfil_defensivo)
                    ]
                ),
                html.Div(
                    className="rival-summary-card",
                    children=[
                        html.H3("Amenaza principal"),
                        html.P(amenaza)
                    ]
                ),
            ]
        ),

        html.Div(
            className="subsection-title",
            children=[
                html.H2("KPIs principales del rival"),
                html.P(
                    "Resumen visual para identificar rápidamente el peso ofensivo, la calidad con balón, la amenaza y la actividad defensiva del rival seleccionado."
                )
            ]
        ),

        html.Div(className="chart-card", children=[
            dcc.Graph(figure=fig_barras_rival(equipo))
        ]),

        html.Div(
            className="subsection-title",
            children=[
                html.H2("Quadrant plots de análisis competitivo"),
                html.P(
                    "Estos gráficos permiten ubicar al rival dentro de la muestra analizada y comparar perfiles: amenaza ofensiva, estilo con balón y comportamiento defensivo."
                )
            ]
        ),

        html.Div(className="grid-2", children=[
            html.Div(className="chart-card", children=[
                dcc.Graph(figure=fig_quadrant_ofensivo()),
                html.Div(
                    className="rival-note",
                    children="Lectura: arriba y a la derecha aparecen rivales con mayor volumen de remate y mayor eficacia. Sirve para detectar amenaza ofensiva real."
                )
            ]),
            html.Div(className="chart-card", children=[
                dcc.Graph(figure=fig_quadrant_estilo()),
                html.Div(
                    className="rival-note",
                    children="Lectura: los equipos situados arriba y a la derecha combinan más posesión con más presencia en campo rival. Ayuda a preparar el tipo de defensa y presión."
                )
            ]),
        ]),

        html.Div(className="chart-card", children=[
            dcc.Graph(figure=fig_quadrant_defensivo()),
            html.Div(
                className="rival-note",
                children="Lectura: este gráfico cruza actividad defensiva y remates concedidos por acción defensiva. Permite valorar si el rival defiende mucho y cuánto concede."
            )
        ]),

        ranking_rivales()
    ])




# ============================================================
# CALLBACK JUGADORES LALIGA
# ============================================================

@app.callback(
    Output("bloque-jugadores-laliga", "children"),
    Input("dropdown-posicion-laliga", "value")
)
def actualizar_jugadores_laliga(posicion):
    df = df_jugadores_laliga.copy()

    if df.empty:
        return html.Div(className="chart-card", children=[
            html.H2("Jugadores LaLiga"),
            html.P("No se han encontrado todavía los datos de jugadores de LaLiga.")
        ])

    if posicion and posicion != "TODAS":
        df = df[df["posicion_app"].astype(str) == str(posicion)]

    return html.Div([
        html.Div(
            className="grid-2",
            children=[
                html.Div(className="chart-card", children=[
                    dcc.Graph(figure=fig_mapa_jugadores_laliga(df))
                ]),
                html.Div(className="chart-card", children=[
                    html.H2("Lectura del filtro"),
                    html.P(
                        "El filtro por posición permite comparar perfiles similares. Así se evita mezclar delanteros, defensas y centrocampistas en una misma lectura sin contexto."
                    ),
                    html.P(
                        "La utilidad principal es detectar qué jugadores destacan por amenaza, progresión, defensa o perfil global dentro de su rol."
                    ),
                    html.Div([
                        html.Span("Posición", className="pill"),
                        html.Span("Índice ofensivo", className="pill"),
                        html.Span("Índice defensivo", className="pill"),
                        html.Span("Índice total", className="pill"),
                    ])
                ])
            ]
        ),

        html.Div(className="chart-card", children=[
            dcc.Graph(figure=fig_ranking_jugadores(df, "Ranking jugadores LaLiga — índice total", top=18))
        ]),

        html.Div(className="grid-2", children=[
            html.Div(className="chart-card", children=[
                dcc.Graph(figure=fig_ranking_jugadores(df, "Top ofensivo — LaLiga", top=12, metrica="indice_ofensivo_app"))
            ]),
            html.Div(className="chart-card", children=[
                dcc.Graph(figure=fig_ranking_jugadores(df, "Top defensivo — LaLiga", top=12, metrica="indice_defensivo_app"))
            ]),
        ]),

        html.Div(className="chart-card", children=[
            html.H2("Tabla de apoyo — ranking individual"),
            html.P("Tabla resumida con los jugadores filtrados. Sirve como respaldo del análisis visual."),
            tabla_jugadores_simple(df, top=35)
        ])
    ])


# ============================================================
# CALLBACK PRE/POST
# ============================================================



# ============================================================
# CALLBACK PRE/POST FINAL 5 PARTIDOS
# ============================================================

@app.callback(
    Output("bloque-prepost", "children"),
    Input("dropdown-prepost", "value")
)
def actualizar_prepost(partido):
    return bloque_prepost_final(partido)





# ============================================================
# CALLBACK FICHA DE PARTIDO PRO
# ============================================================

@app.callback(
    Output("bloque-ficha-pro", "children"),
    Input("dropdown-partido-pro", "value")
)
def actualizar_ficha_partido_pro(partido):
    return layout_ficha_partido_pro(partido)


# ============================================================
# EJECUTAR
# ============================================================

if __name__ == "__main__":
    app.run(debug=True, port=8051)