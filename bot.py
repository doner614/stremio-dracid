import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

print("A iniciar atualização cumulativa do catálogo Stremio...")

# 1. Tentar ler o arquivo atual (se já existir) para manter o histórico
filmes_acumulados = []
if os.path.exists("manifest.json"):
    try:
        with open("manifest.json", "r", encoding="utf-8") as f:
            dados_antigos = json.load(f)
            filmes_acumulados = dados_antigos.get("metas", [])
            print(f"Histórico carregado: {len(filmes_acumulados)} itens já registados.")
    except Exception as e:
        print(f"Aviso ao ler histórico: {e}")

# Criar um conjunto de IDs já existentes para evitar duplicar filmes
ids_existentes = {item["id"] for item in filmes_acumulados if "id" in item}

# 2. Ler as novidades do Dracid para o dia de HOJE
urls = [
    "https://github.io",
    "https://github.io"
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

hoje_str = datetime.now().strftime("%d %b %Y").lstrip("0")
novos_itens = 0

for url in urls:
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            continue
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for card in soup.find_all(class_=["card", "movie-row", "item"]): 
            texto_card = card.get_text()
            
            # Verificar estritamente se o lançamento é hoje
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
                
                # Se o filme for novo e não estiver no histórico, adiciona-o!
                if imdb_id not in ids_existentes and imdb_id != "tt0000000":
                    item_stremio = {
                        "id": imdb_id,
                        "type": "movie" if "movie" in url else "series",
                        "name": titulo_str,
                        "poster": f"https://metahub.space{imdb_id}/img",
                        "released": datetime.now().isoformat(),
                        "behaviorHints": {
                            "defaultVideoId": imdb_id,
                            "hasBadge": True,
                            "badge": f"{plataforma}"
                        }
                    }
                    filmes_acumulados.append(item_stremio)
                    ids_existentes.add(imdb_id)
                    novos_itens += 1
    except Exception as e:
        print(f"Erro ao ler a página: {e}")

# 3. Estruturar e gravar o Add-on final atualizado
meu_addon = {
    "id": "org.dracidclean.streaming",
    "version": "1.0.0",
    "name": "Dracid Streaming Limpo",
    "description": "Lista Acumulativa de Lançamentos de Streaming",
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

print(f"Sucesso! Foram adicionados {novos_itens} novos lançamentos de hoje. Catálogo total: {len(filmes_acumulados)} itens.")
