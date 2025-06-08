from geopy.geocoders import Nominatim
import brazilcep


def buscar_localizacao_por_cep(cep_input: str):
    """
        Dado um CEP (string de números), busca o endereço via brazilcep e faz tentativas de
        geocodificação em três níveis (completo → sem bairro → apenas cidade) até retornar um
        objeto Location ou None, caso nenhuma tentativa encontre coordenadas.

        Retorna:
            geopy.location.Location ou None
    """
    # Pega o endereço do CEP pela api do brazilcep
    endereco = brazilcep.get_address_from_cep(cep_input)

    # Printa no console para analisar todos os parâmetros de saída em formato JSON
    print("JSON do endereço buscado na API dos correios:")
    print(endereco)
    print(f"\n-----\n")

    # Inicializa o geolocator utilizando a lib do Nominatim
    geolocator = Nominatim(user_agent="Supernova_ML")

    # Printa no console para analisar novamente mas organizado de maneira legível
    print("Endereço completo organizado de forma legível: \n")
    print(f"{endereco.get('street')}, {endereco.get('district')} - "
          f"{endereco.get('city')} - {endereco.get('uf')}, {endereco.get('cep')}")
    print(f"\n-----\n")

    # Extrai componentes básicos
    rua = endereco.get('street')  # ex: "Rua Capote Valente"
    bairro = endereco.get('district')  # ex: "Pinheiros"
    cidade = endereco.get('city')  # ex: "São Paulo"
    uf = endereco.get('uf')  # ex: "SP"
    cep = endereco.get('cep')  # ex: "05409-000"

    '''
    Dividi o código em tentativas, pois consultando a documentação oficial verifiquei que existem cidades
    pequenas que não tem "street" e "district" no retorno do JSON
    '''

    # Variavel para armazenar a saída do endereço sendo buscado pelo geopy/Nominatim → localizacao

    # 1ª tentativa: Endereço completo (Mais apropriado para uma precisão EXATA)
    end_completo = f"{rua}, {bairro}, {cidade} - {uf}, Brasil"
    localizacao = geolocator.geocode(end_completo)

    # 2ª tentativa: Vai remover o bairro e tentar de novo
    if localizacao is None:
        end_sem_bairro = f"{rua}, {cidade} - {uf}, Brasil"
        localizacao = geolocator.geocode(end_sem_bairro)

    # 3ª tentativa: vai usar apenas cidade + Brasil
    if localizacao is None:
        end_apenas_cidade = f"{cidade} - Brasil"
        localizacao = geolocator.geocode(end_apenas_cidade)

    # Se mesmo assim não encontrou em nenhuma tentativa, vai ter um aviso de erro e retornar None
    if localizacao is None:
        print("Não foi possível obter as coordenadas para esse endereço. "
              "Verifique se o CEP está correto ou se o local existe no Nominatim.")
        return None

    # Caso encontre, vai exibir o endereço completo e latitude/longitude
    print(f"Endereço encontrado: {localizacao.address}")
    print(f"(Latitude: {localizacao.latitude}, Longitude: {localizacao.longitude})\n")
    return localizacao


