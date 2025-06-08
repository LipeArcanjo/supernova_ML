from flask import Flask, request, jsonify
from services.api_cep_service import buscar_localizacao_por_cep
from services.api_weather_service import obter_previsao_por_coordenadas_json
from services.model_service import predict_condition

app = Flask(__name__)


def _bytes_to_str_recursive(obj):
    """
    Percorre profundamente 'obj' (que pode ser dict, list, tuple ou bytes)
    e converte qualquer instância de bytes para string utf-8.
    Retorna uma nova estrutura com todos os bytes decodificados.
    """
    if isinstance(obj, bytes):
        return obj.decode('utf-8', errors='ignore')
    elif isinstance(obj, dict):
        return {_bytes_to_str_recursive(k): _bytes_to_str_recursive(v)
                for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_bytes_to_str_recursive(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(_bytes_to_str_recursive(item) for item in obj)
    else:
        return obj


@app.route("/health", methods=["GET"])
def health_check():
    """
    Endpoint simples só para checar se a API está rodando.
    """
    return jsonify({"status": "ok"}), 200


@app.route("/consulta", methods=["POST"])
def consulta_por_cep():
    """
    Recebe JSON com { "cep": "00000000" }
    1) chama buscar_localizacao_por_cep(cep)
       • se retornar None → CEP inválido ou não encontrado → HTTP 400
       • caso contrário → pega latitude/longitude
    2) chama obter_previsao_por_coordenadas_json(lat, lon)
    3) devolve um JSON contendo:
       {
         "cep": "...",
         "location": {
             "address": "...",
             "latitude": ...,
             "longitude": ...
         },
         "weather": { ... }   # dicionário montado por obter_previsao_por_coordenadas_json
       }
    """
    data = request.get_json(force=True)
    if not data or "cep" not in data:
        return jsonify({"error": "Envie um JSON com o campo 'cep'."}), 400

    cep = data["cep"]
    # 1) tenta obter coords
    location = buscar_localizacao_por_cep(cep)
    if location is None:
        return jsonify({"error": f"Não foi possível encontrar coordenadas para o CEP '{cep}'."}), 400

    lat = location.latitude
    lon = location.longitude
    address_str = location.address

    # 2) chama serviço de previsão climática
    try:
        weather_info = obter_previsao_por_coordenadas_json(lat, lon)
    except Exception as e:
        # se der erro ao chamar Open-Meteo, devolve 502 (bad gateway)
        return jsonify({"error": "Falha ao obter dados meteorológicos.",
                        "details": str(e)
                        }), 502

    # -------------------------------------------------------------
    # Monta o dicionário completo de entrada para o modelo, usando
    # dados das chaves "current" e "general" (exceto timezone e afins).
    # -------------------------------------------------------------
    current = weather_info["current"]
    general = weather_info["general"]

    # Construir um único dict de features para o modelo:
    features = {
        # campos “current”
        "apparent_temperature": current["apparent_temperature"],
        "cloud_cover": current["cloud_cover"],
        "is_day": current["is_day"],
        "precipitation": current["precipitation"],
        "pressure_msl": current["pressure_msl"],
        "rain": current["rain"],
        "relative_humidity_2m": current["relative_humidity_2m"],
        "showers": current["showers"],
        "snowfall": current["snowfall"],
        "surface_pressure": current["surface_pressure"],
        "temperature_2m": current["temperature_2m"],
        "weather_code": current["weather_code"],
        "wind_direction_10m": current["wind_direction_10m"],
        "wind_gusts_10m": current["wind_gusts_10m"],
        "wind_speed_10m": current["wind_speed_10m"],
        # campos “general”
        "elevation": general["elevation"],
        "latitude": general["latitude"],
        "longitude": general["longitude"]
    }

    # Chamar o modelo para predizer a categoria
    try:
        categoria_predita = predict_condition(features)
    except Exception as e:
        return jsonify({
            "error": "Falha na predição do modelo.",
            "details": str(e)
        }), 500

    # Inserir "previsao_condicao_climatica" dentro de weather_info
    weather_info["previsao_condicao_climatica"] = categoria_predita

    # Montar resposta final
    response_body = {
        "cep": cep,
        "location": {
            "address": address_str,
            "latitude": lat,
            "longitude": lon
        },
        "weather": weather_info
    }

    # Garante que não haja bytes em response_body
    response_body = _bytes_to_str_recursive(response_body)

    return jsonify(response_body), 200


if __name__ == "__main__":
    # define host=0.0.0.0 se quiser testar de outro dispositivo;
    # porta 5000 por padrão
    app.run(debug=True)
