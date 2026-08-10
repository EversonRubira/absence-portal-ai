"""
Backend de IA para o Portal de Gestão de Ausências.

Stateless por design: não guarda nada em disco ou BD.
O frontend envia, a cada pedido, os dados já calculados em memória
(absences, alertas, sobreposições). Isto evita misturar a discussão
de persistência com a demonstração de valor de IA.

Duas responsabilidades:
- /api/summary  -> gera resumo executivo em PT a partir dos dados do dashboard
- /api/query    -> responde perguntas em linguagem natural sobre as ausências

Ambos os endpoints instruem o modelo a usar SOMENTE os dados recebidos,
nunca inventar nomes, datas ou números que não estejam no payload.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Portal Ausências - IA Layer")

# CORS aberto para desenvolvimento local. Antes de expor publicamente,
# trocar allow_origins=["*"] pelo domínio real do frontend (Render/GitHub Pages).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Projeto experimental descontinuado: os endpoints de IA ficam bloqueados,
# sem chamar a Groq nem depender de GROQ_API_KEY estar definida.
SERVICE_DISABLED_MSG = "Serviço de IA descontinuado: este projeto foi experimental e já não está em uso."


class SummaryRequest(BaseModel):
    ano: int
    total_colaboradores: int
    dias_gozados_total: int
    alertas_saldo_critico: list[dict]   # [{"colaborador": str, "dias_restantes": int, "prazo": str}]
    sobreposicoes: list[dict]           # [{"periodo": str, "colaboradores": list[str]}]


class SummaryResponse(BaseModel):
    resumo: str


@app.post("/api/summary", response_model=SummaryResponse)
def gerar_resumo(req: SummaryRequest):
    raise HTTPException(503, SERVICE_DISABLED_MSG)


class QueryRequest(BaseModel):
    pergunta: str
    ausencias: list[dict]  # [{"colaborador": str, "tipo": str, "inicio": str, "fim": str}]


class QueryResponse(BaseModel):
    resposta: str


@app.post("/api/query", response_model=QueryResponse)
def consultar(req: QueryRequest):
    raise HTTPException(503, SERVICE_DISABLED_MSG)


@app.get("/health")
def health():
    return {"status": "ok"}
