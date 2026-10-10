import requests
import json
from datetime import datetime

print("A iniciar filtragem avançada das listas do Dracid...")

# 1. Descarregar os dados reais do manifesto do Dracid
url_manifesto = "https://github.io"
response = requests.get(url_manifesto)
dados_dracid = response.json()

# Obter a data de hoje no formato do site (ex: "10 Oct 2026")
hoje_str = datetime.now().strftime("%d %b %Y").lstrip("0")

filmes_filtrados = []

# 2. Filtrar os filmes e séries lançados HOJE em streaming
for item in dados_dracid.get("metas", []):
    data_lancamento = item.get("released", "")
    plataforma = item.get("platform", "")
    
    # Validar se a estreia é hoje e pertence a uma plataforma digital/streaming
    if hoje_str in data_lancamento:
        plataforma_lower = plataforma.lower()
        if any(p in plataforma_lower for p in ["netflix", "apple tv+", "prime video", "disney+", "hbo max", "vod", "digital"]):
            
            # FORMATAÇÃO STREMIO: Configurar a Badge (Etiqueta no topo do poster)
            # Em vez de "IN CINEMA", injetamos a plataforma e a data
            item["behaviorHints"] = {
                "defaultVideoId": item.get("id"),
                "hasBadge": True,
                "badge": f"{plataforma} | {datetime.now().strftime('%d/%m')}"
            }
            
            filmes_filtrados.append(item)

# 3. Estruturar o Add-on final limpo com as Etiquetas ativas
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

# Gravar o ficheiro público que o Stremio vai ler
with open("addon.json", "w", encoding="utf-8") as f:
    json.dump(meu_addon, f, indent=4, ensure_ascii=False)

print(f"Sucesso! Foram encontrados {len(filmes_filtrados)} lançamentos de streaming para hoje.")
