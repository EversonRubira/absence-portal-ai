"""
Cliente de linha de comando para brincar com o backend do Portal de Ausências.

Assume que o backend já está a correr (uvicorn main:app --reload --port 8000)
noutro terminal.

Uso:
    python chat_cli.py
"""

import requests

BASE_URL = "http://localhost:8000"

# Dados fictícios de exemplo — edita à vontade para testares outros cenários.
AUSENCIAS_EXEMPLO = [
    {"colaborador": "Everson", "tipo": "Férias", "inicio": "2026-08-04", "fim": "2026-08-08"},
    {"colaborador": "Arthur", "tipo": "Férias", "inicio": "2026-08-04", "fim": "2026-08-08"},
    {"colaborador": "Ana Silva", "tipo": "Férias", "inicio": "2026-09-01", "fim": "2026-09-10"},
]

ALERTAS_EXEMPLO = [
    {"colaborador": "Everson", "dias_restantes": 3, "prazo": "2026-12-31"},
    {"colaborador": "Arthur", "dias_restantes": 3, "prazo": "2026-12-31"},
]


def testar_saude():
    r = requests.get(f"{BASE_URL}/health")
    print(f"[health] {r.status_code} — {r.json()}\n")


def gerar_resumo():
    payload = {
        "ano": 2026,
        "total_colaboradores": 12,
        "dias_gozados_total": 84,
        "alertas_saldo_critico": ALERTAS_EXEMPLO,
        "sobreposicoes": [],
    }
    r = requests.post(f"{BASE_URL}/api/summary", json=payload)
    if r.ok:
        print("\n--- Resumo ---")
        print(r.json()["resumo"])
        print("--------------\n")
    else:
        print(f"[erro {r.status_code}] {r.text}\n")


def perguntar():
    pergunta = input("A tua pergunta sobre as ausências: ").strip()
    if not pergunta:
        print("Pergunta vazia, a ignorar.\n")
        return
    payload = {"pergunta": pergunta, "ausencias": AUSENCIAS_EXEMPLO}
    r = requests.post(f"{BASE_URL}/api/query", json=payload)
    if r.ok:
        print(f"\n> {r.json()['resposta']}\n")
    else:
        print(f"[erro {r.status_code}] {r.text}\n")


def menu():
    print("""
Portal de Ausências — cliente de teste
1) Testar /health
2) Gerar resumo executivo (dados de exemplo)
3) Fazer uma pergunta em linguagem natural
4) Ver/editar dados de exemplo (ausências)
0) Sair
""")


def ver_dados():
    print("\nAusências de exemplo atuais:")
    for a in AUSENCIAS_EXEMPLO:
        print(f"  - {a['colaborador']}: {a['tipo']} de {a['inicio']} a {a['fim']}")
    print("\nPara mudar estes dados, edita a lista AUSENCIAS_EXEMPLO no topo deste ficheiro.\n")


if __name__ == "__main__":
    while True:
        menu()
        escolha = input("Escolhe uma opção: ").strip()
        if escolha == "1":
            testar_saude()
        elif escolha == "2":
            gerar_resumo()
        elif escolha == "3":
            perguntar()
        elif escolha == "4":
            ver_dados()
        elif escolha == "0":
            print("Até já.")
            break
        else:
            print("Opção inválida.\n")