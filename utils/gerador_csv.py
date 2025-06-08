import pandas as pd
import numpy as np
import os

# 1. Descobre a pasta raiz do projeto (um nível acima de utils/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#    └─ __file__ é ".../utils/gerador_csv.py"
#    dirname(__file__) → ".../utils"
#    dirname(dirname(__file__)) → pasta raiz do projeto

# 2. Define o diretório de saída como "data/" dentro da raiz, e cria se não existir
output_dir = os.path.join(BASE_DIR, "data")
os.makedirs(output_dir, exist_ok=True)

# 3. Caminho completo para salvar o CSV
csv_path = os.path.join(output_dir, "weather_dataset_with_rules.csv")

# 4. Função que gera uma linha aleatória
def generate_random_row():
    return {
        "apparent_temperature": np.random.uniform(-30, 50),
        "cloud_cover": np.random.uniform(0, 100),
        "is_day": np.random.choice([0.0, 1.0]),
        "precipitation": np.random.uniform(0, 60),
        "pressure_msl": np.random.uniform(900, 1050),
        "rain": np.random.uniform(0, 60),
        "relative_humidity_2m": np.random.uniform(0, 100),
        "showers": np.random.uniform(0, 60),
        "snowfall": np.random.uniform(0, 30),
        "surface_pressure": np.random.uniform(900, 1050),
        "temperature_2m": np.random.uniform(-30, 50),
        "weather_code": np.random.uniform(0, 100),
        "wind_direction_10m": np.random.uniform(0, 360),
        "wind_gusts_10m": np.random.uniform(0, 60),
        "wind_speed_10m": np.random.uniform(0, 60),
        "elevation": np.random.uniform(0, 2000),
        "latitude": np.random.uniform(-90, 90),
        "longitude": np.random.uniform(-180, 180),
        "timezone": "America/Sao_Paulo",
        "timezone_abbreviation": "GMT-3",
        "utc_offset_seconds": -10800
    }

# 5. Regra de negócio revisada para categorizar
def categorize(row):
    crit = [
        row["wind_speed_10m"] >= 20,
        row["wind_gusts_10m"] >= 25,
        row["precipitation"] >= 50,
        row["snowfall"] >= 20,
        (row["temperature_2m"] <= -20) or (row["temperature_2m"] >= 45),
        row["relative_humidity_2m"] >= 95,
        row["cloud_cover"] >= 90
    ]
    if sum(crit) >= 5:
        return "Crítico (Emergência Imediata)"

    severe = [
        12 <= row["wind_speed_10m"] < 20,
        15 <= row["wind_gusts_10m"] < 25,
        30 <= row["precipitation"] < 50,
        10 <= row["snowfall"] < 20,
        (-20 <= row["temperature_2m"] < -10) or (40 < row["temperature_2m"] < 45),
        90 <= row["relative_humidity_2m"] < 95,
        75 <= row["cloud_cover"] < 90
    ]
    if sum(severe) >= 3:
        return "Severo (Alerta Vermelho)"

    moderate = [
        6 <= row["wind_speed_10m"] < 12,
        8 <= row["wind_gusts_10m"] < 15,
        10 <= row["precipitation"] < 30,
        5 <= row["snowfall"] < 10,
        (-10 <= row["temperature_2m"] < -5) or (35 < row["temperature_2m"] <= 40),
        80 <= row["relative_humidity_2m"] < 90,
        50 <= row["cloud_cover"] < 75
    ]
    if sum(moderate) >= 3:
        return "Moderado (Atenção Amarela)"

    stable = [
        2 <= row["wind_speed_10m"] < 6,
        3 <= row["wind_gusts_10m"] < 8,
        1 <= row["precipitation"] < 10,
        1 <= row["snowfall"] < 5,
        0 <= row["temperature_2m"] <= 35,
        50 <= row["relative_humidity_2m"] < 80,
        25 <= row["cloud_cover"] < 50
    ]
    if sum(stable) >= 3:
        return "Estável (Suporte Disponível)"

    return "Suave (Verde)"

# 6. Geração balanceada (1000 amostras por categoria)
n_each = 1000
counts = {cat: 0 for cat in [
    "Crítico (Emergência Imediata)",
    "Severo (Alerta Vermelho)",
    "Moderado (Atenção Amarela)",
    "Estável (Suporte Disponível)",
    "Suave (Verde)"
]}
rows = []

while any(counts[c] < n_each for c in counts):
    row = generate_random_row()
    cat = categorize(row)
    if counts[cat] < n_each:
        row["previsao_condicao_climatica"] = cat
        rows.append(row)
        counts[cat] += 1

df_final = pd.DataFrame(rows)
df_final.to_csv(csv_path, index=False)
print(f"CSV salvo em: {csv_path}")
