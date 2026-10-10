import requests
from bs4 import BeautifulSoup
import json

print("A extrair dados diretamente das tabelas reais do Dracid...")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# 1. LINKS REAIS (Lembra-te de apagar os espaços dentro das aspas!)
urls = {
    "movie": "https://dracid77.github.io/lists/upcoming-movies",
    "series": "https://dracid77.github.io/lists/upcoming-series"
}

filmes_filtrados = []
series_filtradas = []

for tipo, url in urls.items():
    url_limpa = url.replace(" ", "")
    try:
        response = requests.get(url_limpa, headers=headers)
        if response.status_code != 200:
            print(f"Erro ao aceder à página: {url_limpa}")
            continue
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for item in soup.find_all(['div', 'tr', 'li', 'td']):
            texto = item.get_text()
            texto_lower = texto.lower()
            
            plataformas_validas = ["netflix", "apple tv+", "prime video", "disney+", "hbo max", "vod", "digital"]
            if any(p in texto_lower for p in plataformas_validas):
                
                if "cinema" in texto_lower and not any(p in texto_lower for p in plataformas_validas if p != "digital"):
                    continue
                
                imdb_id = "tt0000000"
                for link in item.find_all('a', href=True):
                    if "://imdb.com" in link['href']:
                        href_link = link['href']
                        if "/title/" in href_link:
                            partes_url = href_link.split("/title/")
                            if len(partes_url) > 1:
                                id_extraido = partes_url[1].split("/")[0]
                                if id_extraido.startswith("tt"):
                                    imdb_id = id_extraido
                        break
                
                nome_plataforma = "Streaming"
                for p in plataformas_validas:
                    if p in texto_lower:
                        nome_plataforma = p.upper() if p != "apple tv+" else "Apple TV+"
                        break
                
                tag_titulo = item.find(['h2', 'h3', 'strong', 'b'])
                titulo_str = tag_titulo.get_text().strip() if tag_titulo else "Conteúdo Digital"
                
                if imdb_id != "tt0000000":
                    meta_item = {
                        "id": imdb_id,
                        "type": tipo,
                        "name": titulo_str,
                        "poster": f"https://metahub.space{imdb_id}/img",
                        "behaviorHints": {
                            "defaultVideoId": imdb_id,
                            "hasBadge": True,
                            "badge": f"{nome_plataforma}"
                        }
                    }
                    if tipo == "movie":
                        filmes_filtrados.append(meta_item)
                    else:
                        series_filtradas.append(meta_item)
    except Exception as e:
        print(f"Erro ao processar a página {url_limpa}: {e}")

def limpar_duplicados(lista):
    vistos = set()
    nova_lista = []
    for x in lista:
        if x["id"] not in vistos:
            vistos.add(x["id"])
            nova_lista.append(x)
    return nova_lista

filmes_finais = limpar_duplicados(filmes_filtrados)
series_finais = limpar_duplicados(series_filtradas)

meu_addon = {
    "id": "org.dracidclean.streaming",
    "version": "1.0.0",
    "name": "Dracid Streaming Limpo",
    "description": "Catálogo de Streaming das Tabelas do Dracid",
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
    "metas": filmes_finais + series_finais
}

with open("manifest.json", "w", encoding="utf-8") as f:
    json.dump(meu_addon, f, indent=4, ensure_ascii=False)

print(f"Sucesso! Gerados {len(filmes_finais)} filmes e {len(series_finais)} séries.")
