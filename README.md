# Absence Portal AI

Camada de IA para um portal de gestão de ausências/férias. Adiciona resumos
executivos e respostas em linguagem natural sobre os dados já existentes no
portal, sem alterar o portal original nem os dados que ele gere.

## O que este projeto NÃO é

Não é uma reescrita do portal. Não guarda, edita nem apaga nenhuma ausência,
colaborador ou ficheiro. É só leitura: recebe dados que o frontend já calculou,
gera texto sobre eles, devolve texto. Nenhuma escrita acontece em lado nenhum.

## Arquitetura, em duas frases

O frontend (`portal_ferias.html`) continua 100% HTML/CSS/JavaScript, a correr
inteiramente no browser, exatamente como antes. Um backend novo e independente
(`main.py`, Python/FastAPI) fica no meio, entre o browser e o modelo de IA
(Groq), com uma única função: esconder a chave de API.

```
portal_ferias.html  --(pergunta/dados)-->  main.py (Render)  --(prompt)-->  Groq (Llama 3.3)
       (browser)                          (backend, sem estado)              (modelo)
```

### Porque é que existe um backend, já que o portal é só HTML?

Uma chave de API nunca pode estar visível dentro de um ficheiro HTML estático
— qualquer pessoa que o abra consegue ver o código-fonte (`Ctrl+U` no browser)
e, com ele, a chave. É o mesmo risco de deixar uma password escrita num
post-it colado ao ecrã. O backend existe só para isso: o browser fala com o
backend (sem segredo nenhum visível), e é o backend, escondido, que fala com a
Groq usando a chave.

### Porque é o backend "stateless" (sem guardar nada)?

Porque o frontend já calcula tudo o que precisa — totais, alertas de saldo
crítico, sobreposições de período — antes de pedir o resumo. O backend não
recalcula nada, só recebe o que já está pronto e escreve uma narrativa à
volta disso. Isto evita duas fontes de verdade a competirem: os dados vivem
só onde sempre viveram (no frontend / na planilha), a IA nunca guarda uma
cópia paralela.

## Ficheiros

| Ficheiro | O que é |
|---|---|
| `main.py` | Backend FastAPI: os dois endpoints de IA |
| `requirements.txt` | Dependências Python, com versões fixas |
| `.python-version` | Pin da versão do Python (3.11.9), evita erro de build no Render |
| `portal_ferias.html` | Cópia de trabalho do portal, com as features de IA adicionadas |
| `copia_Vitor/` | Ficheiro original, **nunca editado**, mantido como referência |
| `chat_cli.py` | Script de teste do backend via terminal, sem precisar do frontend |
| `CLAUDE.md` | Regras para o Claude Code (nunca editar `copia_Vitor/`) |

## Endpoints

### `POST /api/summary`

Recebe os dados já calculados do dashboard, devolve um resumo executivo em
português, terminando sempre numa recomendação concreta (nunca uma conclusão
genérica).

```json
{
  "ano": 2026,
  "total_colaboradores": 12,
  "dias_gozados_total": 84,
  "alertas_saldo_critico": [{"colaborador": "Ana", "dias_restantes": 3, "prazo": "2026-12-31"}],
  "sobreposicoes": []
}
```

### `POST /api/query`

Recebe uma pergunta em linguagem natural + a lista de ausências, devolve uma
resposta. Pode responder factos diretos ou sugerir com base em padrões visíveis
nos dados (ex.: sobreposição de datas) — mas nunca inventa informação que não
está presente (ex.: estado de aprovação, motivo, políticas).

```json
{
  "pergunta": "Quem está de férias na próxima semana?",
  "ausencias": [{"colaborador": "Ana", "tipo": "Férias", "inicio": "2026-08-04", "fim": "2026-08-08"}]
}
```

### `GET /health`

Verificação simples de que o serviço está no ar.

## Correr localmente

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\Activate.ps1
pip install -r requirements.txt
export GROQ_API_KEY=a_tua_chave   # Windows: $env:GROQ_API_KEY = "a_tua_chave"
uvicorn main:app --reload --port 8000
```

Depois, abre `portal_ferias.html` diretamente no browser (duplo-clique) — o
CORS já está aberto para desenvolvimento.

## Testar sem o frontend

```bash
python chat_cli.py
```

Menu interativo para testar os dois endpoints com dados de exemplo, sem
precisar de escrever `curl` à mão.

## Deploy

Já em produção no Render: `https://absence-portal-ai.onrender.com`.
Qualquer `git push` para `main` faz redeploy automático.

Variável de ambiente necessária no Render: `GROQ_API_KEY`.

Nota: no plano gratuito, o serviço "adormece" após inatividade — o primeiro
pedido depois de um período parado pode demorar até 50 segundos.

## Decisões conscientes, não pendências

- **Sem base de dados / sem localStorage (ainda):** o portal continua a
  depender da planilha Excel como fonte de dados, tal como sempre dependeu.
  Não foi alterado, porque não era o que foi pedido, e porque a solução certa
  depende de como o sistema é realmente usado no dia a dia — não é assumida
  aqui.
- **IA nunca decide nem aprova nada:** aprovação de férias, alteração de
  saldo, ou qualquer escrita de dados continuam 100% manuais, através da
  interface já existente do portal.
- **Groq (cloud) em vez de modelo local:** decisão válida para uma prova de
  conceito; se a preferência for manter os dados 100% fora de qualquer serviço
  externo, o backend pode ser adaptado para usar um modelo local (Ollama) sem
  alterar o frontend.
