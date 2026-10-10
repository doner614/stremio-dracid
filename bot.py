import requests
import json
from datetime import datetime

print("A iniciar leitura direta do banco de dados oficial do Dracid...")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

filmes_acumulados = []

# Link do banco de dados bruto do catálogo de filmes do Dracid
url_db = "https://github.io"

try:
    response = requests.get(url_db, headers=headers)
    if response.status_code == 200:
        dados_brutos = response.json()
        
        # Percorrer os filmes já lançados e aplicar o nosso filtro de Streaming limpo
        for item in dados_brutos.get("metas", []):
            plataforma = item.get("platform", "Streaming")
            plataforma_lower = plataforma.lower()
            
            # Filtrar apenas o que é digital/streaming, eliminando o cinema puro
            if any(p in plataforma_lower for p in ["netflix", "apple tv+", "prime video", "disney+", "hbo max", "vod", "digital"]):
                
                # Configurar a etiqueta oficial no topo do poster
                item["behaviorHints"] = {
                    "defaultVideoId": item.get("id"),
                    "hasBadge": True,
                    "badge": f"{plataforma}"
                }
                filmes_acumulados.append(item)
        print(f"Sucesso! Encontrados {len(filmes_acumulados)} filmes de streaming na base de dados.")
except Exception as e:
    print(f"Erro ao ler banco de dados: {e}")

# Estrutura do Manifesto Corrigida para o seu Stremio
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
        },
        {
            "id": "dracid_streaming_hoje",
            "type": "series",
            "name": "Lançados no Streaming"
        }
    ],
    "metas": filmes_acumulados
}

with open("manifest.json", "w", encoding="utf-8") as f:
    json.dump(meu_addon, f, indent=4, ensure_ascii=False)

print("Ficheiro manifest.json atualizado de forma segura!")
