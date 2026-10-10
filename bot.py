import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

print("A iniciar extração direta (Scraping) das páginas públicas do Dracid...")

# Links das tabelas públicas do Dracid
urls = [
    "https://github.io",
    "https://github.io"
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Obter a data de hoje no formato do site (ex: "10 Oct 2026")
hoje_str = datetime.now().strftime("%d %b %Y").lstrip("0")
filmes_filtrados = []

for url in urls:
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            continue
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Procurar por todas as linhas ou cartões de filmes na página
        for card in soup.find_all(class_=["card", "movie-row", "item"]): 
            texto_card = card.get_text()
            
            # Verificar se o lançamento é hoje
            if hoje_str in texto_card:
                # Identificar a plataforma de streaming
                plataforma = "Streaming"
                texto_lower = texto_card.lower()
                
                for p in ["netflix", "apple tv+", "prime video", "disney+", "hbo max", "vod", "digital"]:
                    if p in texto_lower:
                        plataforma = p.upper() if p != "apple tv+" else "Apple TV+"
                        break
                
                # Se contiver apenas cinema, ignoramos
                if "cinema" in texto_lower and plataforma == "Streaming":
                    continue
                
                # Tentar extrair o título e o ID do IMDb se estiver presente nos links
                titulo = card.find(['h2', 'h3', 'strong'])
                titulo_str = titulo.get_text().strip() if titulo else "Conteúdo Digital"
                
                imdb_id = "tt0000000"
                for link in card.find_all('a', href=True):
                    if "://imdb.com" in link['href']:
                        imdb_id = link['href'].split("/title/")[1].split("/")[0]
                        break
                
                # Montar o objeto no formato oficial de metadados do Stremio
                item_stremio = {
                    "id": imdb_id,
                    "type": "movie" if "movie" in url else "series",
                    "name": titulo_str,
                    "poster": "https://metahub.space" + imdb_id + "/img",
                    "released": datetime.now().isoformat(),
                    "behaviorHints": {
                        "defaultVideoId": imdb_id,
                        "hasBadge": True,
                        "badge": f"{plataforma} | {datetime.now().strftime('%d/%m')}"
                    }
                }
                filmes_filtrados.append(item_stremio)
    except Exception as e:
        print(f"Erro ao ler a página {url}: {e}")

# Estrutura do Add-on final para o Stremio
meu_addon = {
    "id": "org.dracidclean.streaming",
    "version": "1.0.0",
    "name": "Dracid Streaming Limpo",
    "description": "Lançamentos de Streaming do Dia com Badges",
    "resources": ["catalog", "meta"],
    "types": ["movie", "series"],
    "catalogs": [
        {
            "id": "dracid_streaming_hoje",
            "type": "movie",
            "name": "Lançados Hoje no Streaming"
        }
    ],
    "metas": filmes_filtrados
}

# Gravar o ficheiro final público
with open("addon.json", "w", encoding="utf-8") as f:
    json.dump(meu_addon, f, indent=4, ensure_ascii=False)

print(f"Sucesso! Processo concluído. {len(filmes_filtrados)} lançamentos filtrados para o catálogo.")
