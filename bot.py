import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

print("A iniciar robô cumulativo completo (Released Movies + Upcoming)...")

# 1. Tentar ler o arquivo manifest.json atual para manter o histórico que já temos
filmes_acumulados = []
if os.path.exists("manifest.json"):
    try:
        with open("manifest.json", "r", encoding="utf-8") as f:
            dados_antigos = json.load(f)
            filmes_acumulados = dados_antigos.get("metas", [])
            print(f"Histórico atual carregado: {len(filmes_acumulados)} itens.")
    except Exception as e:
        print(f"Aviso ao ler histórico existente: {e}")

# Criar o conjunto de IDs existentes para evitar duplicados
ids_existentes = {item["id"] for item in filmes_acumulados if "id" in item}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# 2. PARTE 1: Importar a base histórica do "Released Movies" do Dracid
url_released = "https://github.io"
try:
    response = requests.get(url_released, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        for card in soup.find_all(class_=["card", "movie-row", "item"]):
            texto_card = card.get_text()
            
            # Tentar extrair o ID do IMDb
            imdb_id = "tt0000000"
            for link in card.find_all('a', href=True):
                if "://imdb.com" in link['href']:
                    partes = link['href'].split("/title/")
                    if len(partes) > 1:
                        imdb_id = partes[1].split("/")[0]
                    break
            
            if imdb_id not in ids_existentes and imdb_id != "tt0000000":
                # Descobrir a plataforma
                plataforma = "Streaming"
                texto_lower = texto_card.lower()
                for p in ["netflix", "apple tv+", "prime video", "disney+", "hbo max", "vod", "digital"]:
                    if p in texto_lower:
                        plataforma = p.upper() if p != "apple tv+" else "Apple TV+"
                        break
                
                titulo = card.find(['h2', 'h3', 'strong'])
                titulo_str = titulo.get_text().strip() if titulo else "Filme Lançado"
                
                filmes_acumulados.append({
                    "id": imdb_id,
                    "type": "movie",
                    "name": titulo_str,
                    "poster": f"https://metahub.space{imdb_id}/img",
                    "behaviorHints": {
                        "defaultVideoId": imdb_id,
                        "hasBadge": True,
                        "badge": f"{plataforma}"
                    }
                })
                ids_existentes.add(imdb_id)
except Exception as e:
    print(f"Erro ao ler base histórica: {e}")

# 3. PARTE 2: Monitorizar e acrescentar os lançamentos do dia a partir das listas Upcoming
urls_upcoming = [
    "https://github.io",
    "https://github.io"
]

hoje_str = datetime.now().strftime("%d %b %Y").lstrip("0")

for url in urls_upcoming:
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            continue
            
        soup = BeautifulSoup(response.text, 'html.parser')
        for card in soup.find_all(class_=["card", "movie-row", "item"]): 
            texto_card = card.get_text()
            
            if hoje_str in texto_card:
                plataforma = "Streaming"
                texto_lower = texto_card.lower()
                for p in ["netflix", "apple tv+", "prime video", "disney+", "hbo max", "vod", "digital"]:
                    if p in texto_lower:
                        plataforma = p.upper() if p != "apple tv+" else "Apple TV+"
                        break
                
                if "cinema" in texto_lower and plataforma == "Streaming":
                    continue
                
                titulo = card.find(['h2', 'h3', 'strong'])
                titulo_str = titulo.get_text().strip() if titulo else "Conteúdo Digital"
                
                imdb_id = "tt0000000"
                for link in card.find_all('a', href=True):
                    if "://imdb.com" in link['href']:
                        partes = link['href'].split("/title/")
                        if len(partes) > 1:
                            imdb_id = partes[1].split("/")[0]
                        break
                
                if imdb_id not in ids_existentes and imdb_id != "tt0000000":
                    filmes_acumulados.append({
                        "id": imdb_id,
                        "type": "movie" if "movie" in url else "series",
                        "name": titulo_str,
                        "poster": f"https://metahub.space{imdb_id}/img",
                        "released": datetime.now().isoformat(),
                        "behaviorHints": {
                            "defaultVideoId": imdb_id,
                            "hasBadge": True,
                            "badge": f"{plataforma} | {datetime.now().strftime('%d/%m')}"
                        }
                    })
                    ids_existentes.add(imdb_id)
    except Exception as e:
        print(f"Erro ao ler listas upcoming: {e}")

# 4. Estruturar e gravar o manifesto final
meu_addon = {
    "id": "org.dracidclean.streaming",
    "version": "1.0.0",
    "name": "Dracid Streaming Limpo",
    "description": "Catálogo Cumulativo de Streaming do Dracid",
    "resources": ["catalog", "meta"],
    "types": ["movie", "series"],
    "catalogs": [
        {
            "id": "dracid_streaming_hoje",
            "type": "movie",
            "name": "Lançados no Streaming"
        }
    ],
    "metas": filmes_acumulados
}

with open("manifest.json", "w", encoding="utf-8") as f:
    json.dump(meu_addon, f, indent=4, ensure_ascii=False)

print(f"Sucesso! Catálogo atualizado. Total de títulos guardados: {len(filmes_acumulados)}")
