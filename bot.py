import requests
import json

print("A clonar e a filtrar o catálogo oficial do Dracid...")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

filmes_filtrados = []

# Link do catálogo oficial que o Add-on do Dracid usa no Stremio
url_dracid = "https://github.io"

try:
    response = requests.get(url_dracid, headers=headers)
    if response.status_code == 200:
        dados_dracid = response.json()
        
        # Percorrer a lista oficial do Dracid e extrair APENAS o streaming
        for item in dados_dracid.get("metas", []):
            plataforma = item.get("platform", "")
            plataforma_lower = plataforma.lower()
            
            # Filtro rigoroso: mantém apenas plataformas digitais
            if any(p in plataforma_lower for p in ["netflix", "apple tv+", "prime video", "disney+", "hbo max", "vod", "digital"]):
                
                # Injetar a badge oficial com o nome da plataforma
                item["behaviorHints"] = {
                    "defaultVideoId": item.get("id"),
                    "hasBadge": True,
                    "badge": f"{plataforma}"
                }
                filmes_filtrados.append(item)
                
        print(f"Sucesso! Clonados e limpos {len(filmes_filtrados)} títulos de streaming.")
except Exception as e:
    print(f"Erro ao ler o Add-on do Dracid: {e}")

# Estrutura do Manifesto idêntica à do Dracid para garantir compatibilidade máxima
meu_addon = {
    "id": "org.dracidclean.streaming",
    "version": "1.0.0",
    "name": "Dracid Streaming Limpo",
    "description": "Lançamentos de Streaming do Dracid sem Cinema",
    "resources": ["catalog", "meta"],
    "types": ["movie", "series"],
    "catalogs": [
        {
            "id": "dracid_released_movies", # ID igual ao do Dracid para o Stremio aceitar
            "type": "movie",
            "name": "Lançados no Streaming"
        }
    ],
    "metas": filmes_filtrados
}

with open("manifest.json", "w", encoding="utf-8") as f:
    json.dump(meu_addon, f, indent=4, ensure_ascii=False)

print("Ficheiro manifest.json clonado e gerado com sucesso!")
