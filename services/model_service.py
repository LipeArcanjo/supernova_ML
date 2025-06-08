import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score
import lightgbm as lgb
import joblib

# Caminho para o CSV de treinamento
BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # volta de services/ para a pasta raiz
CSV_PATH = os.path.join(BASE_DIR, "data", "weather_dataset_with_rules.csv")

# Nome do arquivo onde vamos salvar (pickle) o modelo já treinado
MODEL_PATH = os.path.join(BASE_DIR, "data", "weather_model_lgbm.pkl")

# Lista de colunas numéricas que usamos como FEATURES (todas as do dataset, exceto a target)
FEATURE_COLS = [
    # Campos “current”
    "apparent_temperature",
    "cloud_cover",
    "is_day",
    "precipitation",
    "pressure_msl",
    "rain",
    "relative_humidity_2m",
    "showers",
    "snowfall",
    "surface_pressure",
    "temperature_2m",
    "weather_code",
    "wind_direction_10m",
    "wind_gusts_10m",
    "wind_speed_10m",
    # Campos “general”
    "elevation",
    "latitude",
    "longitude",
    # Observação: timezone, timezone_abbreviation e utc_offset_seconds não são usados no modelo
]

TARGET_COL = "previsao_condicao_climatica"


class WeatherModelService:
    def __init__(self):
        self.label_encoder = LabelEncoder()
        self.model = None
        # Ao inicializar, tentamos carregar o modelo já treinado
        if os.path.exists(MODEL_PATH):
            self._load_model()
        else:
            # Se não existir, treinamos um novo
            self._train_and_save_model()

    def _load_model(self):
        """
        Carrega o modelo e o LabelEncoder do disco.
        """
        saved = joblib.load(MODEL_PATH)
        self.model = saved["model"]
        self.label_encoder = saved["label_encoder"]

    def _train_and_save_model(self):
        """
        Carrega o CSV, treina o modelo LightGBM e salva model + label_encoder em disco.
        Exibe relatório de métricas (AUC-ROC, precisão e recall).
        """
        # 1) Carregar CSV
        df = pd.read_csv(CSV_PATH)

        # 2) Separar X e y
        x = df[FEATURE_COLS].copy()
        y_raw = df[TARGET_COL].copy()

        # 3) Codificar labels (por exemplo: “Crítico” → 0, “Severo” → 1, etc.)
        y = self.label_encoder.fit_transform(y_raw)

        # 4) Dividir em treino e teste
        x_train, x_test, y_train, y_test = train_test_split(
            x, y, test_size=0.2, random_state=42, stratify=y
        )

        # 5) Criar Dataset do LightGBM
        lgb_train = lgb.Dataset(x_train, label=y_train)
        lgb_test = lgb.Dataset(x_test, label=y_test, reference=lgb_train)

        # 6) Definir parâmetros básicos do LightGBM
        params = {
            "objective": "multiclass",
            "num_class": len(self.label_encoder.classes_),
            "metric": "multi_logloss",
            "verbosity": -1,
            "boosting_type": "gbdt",
            "seed": 42
        }

        # 7) Treinar
        self.model = lgb.train(
            params,
            lgb_train,
            valid_sets=[lgb_train, lgb_test],
            valid_names=["train", "valid"],
            num_boost_round=100,
            callbacks=[lgb.early_stopping(stopping_rounds=10)]
        )

        # 8) Previsão no conjunto de teste
        y_pred_proba = self.model.predict(x_test)  # retorna matriz (n_samples, num_classes)
        # Para obter o rótulo predito, pegamos argmax na probabilidade
        y_pred = np.argmax(y_pred_proba, axis=1)

        # 9) Cálculo das métricas
        # 9a) AUC-ROC multiclass (one-vs-rest)
        try:
            auc_roc = roc_auc_score(y_test, y_pred_proba, multi_class="ovr")
        except ValueError:
            auc_roc = None

        # 9b) Precision / Recall por classe
        report = classification_report(
            y_test,
            y_pred,
            target_names=self.label_encoder.classes_,
            digits=4,
            output_dict=True
        )

        # 10) Exibir métricas no console
        print("=== LightGBM Training Report ===")
        if auc_roc is not None:
            print(f"AUC-ROC (multiclass ovo): {auc_roc:.4f}")
        else:
            print("AUC-ROC não pôde ser calculado (verifique o formato dos dados).")
        print("\n=== Classification Report (Precision / Recall / F1) ===")
        print(pd.DataFrame(report).transpose())

        # 11) Salvar modelo + label_encoder no disco (joblib)
        joblib.dump(
            {
                "model": self.model,
                "label_encoder": self.label_encoder
            },
            MODEL_PATH
        )
        print(f"\nModelo treinado e salvo em: {MODEL_PATH}")

    def predict_condition(self, weather_dict: dict) -> str:
        """
        Recebe um dict com as mesmas chaves numéricas de FEATURE_COLS
        (ou seja, coloque todos os campos de current + general, exceto 'timezone',
        'timezone_abbreviation', 'utc_offset_seconds' e 'previsao_condicao_climatica').

        Exemplo de weather_dict:
        {
          "apparent_temperature": 22.3,
          "cloud_cover": 12.3,
          "is_day": 1.0,
          "precipitation": 0.48,
          "pressure_msl": 902.45,
          "rain": 0.02,
          "relative_humidity_2m": 54.7,
          "showers": 0.32,
          "snowfall": 0.0,
          "surface_pressure": 989.10,
          "temperature_2m": 21.84,
          "weather_code": 98.2,
          "wind_direction_10m": 305.93,
          "wind_gusts_10m": 5.32,
          "wind_speed_10m": 17.54,
          "elevation": 145.24,
          "latitude": -74.33,
          "longitude": 130.11
        }

        Retorna a string da categoria (ex.: "Crítico (Emergência Imediata)").
        """
        # 1) Garante que o modelo esteja carregado
        if self.model is None:
            raise RuntimeError("Modelo não está carregado.")

        # 2) Monta um DataFrame com uma única linha (com as FEATURES na mesma ordem)
        x_new = pd.DataFrame([weather_dict])[FEATURE_COLS].copy()

        # 3) Predição das probabilidades
        proba = self.model.predict(x_new) # retorna array shape (1, num_classes)
        idx_pred = np.argmax(proba, axis=1)[0]  # índice da classe com maior probabilidade

        # 4) Decodifica para o rótulo original
        label_pred = self.label_encoder.inverse_transform([idx_pred])[0]
        return label_pred


# Instancia única do serviço para todo o ciclo de vida da aplicação
_model_service = WeatherModelService()

def predict_condition(weather_dict: dict) -> str:
    """
    Função conveniência para ser importada externamente.
    Devolve o rótulo predito (string) para o dicionário de atributos meteorológicos.
    """
    return _model_service.predict_condition(weather_dict)
