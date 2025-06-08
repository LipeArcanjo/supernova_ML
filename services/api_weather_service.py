import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry

# Ajustes globais pro pandas
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)


def obter_previsao_por_coordenadas_json(latitude: float, longitude: float):
    """
    Consulta a Open-Meteo (com cache e retry). Recebe latitude e longitude,
    monta a requisição, e devolve um dicionário Python com:
      - general: dados gerais (latitude, longitude, elevation, timezone, utc_offset_seconds)
      - current: dicionário com as variáveis atuais (time_local, temperature_2m, precipitation, wind_speed_10m, wind_direction_10m,
                 is_day, rain, snowfall, surface_pressure, weather_code, cloud_cover, pressure_msl, showers,
                 relative_humidity_2m, apparent_temperature, wind_gusts_10m)
    """
    # Configura sessão com cache (expira em 1h) e retry automático (até 5 tentativas)
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    # Monta URL e parâmetros usando lat/lon
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "weather_code",
        "hourly": [
            "temperature_2m",
            "weather_code",
            "rain",
            "visibility",
            "precipitation_probability",
            "precipitation",
            "snowfall"
        ],
        "current": [
            "temperature_2m",
            "precipitation",
            "wind_speed_10m",
            "wind_direction_10m",
            "is_day",
            "rain",
            "snowfall",
            "surface_pressure",
            "weather_code",
            "cloudcover",
            "pressure_msl",
            "showers",
            "relativehumidity_2m",
            "apparent_temperature",
            "windgusts_10m"
        ],
        "timezone": "auto",
        "past_days": 1,
        "forecast_days": 1
    }

    # Faz a requisição e obtém lista de respostas (normalmente só precisa do primeiro)
    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]

    # Exibe informações gerais
    print(f"Coordenadas: {response.Latitude()}°N {response.Longitude()}°E")
    print(f"Altitude: {response.Elevation()} m asl")
    print(f"Time zone: {response.Timezone()}{response.TimezoneAbbreviation()}")
    print(f"Diferença para GMT+0: {response.UtcOffsetSeconds()} segundos\n")

    info_geral = {
        "latitude": response.Latitude(),
        "longitude": response.Longitude(),
        "elevation": response.Elevation(),
        "timezone": response.Timezone(),
        "timezone_abbreviation": response.TimezoneAbbreviation(),
        "utc_offset_seconds": response.UtcOffsetSeconds()
    }

    # ------------------
    # Dados ao vivo ("current")
    current = response.Current()
    ts = current.Time()

    # Deixando o utc legível
    hora_local = pd.to_datetime(ts, unit='s').tz_localize('UTC').tz_convert('America/Sao_Paulo')

    # Cada índice em Variables() corresponde a uma das variáveis solicitadas em "current"
    current_temperature_2m        = current.Variables(0).Value()
    current_precipitation         = current.Variables(1).Value()
    current_wind_speed_10m        = current.Variables(2).Value()
    current_wind_direction_10m    = current.Variables(3).Value()
    current_is_day                = current.Variables(4).Value()
    current_rain                  = current.Variables(5).Value()
    current_snowfall              = current.Variables(6).Value()
    current_surface_pressure      = current.Variables(7).Value()
    current_weather_code          = current.Variables(8).Value()
    current_cloud_cover           = current.Variables(9).Value()
    current_pressure_msl          = current.Variables(10).Value()
    current_showers               = current.Variables(11).Value()
    current_relative_humidity_2m  = current.Variables(12).Value()
    current_apparent_temperature  = current.Variables(13).Value()
    current_wind_gusts_10m        = current.Variables(14).Value()

    # Exibe informações ao vivo
    print("\n== Dados atuais ==\n")
    print(f"Hora da última atualização: {hora_local}")
    print(f"Temperatura (2m): {current_temperature_2m}°C")
    print(f"Precipitação atual: {current_precipitation} mm")
    print(f"Velocidade do vento (10m): {current_wind_speed_10m} m/s")
    print(f"Direção do vento (10m): {current_wind_direction_10m}°\n")
    print(f"Está de dia?: {current_is_day}")
    print(f"Chuva atual: {current_rain}")
    print(f"Neve atual: {current_snowfall}")
    print(f"Pressão do solo atual: {current_surface_pressure}")
    print(f"Código de clima atual: {current_weather_code}")
    print(f"Cobertura das nuvens: {current_cloud_cover}")
    print(f"Presão de altura por nivel do mar: {current_pressure_msl}")
    print(f"Garoa atual: {current_showers}")
    print(f"Umidade relativa atual: {current_relative_humidity_2m}")
    print(f"Sensação térmica atual: {current_apparent_temperature}")
    print(f"Pico da velocidade do vento: {current_wind_gusts_10m}")

    info_atual = {
        "time_local": hora_local.isoformat(),
        "temperature_2m": current_temperature_2m,
        "precipitation": current_precipitation,
        "wind_speed_10m": current_wind_speed_10m,
        "wind_direction_10m": current_wind_direction_10m,
        "is_day": current_is_day,
        "rain": current_rain,
        "snowfall": current_snowfall,
        "surface_pressure": current_surface_pressure,
        "weather_code": current_weather_code,
        "cloud_cover": current_cloud_cover,
        "pressure_msl": current_pressure_msl,
        "showers": current_showers,
        "relative_humidity_2m": current_relative_humidity_2m,
        "apparent_temperature": current_apparent_temperature,
        "wind_gusts_10m": current_wind_gusts_10m
    }

    # Monta dicionário final
    resultado_clima = {
        "general": info_geral,
        "current": info_atual,
    }
    return resultado_clima
