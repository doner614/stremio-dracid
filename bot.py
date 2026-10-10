import requests
import json

print("A aceder diretamente aos canais de dados oficiais e limpos do Dracid...")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# 1. LINKS REAIS (Garante que apagas todos os espaços dentro das aspas!)
urls = {
    "movie": "https://dracid77.github.io/lists/addon/catalog/movie/dracid_released_movies.json",
    "series": "https://dracid77.github.io/lists/addon/catalog/series/dracid_released_series.json"
}

filmes_filtrados = []
series_filtradas = []

def processar_banco_dados(url, lista_destino):
    url_limpa = url.replace(" ", "")
    try:
        response = requests.get(url_limpa, headers=headers)
        if response.status_code == 200:
            dados = response.json()
            for item in dados.get("metas", []):
                plataforma = item.get("platform", "Streaming")
                plataforma_lower = plataforma.lower()
                
                # Capturar o ID do IMDb correto diretamente do banco de dados (Sem Splits!)
                imdb_id = item.get("id", "")
                
                # Aplicação do filtro de streaming digital
                if imdb_id and any(p in plataforma_lower for p in ["netflix", "apple tv+", "prime video", "disney+", "hbo max", "vod", "digital"]):
                    
                    # Garantir que o item mantém o seu ID nativo estruturado
                    item["behaviorHints"] = {
                        "defaultVideoId": imdb_id,
                        "hasBadge": True,
                        "badge": f"{plataforma}"
                    }
                    lista_destino.append(item)
        print(f"Sucesso! Processados {len(lista_destino)} itens de {url_limpa}")
    except Exception as e:
        print(f"Erro ao ler canal de dados: {e}")

# Executar a leitura direta nos bancos de dados reais
processar_banco_dados(urls["movie"], filmes_filtrados)
processar_banco_dados(urls["series"], series_filtradas)

# Estrutura do Manifesto com os catálogos separados exigidos pelo Stremio
meu_addon = {
    "id": "org.dracidclean.streaming",
    "version": "1.0.0",
    "name": "Dracid Streaming Limpo",
    "description": "Catálogo de Streaming Direto da Base de Dados do Dracid",
    "resources": ["catalog", "meta"],
    "types": ["movie", "series"],
    "catalogs": [
        {
            "id": "dracid_clean_movies",
            "type": "movie",
            "name": "Lançados no Streaming"
        },
        {
            "id": "dracid_clean_series",
            "type": "series",
            "name": "Séries no Streaming"
        }
    ],
    "metas": filmes_filtrados + series_filtradas
}

with open("manifest.json", "w", encoding="utf-8") as f:
    json.dump(meu_addon, f, indent=4, ensure_ascii=False)

print(f"Concluído! Catálogo preenchido com {len(filmes_filtrados)} filmes e {len(series_filtradas)} séries.")
