# -*- coding: utf-8 -*-
import math
import urllib.request
import urllib.parse
import json
import time

# ==============================================================================
# PASSO 1: DATA LAYER (ESTRUTURA DE DADOS DAS AGÊNCIAS LOCALIZA SP)
# ==============================================================================
AGENCIAS_LOCALIZA_SP = {
    "CAPITAL": {
        "CENTRO": [
            {"nome": "Localiza Consolação", "endereco": "Rua Consolação, 323", "lat": -23.5489, "lon": -46.6432},
            {"nome": "Localiza República", "endereco": "Avenida Ipiranga, 210", "lat": -23.5432, "lon": -46.6410},
            {"nome": "Localiza Alameda Santos", "endereco": "Alameda Santos, 1826", "lat": -23.5619, "lon": -46.6582}
        ],
        "NORTE": [
            {"nome": "Localiza Santana", "endereco": "Avenida Cruzeiro do Sul, 1800", "lat": -23.5042, "lon": -46.6234},
            {"nome": "Localiza Vila Guilherme", "endereco": "Avenida Morvan Dias de Figueiredo, 3177", "lat": -23.5189, "lon": -46.5980},
            {"nome": "Localiza Tucuruvi", "endereco": "Avenida Tucuruvi, 500", "lat": -23.4802, "lon": -46.6034}
        ],
        "SUL": [
            {"nome": "Localiza Congonhas (Aeroporto)", "endereco": "Rua Otávio Tarquínio de Souza, 377", "lat": -23.6231, "lon": -46.6645},
            {"nome": "Localiza Santo Amaro", "endereco": "Avenida Adolfo Pinheiro, 684", "lat": -23.6450, "lon": -46.7020},
            {"nome": "Localiza Giovanni Gronchi", "endereco": "Avenida Giovanni Gronchi, 5930", "lat": -23.6291, "lon": -46.7321},
            {"nome": "Localiza Ibirapuera", "endereco": "Avenida Ibirapuera, 3103", "lat": -23.5981, "lon": -46.6610},
            {"nome": "Localiza Interlagos", "endereco": "Avenida Interlagos, 5800", "lat": -23.6912, "lon": -46.6980}
        ],
        "LESTE": [
            {"nome": "Localiza Tatuapé", "endereco": "Avenida Celso Garcia, 4000", "lat": -23.5350, "lon": -46.5750},
            {"nome": "Localiza Itaquera", "endereco": "Avenida José Pinheiro Borges, s/n", "lat": -23.5342, "lon": -46.4710},
            {"nome": "Localiza Aricanduva", "endereco": "Avenida Aricanduva, 5555", "lat": -23.5810, "lon": -46.5120},
            {"nome": "Localiza Penha", "endereco": "Avenida Airton Pretini, 499", "lat": -23.5220, "lon": -46.5410}
        ],
        "OESTE": [
            {"nome": "Localiza Barra Funda", "endereco": "Rua Jornalista Aloysio Biondi, 556", "lat": -23.5262, "lon": -46.6669},
            {"nome": "Localiza Pinheiros", "endereco": "Avenida Rebouças, 955", "lat": -23.5689, "lon": -46.6801},
            {"nome": "Localiza Butantã", "endereco": "Avenida Professor Francisco Morato, 2718", "lat": -23.5852, "lon": -46.7214},
            {"nome": "Localiza Lapa", "endereco": "Avenida Ermano Marchetti, 800", "lat": -23.5180, "lon": -46.7010}
        ]
    },
    "LITORAL": {
        "SUL": [
            {"nome": "Localiza Santos - Centro", "endereco": "Avenida Ana Costa, 200", "lat": -23.9554, "lon": -46.3315},
            {"nome": "Localiza São Vicente", "endereco": "Avenida Presidente Wilson, 213", "lat": -23.9715, "lon": -46.3820},
            {"nome": "Localiza Praia Grande - Centro", "endereco": "Avenida Presidente Kennedy, 1500", "lat": -24.0112, "lon": -46.4250},
            {"nome": "Localiza Praia Grande - Tude Bastos", "endereco": "Terminal Rodoviário Tude Bastos", "lat": -24.0080, "lon": -46.4110},
            {"nome": "Localiza Itanhaém", "endereco": "Avenida Jaime de Castro", "lat": -24.1780, "lon": -46.7820},
            {"nome": "Localiza Peruíbe", "endereco": "Avenida Padre Anchieta, 1200", "lat": -24.3180, "lon": -46.9910}
        ],
        "NORTE": [
            {"nome": "Localiza Caraguatatuba", "endereco": "Avenida Prestes Maia, 300", "lat": -23.6225, "lon": -45.4121},
            {"nome": "Localiza São Sebastião", "endereco": "Avenida Guarda Mor Lobo Viana, 500", "lat": -23.8012, "lon": -45.4010},
            {"nome": "Localiza Ubatuba", "endereco": "Avenida Iperoig, 150", "lat": -23.4340, "lon": -45.0680},
            {"nome": "Localiza Ilhabela", "endereco": "Avenida Princesa Isabel, 1200", "lat": -23.8150, "lon": -45.3610}
        ]
    },
    "INTERIOR": {
        "CAMPINAS_E_REGIAO": [
            {"nome": "Localiza Campinas - Aeroporto Viracopos", "endereco": "Rodovia Santos Dumont, km 66", "lat": -23.0084, "lon": -47.1397},
            {"nome": "Localiza Campinas - Centro", "endereco": "Avenida Francisco Glicério, 1800", "lat": -22.9020, "lon": -47.0580},
            {"nome": "Localiza Indaiatuba", "endereco": "Avenida Visconde de Indaiatuba, 850", "lat": -23.1020, "lon": -47.2110},
            {"nome": "Localiza Americana", "endereco": "Avenida Brasil, 1200", "lat": -22.7410, "lon": -47.3320}
        ],
        "VALE_DO_PARAIBA": [
            {"nome": "Localiza São José dos Campos - Centro", "endereco": "Avenida Deputado Benedito Matarazzo, 5701", "lat": -23.2010, "lon": -45.8840},
            {"nome": "Localiza Taubaté", "endereco": "Avenida Charles Schnneider, 1300", "lat": -23.0180, "lon": -45.5520}
        ],
        "SOROCABA_E_REGIAO": [
            {"nome": "Localiza Sorocaba - Campolim", "endereco": "Avenida Antônio Carlos Comitre, 80", "lat": -23.5280, "lon": -47.4640},
            {"nome": "Localiza Itu", "endereco": "Avenida Dr. Otaviano Pereira Mendes, 500", "lat": -23.2640, "lon": -47.3010}
        ],
        "RIBEIRAO_PRETO_E_REGIAO": [
            {"nome": "Localiza Ribeirão Preto - Aeroporto", "endereco": "Avenida Thomaz Alberto Whately, s/n", "lat": -21.1350, "lon": -47.7780},
            {"nome": "Localiza Franca", "endereco": "Avenida Dr. Ismael Alonso Y Alonso, 1800", "lat": -20.5380, "lon": -47.4010}
        ],
        "SAO_JOSE_DO_RIO_PRETO": [
            {"nome": "Localiza São José do Rio Preto - Aeroporto", "endereco": "Avenida Estudantes, s/n", "lat": -20.8090, "lon": -49.3980}
        ],
        "OESTE_PAULISTA": [
            {"nome": "Localiza Bauru", "endereco": "Avenida Nações Unidas, 20-30", "lat": -22.3210, "lon": -49.0710},
            {"nome": "Localiza Marília", "endereco": "Rua Brigadeiro Eduardo Gomes, 1519", "lat": -22.2240, "lon": -49.9320},
            {"nome": "Localiza Presidente Prudente", "endereco": "Avenida Manoel Goulart, 1784", "lat": -22.1210, "lon": -51.3820}
        ],
        "CENTRO_SUL_PAULISTA": [
            {"nome": "Localiza Piracicaba", "endereco": "Rua Edu Chaves, 1806", "lat": -22.7230, "lon": -47.6410},
            {"nome": "Localiza Jundiaí", "endereco": "Avenida Nove de Julho, 1500", "lat": -23.1890, "lon": -46.8840}
        ]
    }
}

# ==============================================================================
# PASSO 2 & 3: MOTOR GEOSERVICE + INTEGRATION LAYER (GEOCODING API)
# ==============================================================================
class GeoService:
    LIMITES_PERIMETRO = {
        "Capital": (2.0, 20.0),
        "Litoral": (2.0, 10.0),
        "Interior": (2.0, 5.0)
    }

    @staticmethod
    def haversine(lat1, lon1, lat2, lon2):
        """Calcula a distância real em km usando a fórmula de Haversine."""
        R = 6371.0 # Raio médio do planeta Terra em km
        
        lat1_rad, lon1_rad = math.radians(lat1), math.radians(lon1)
        lat2_rad, lon2_rad = math.radians(lat2), math.radians(lon2)
        
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c

    @classmethod
    def obter_coordenadas_por_endereco(cls, endereco):
        """
        Consome a API pública e segura do OpenStreetMap (Nominatim) para geocodificar
        o endereço recebido e retornar uma tupla (lat, lon) em float.
        """
        # CTO Best Practice: Definindo um User-Agent exclusivo para respeitar a política de uso do OSM
        headers = {
            'User-Agent': 'LocalizaGeoServiceEngine/2.0 (senior_dev_system@empresa.com)'
        }
        
        # Codifica o endereço para formato de URL válida (trata acentos, espaços, etc)
        endereco_encoded = urllib.parse.quote(endereco)
        url = f"https://nominatim.openstreetmap.org/search?q={endereco_encoded}&format=json&limit=1"
        
        try:
            req = urllib.request.Request(url, headers=headers)
            # Timeout de 5s para evitar que a aplicação trave se a rede falhar
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode('utf-8'))
                
                if data:
                    lat = float(data[0]['lat'])
                    lon = float(data[0]['lon'])
                    return lat, lon
                else:
                    return None
        except Exception as e:
            # CTO Safe Gate: Captura qualquer erro de rede sem derrubar o microserviço
            print(f"[GEOCODING ERROR] Falha ao geocodificar o endereço '{endereco}': {e}")
            return None

    @classmethod
    def obter_todas_agencias(cls):
        """Varre o dicionário estruturado e devolve uma lista unificada."""
        lista_completa = []
        for zona, agencias in AGENCIAS_LOCALIZA_SP["CAPITAL"].items():
            for ag in agencias:
                lista_completa.append({"regiao": "Capital", "sub_regiao": zona, **ag})
                
        for costa, agencias in AGENCIAS_LOCALIZA_SP["LITORAL"].items():
            for ag in agencias:
                lista_completa.append({"regiao": "Litoral", "sub_regiao": costa, **ag})
                
        for interior_reg, agencias in AGENCIAS_LOCALIZA_SP["INTERIOR"].items():
            for ag in agencias:
                lista_completa.append({"regiao": "Interior", "sub_regiao": interior_reg, **ag})
                
        return lista_completa

    @classmethod
    def filtrar_agencias_no_perimetro(cls, lat_candidato, lon_candidato):
        """Varre todas as agências aplicando as restrições estritas de perímetro."""
        agencias = cls.obter_todas_agencias()
        agencias_validas = []
        
        for ag in agencias:
            distancia = cls.haversine(lat_candidato, lon_candidato, ag["lat"], ag["lon"])
            regiao = ag["regiao"]
            
            limite_min, limite_max = cls.LIMITES_PERIMETRO.get(regiao, (0.0, float('inf')))
            
            if limite_min <= distancia <= limite_max:
                ag_com_distancia = ag.copy()
                ag_com_distancia["distancia_calculada"] = distancia
                agencias_validas.append(ag_com_distancia)
                
        agencias_validas.sort(key=lambda x: x["distancia_calculada"])
        return agencias_validas


# ==============================================================================
# PIPELINE COMPLETA DE EXECUÇÃO END-TO-END
# ==============================================================================
if __name__ == "__main__":
    print("=" * 80)
    print("SISTEMA CORPORATIVO LOCALIZA GEOSERVICE - PIPELINE INICIADO")
    print("=" * 80)
    
    # Endereços de testes (Podem ser CEPs ou endereços de texto livre)
    enderecos_teste = [
        # Teste 1: Candidato no Centro de São Paulo (Deverá cair na regra da Capital: 2km a 20km)
        "Avenida Paulista, 1578, Bela Vista, São Paulo - SP",
        
        # Teste 2: Candidato em Santos (Deverá cair na regra do Litoral: 2km a 10km)
        "Avenida Vicente de Carvalho, Boqueirão, Santos - SP",
        
        # Teste 3: Candidato no Interior - Campinas (Deverá cair na regra do Interior: 2km a 5km)
        "Rua Barão de Jaguara, Centro, Campinas - SP"
    ]
    
    for i, endereco in enumerate(enderecos_teste, 1):
        print(f"\n--- [EXECUÇÃO DO PIPELINE {i}] ---")
        print(f"Endereço de entrada: '{endereco}'")
        print("Buscando coordenadas via Geocoding API...")
        
        coordenadas = GeoService.obter_coordenadas_por_endereco(endereco)
        
        if coordenadas:
            lat, lon = coordenadas
            print(f"-> Coordenadas obtidas: Lat {lat:.6f} / Lon {lon:.6f}")
            
            # Processamento matemático de perímetros
            print("Processando regras de perímetro de negócios...")
            agencias_recomendadas = GeoService.filtrar_agencias_no_perimetro(lat, lon)
            
            if agencias_recomendadas:
                print(f"-> SUCESSO: {len(agencias_recomendadas)} agência(s) encontrada(s) no perímetro!")
                for index, ag in enumerate(agencias_recomendadas[:3], 1): # Exibe as top 3
                    print(f"   [{index}] {ag['nome']}")
                    print(f"       Setor: {ag['regiao']} | Zona/Sub: {ag['sub_regiao']}")
                    print(f"       Distância: {ag['distancia_calculada']:.2f} km")
                    print(f"       Endereço Filial: {ag['endereco']}")
            else:
                print("-> ALERTA: Nenhuma filial encontrada dentro do raio permitido para esta região.")
        else:
            print("-> ERRO: Não foi possível obter as coordenadas para o endereço fornecido.")
            
        # Espera de 1 segundo para respeitar o Rate Limit da API do Nominatim de forma elegante
        time.sleep(1)
        
    print("\n" + "=" * 80)