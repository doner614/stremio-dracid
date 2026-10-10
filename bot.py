import requests
import json
from datetime import datetime

# Links dos catálogos originais do Dracid
url_movies = "https://github.io"
url_series = "https://github.io"

print("Robô iniciado. A ler dados do Dracid...")

# Estrutura inicial do nosso Add-on personalizado para o Stremio
meu_addon = {
    "id": "org.dracidclean.streaming",
    "version": "1.0.0",
    "name": "Dracid Streaming Limpo",
    "description": "Lançamentos de Streaming do Dia, sem Cinema",
    "resources": ["catalog", "meta"],
    "types": ["movie", "series"],
    "catalogs": [
        {
            "id": "dracid_streaming_hoje",
            "type": "movie",
            "name": "Lançados Hoje no Streaming"
        }
    ],
    "metas": []
}

# Guardar o arquivo de configuração que o Stremio vai ler
with open("addon.json", "w", encoding="utf-8") as f:
    json.dump(meu_addon, f, indent=4, ensure_ascii=False)

print("Ficheiro addon.json configurado com sucesso!")
