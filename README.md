# Supernova_ML

Repositório da solução IoT “Supernova_ML” para predição de condições climáticas a partir de um CEP.

---

## 📋 Sumário

- [Sobre o Projeto](#-sobre-o-projeto)  
- [Pré-requisitos](#-pré-requisitos)  
- [Instalação](#-instalação)
- [Como Executar](#-como-executar)  
- [Endpoints da API](#-endpoints-da-api)
- [Estrutura do Projeto](#-estrutura-do-projeto)  
- [Contribuições](#-contribuições)

---

## 🔍 Sobre o Projeto

O **Supernova_ML** é uma API em Python que recebe um CEP brasileiro, consulta condições climáticas reais e gera, via modelo de Machine Learning, um “status técnico de urgência” para previnir cenários de risco (enchentes, incêndios, frio extremo etc).  
Ideal para integrar a aplicativos comunitários que facilitem a tomada de decisões rápidas em situações de emergência.

---

## ⚙️ Pré-requisitos

- Python 3.8 ou superior  
- Git  
- (Opcional) [virtualenv](https://virtualenv.pypa.io/)  

---

## 📦 Instalação

1. **Clone o repositório**  
   ```bash
   git clone https://github.com/LipeArcanjo/supernova_ML.git
   cd supernova_ML

2. Crie e ative um ambiente virtual
   ```bash
   python3 -m venv venv
   source venv/bin/activate    # Linux / macOS
   venv\Scripts\activate       # Windows
   
3. Instale as dependências
   ```bash
   pip install -r requirements.txt
   
## ▶️ Como Executar

1. Se diriga ao arquivo api/app.py

2. Utilize o atalho Ctrl+Shift+F10 para iniciar o app

3. Você deve receber um retorno com: http://127.0.0.1:5000

4. Com isso, acesse o postman (para testes) e escreva a porta acima com as rotas desejadas (Se atentando aos metódos selecionados)

## 🚀 Endpoints da API

### GET /health

Verifica se a API está no ar.

- Request
   ```
  http://localhost:8000/health
  
- Response
   ```
   {
  "status": "ok"
   }
  
### POST /consulta

Prediz as condições climáticas técnicas a partir de um CEP.

- Request
   ```
  {
  "cep": "01311000"
   }
  
- Response
   ```
   {
    "cep": "01311000",
    "location": {
        "address": "Avenida Paulista, Morro dos Ingleses, Bela Vista, São Paulo, Região Imediata de São Paulo, Região Metropolitana de São Paulo, São Paulo, Região Sudeste, 04001-080, Brasil",
        "latitude": -23.5681514,
        "longitude": -46.6482451
    },
    "weather": {
        "current": {
            "apparent_temperature": 18.366695404052734,
            "cloud_cover": 100.0,
            "is_day": 0.0,
            "precipitation": 0.0,
            "pressure_msl": 1015.7999877929688,
            "rain": 0.0,
            "relative_humidity_2m": 100.0,
            "showers": 0.0,
            "snowfall": 0.0,
            "surface_pressure": 922.1760864257812,
            "temperature_2m": 16.350000381469727,
            "time_local": "2025-06-08T06:00:00-03:00",
            "weather_code": 45.0,
            "wind_direction_10m": 236.30990600585938,
            "wind_gusts_10m": 3.5999999046325684,
            "wind_speed_10m": 1.2979984283447266
        },
        "general": {
            "elevation": 827.0,
            "latitude": -23.5,
            "longitude": -46.625,
            "timezone": "America/Sao_Paulo",
            "timezone_abbreviation": "GMT-3",
            "utc_offset_seconds": -10800
        },
        "previsao_condicao_climatica": "Estável (Suporte Disponível)"
    }
   }
  
## 📁 Estrutura do Projeto

      supernova_ML/
      ├── api/           
      │   └── app.py     # Código da API (Flask)
      ├── data/          # Modelo treinado (pickle) e datasets
      ├── services/      # Lógicas de API (Cep e Weather) e predição ML
      ├── utils/         # Funções auxiliares (ex.: gerador de CSV)
      └── requirements.txt # Dependências

## 🤝 Contribuições

1. Faça um fork

2. Crie uma branch (git checkout -b feature/nova-funcionalidade)

3. Commit suas alterações (git commit -m 'Adiciona nova funcionalidade')

4. Dê um push (git push origin feature/nova-funcionalidade)

5. Abra um Pull Request




