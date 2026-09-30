import requests
import json

MEU_ID_AFILIADO = "SEU_ID_AFILIADO_AQUI" # Insira seu ID de Afiliado ML

GARAGEM_MOTOS = {
    "royal_enfield_hunter_350": {
        "marca": "Royal Enfield",
        "modelo": "Hunter 350",
        "anos": ["2023", "2024", "2025", "2026"],
        "buscas_especificas": [
            {"categoria": "Manutenção", "query": "kit relacao hunter 350"},
            {"categoria": "Manutenção", "query": "filtro oleo hunter 350"},
            {"categoria": "Acessórios", "query": "sissy bar hunter 350"},
            {"categoria": "Acessórios", "query": "protetor carenagem hunter 350"},
            {"categoria": "Acessórios", "query": "suporte bau hunter 350"},
            {"categoria": "Acessórios", "query": "bolha para brisa hunter 350"}
        ]
    },
    "honda_cg_160_titan": {
        "marca": "Honda",
        "modelo": "CG 160 Titan",
        "anos": ["2016", "2018", "2020", "2022", "2024", "2025", "2026"],
        "buscas_especificas": [
            {"categoria": "Manutenção", "query": "kit transmissao cg 160 titan"},
            {"categoria": "Manutenção", "query": "pneu cg 160 titan"},
            {"categoria": "Acessórios", "query": "protetor carenagem cg 160"},
            {"categoria": "Acessórios", "query": "bagageiro cg 160"}
        ]
    }
}

BUSCAS_GERAIS = [
    {"categoria": "Equipamentos", "query": "capacete motociclista fechado escamoteavel"},
    {"categoria": "Equipamentos", "query": "jaqueta motociclista impermeavel com protecao"},
    {"categoria": "Equipamentos", "query": "luva motociclista couro"},
    {"categoria": "Acessórios Gerais", "query": "intercomunicador bluetooth capacete"}
]

CUPONS_MOTOS = [
    {"codigo": "MOTOS10", "descricao": "10% OFF em Peças e Acessórios Selecionados", "regra": "Compras acima de R$ 150"},
    {"codigo": "CAPACETE15", "descricao": "15% OFF em Capacetes e Vestuário", "regra": "Válido em itens selecionados"}
]

def buscar_produtos_ml(query_string, limite=5):
    url = f"https://api.mercadolibre.com/sites/MLB/search?q={query_string}&sort=relevance"
    res = requests.get(url)
    if res.status_code != 200:
        return []
    
    items = res.json().get('results', [])[:limite]
    lista_produtos = []
    
    for item in items:
        preco_orig = item.get('original_price')
        preco_atual = item.get('price')
        
        desconto = 0
        if preco_orig and preco_atual < preco_orig:
            desconto = round(((preco_orig - preco_atual) / preco_orig) * 100)
            
        link_orig = item.get('permalink')
        link_afiliado = f"{link_orig}?matt_tool={MEU_ID_AFILIADO}"
        
        lista_produtos.append({
            "id": item.get('id'),
            "titulo": item.get('title'),
            "preco_de": preco_orig if preco_orig else preco_atual,
            "preco_por": preco_atual,
            "desconto": desconto,
            "imagem": item.get('thumbnail').replace("-I.jpg", "-O.jpg"),
            "link": link_afiliado
        })
    return lista_produtos

def compilar_dados():
    resultado = {
        "motos": {},
        "equipamentos_gerais": [],
        "cupons": CUPONS_MOTOS
    }
    
    for chave_moto, dados in GARAGEM_MOTOS.items():
        produtos_moto = []
        for busca in dados["buscas_especificas"]:
            prods = buscar_produtos_ml(busca["query"], limite=3)
            for p in prods:
                p["categoria"] = busca["categoria"]
                produtos_moto.append(p)
                
        # ORDENAÇÃO CHAVE: Maior desconto primeiro (descendente)
        produtos_moto.sort(key=lambda x: x["desconto"], reverse=True)
                
        resultado["motos"][chave_moto] = {
            "marca": dados["marca"],
            "modelo": dados["modelo"],
            "anos": dados["anos"],
            "produtos": produtos_moto
        }
        
    for busca in BUSCAS_GERAIS:
        prods = buscar_produtos_ml(busca["query"], limite=3)
        for p in prods:
            p["categoria"] = busca["categoria"]
            resultado["equipamentos_gerais"].append(p)
            
    # Ordena equipamentos gerais por desconto também
    resultado["equipamentos_gerais"].sort(key=lambda x: x["desconto"], reverse=True)
            
    with open('ofertas_motos.json', 'w', encoding='utf-8') as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    compilar_dados()
    print("Dados atualizados e ordenados por maior desconto!")