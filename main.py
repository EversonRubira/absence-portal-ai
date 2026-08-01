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
from groq import Groq
import os

app = FastAPI(title="Portal Ausências - IA Layer")

# CORS aberto para desenvolvimento local. Antes de expor publicamente,
# trocar allow_origins=["*"] pelo domínio real do frontend (Render/GitHub Pages).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

client = Groq(api_key=os.environ["GROQ_API_KEY"])
MODEL = "llama-3.3-70b-versatile"


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
    prompt = f"""Escreve um resumo executivo em português de Portugal, para um
gestor de equipa, sobre a situação de ausências da sua equipa em {req.ano}.

Dados (usa APENAS o que está aqui, não inventes nomes nem números):
- Total de colaboradores: {req.total_colaboradores}
- Dias de ausência gozados no ano: {req.dias_gozados_total}
- Alertas de saldo crítico: {req.alertas_saldo_critico}
- Sobreposições de período: {req.sobreposicoes}

Regras:
- Máximo 3 parágrafos curtos.
- Tom direto, sem floreios.
- Se uma lista vier vazia, não a menciones como problema.
- Não sugerimas ações fora do que os dados permitem concluir.
- O último parágrafo deve ser uma recomendação concreta e acionável, baseada
  apenas nos alertas e sobreposições recebidos (ex.: "agendar substituição
  para X antes de Y", "confirmar cobertura na semana de Z"). Não escrevas
  conclusões genéricas do tipo "a gestão está a ser monitorizada" — se não
  houver nenhum alerta ou sobreposição, diz apenas que não há ação necessária
  neste momento.
"""
    resposta = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=500,
    )
    return SummaryResponse(resumo=resposta.choices[0].message.content)


class QueryRequest(BaseModel):
    pergunta: str
    ausencias: list[dict]  # [{"colaborador": str, "tipo": str, "inicio": str, "fim": str}]


class QueryResponse(BaseModel):
    resposta: str


@app.post("/api/query", response_model=QueryResponse)
def consultar(req: QueryRequest):
    if not req.ausencias:
        raise HTTPException(400, "Lista de ausências vazia.")

    prompt = f"""Tens acesso aos seguintes registos de ausências de uma equipa:

{req.ausencias}

Pergunta do gestor: "{req.pergunta}"

Responde em português de Portugal, de forma direta, usando APENAS os dados acima.

Podes fazer dois tipos de coisa:
1. Responder factos diretos sobre os registos (quem está ausente quando, quantos dias, etc.).
2. Se o gestor pedir sugestões, insights ou opinião, podes raciocinar sobre PADRÕES visíveis nos próprios dados (ex.: sobreposição de datas entre colaboradores, concentração de ausências num período, datas próximas de feriados) e propor ações razoáveis (ex.: "considera espaçar estas duas ausências" ou "vale a pena confirmar cobertura nesse período").

O que NUNCA deves fazer, em nenhum dos dois casos: inventar informação que não está nos dados — como estado de aprovação, motivo da ausência, políticas da empresa, orçamento, ou decisões que dependem de contexto que não te foi dado. Se o pedido depender de algo que não está nos dados, diz isso claramente e sugere ao gestor o que precisaria de fornecer para receber uma resposta útil, em vez de simplesmente recusar sem explicação.
"""
    resposta = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=400,
    )
    return QueryResponse(resposta=resposta.choices[0].message.content)


@app.get("/health")
def health():
    return {"status": "ok"}
