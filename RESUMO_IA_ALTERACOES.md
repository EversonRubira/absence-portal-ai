# Feature: "Gerar resumo com IA" — Dashboard

Ficheiro alterado: `portal_ferias.html`
Ficheiro **não** alterado: `copia_Vitor/1785409553136_portal_ferias_6_2_27.html`

## 1. Botão novo (view Dashboard)

Local: início do bloco `<div class="view active" id="view-dashboard">` (~linha 843).

```html
<div style="display:flex;justify-content:flex-end;margin-bottom:14px;">
  <button class="btn btn-secondary btn-sm" onclick="gerarResumoIA()" title="Gerar resumo do dashboard com IA">
    <svg width="12" height="12" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path d="M12 2l1.9 5.8L20 9.5l-6.1 1.7L12 17l-1.9-5.8L4 9.5l6.1-1.7z"/></svg>
    Gerar resumo com IA
  </button>
</div>
```

Usa as classes `btn`, `btn-secondary`, `btn-sm` já existentes no ficheiro — sem CSS novo.

## 2. Modal novo

Local: a seguir ao modal `modal-editar-ano` (~linha 1953), antes do modal `modal-gerar-ics`.

```html
<div class="modal-backdrop" id="modal-ai-resumo">
  <div class="modal" style="width:560px;max-width:97vw;">
    <div class="modal-header">
      <h3>Resumo com IA</h3>
      <button class="modal-close" onclick="closeModal('ai-resumo')">&times;</button>
    </div>
    <div class="modal-body" id="ai-resumo-body" style="padding:18px 22px;font-size:13px;color:var(--acc-gray-800);line-height:1.6;">
    </div>
    <div class="modal-footer">
      <button class="btn btn-secondary" onclick="closeModal('ai-resumo')">Fechar</button>
    </div>
  </div>
</div>
```

Segue exatamente a mesma estrutura/CSS dos outros modais (`modal-backdrop`, `modal-header`, `modal-body`, `modal-footer`) e reutiliza as funções genéricas já existentes `openModal(id)` / `closeModal(id)`.

## 3. JavaScript novo

Local: logo a seguir à função `checkAlertsForDashboard()` (~linha 4799), antes de `// ─── PDF EXPORT ───`.

### `collectAISummaryData()`

Recolhe os dados já calculados/renderizados no dashboard e monta o payload da API, reutilizando as mesmas regras já usadas em `checkAlertsForDashboard()` (não altera essa função):

| Campo | Origem |
|---|---|
| `ano` | `currentYear` |
| `total_colaboradores` | `users.length` |
| `dias_gozados_total` | soma de dias de todas as ausências do ano corrente (`getYearAbsences()`) |
| `alertas_saldo_critico` | colaboradores com saldo ≤ 3 dias (mesma regra `SALDO_MIN` do alerta do dashboard); cada item: `{ colaborador, dias_restantes, prazo }`, `prazo` = `"31/12/<ano>"` |
| `sobreposicoes` | dias úteis futuros com ≥50% da equipa ausente em simultâneo (mesma regra do alerta do dashboard); cada item: `{ periodo, colaboradores: [nomes] }` |

### `gerarResumoIA()`

Função chamada pelo `onclick` do botão:

1. Abre o modal (`openModal('ai-resumo')`) e mostra **"A gerar resumo..."** no corpo.
2. Constrói o payload via `collectAISummaryData()`.
3. `fetch` **POST** para `http://localhost:8000/api/summary`, `Content-Type: application/json`, corpo = payload em JSON.
4. Sucesso → mostra `data.resumo` no corpo do modal (com escape básico de `<` para evitar HTML injection).
5. Falha (erro de rede ou resposta não-OK) → captura em `try/catch` e mostra mensagem de erro simples no modal, sem quebrar a página.

## Código completo (diff)

```diff
diff --git a/portal_ferias.html b/portal_ferias.html
index 730b68d..c170a4d 100644
--- a/portal_ferias.html
+++ b/portal_ferias.html
@@ -841,6 +841,12 @@
 
     <!-- ════ VIEW: DASHBOARD ════ -->
     <div class="view active" id="view-dashboard">
+      <div style="display:flex;justify-content:flex-end;margin-bottom:14px;">
+        <button class="btn btn-secondary btn-sm" onclick="gerarResumoIA()" title="Gerar resumo do dashboard com IA">
+          <svg width="12" height="12" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path d="M12 2l1.9 5.8L20 9.5l-6.1 1.7L12 17l-1.9-5.8L4 9.5l6.1-1.7z"/></svg>
+          Gerar resumo com IA
+        </button>
+      </div>
       <div id="dash-overlap-alert" style="display:none;background:#FFEBEE;border-left:4px solid var(--acc-red);padding:10px 16px;border-radius:2px;font-size:12px;color:#B71C1C;margin-bottom:16px;"></div>
       <div id="dash-saldo-alert" style="display:none;background:#FFF3E0;border-left:4px solid var(--acc-orange);padding:10px 16px;border-radius:2px;font-size:12px;color:#BF360C;margin-bottom:16px;"></div>
       <div class="kpi-row">
@@ -1947,6 +1953,21 @@
   </div>
 </div>
 
+<!-- Modal: Resumo com IA -->
+<div class="modal-backdrop" id="modal-ai-resumo">
+  <div class="modal" style="width:560px;max-width:97vw;">
+    <div class="modal-header">
+      <h3>Resumo com IA</h3>
+      <button class="modal-close" onclick="closeModal('ai-resumo')">&times;</button>
+    </div>
+    <div class="modal-body" id="ai-resumo-body" style="padding:18px 22px;font-size:13px;color:var(--acc-gray-800);line-height:1.6;">
+    </div>
+    <div class="modal-footer">
+      <button class="btn btn-secondary" onclick="closeModal('ai-resumo')">Fechar</button>
+    </div>
+  </div>
+</div>
+
 <!-- Modal: Gerar ICS -->
 <div class="modal-backdrop" id="modal-gerar-ics">
   <div class="modal" style="width:560px;max-width:97vw;">
@@ -4775,6 +4796,78 @@ function checkAlertsForDashboard() {
   } else { overlapEl.style.display='none'; }
 }
 
+// ─── RESUMO COM IA ──────────────────────────────────────────────
+function collectAISummaryData() {
+  const ya = getYearAbsences();
+  const SALDO_MIN = 3;
+
+  let diasGozadosTotal = 0;
+  ya.forEach(a => { diasGozadosTotal += countDays(a.start, a.end); });
+
+  // Saldo crítico — mesma regra usada em checkAlertsForDashboard
+  const alertasSaldoCritico = users.filter(u => {
+    const F = ya.filter(a=>a.userId===u.id&&(a.type==='F'||a.type==='FJ')).reduce((s,a)=>s+countDays(a.start,a.end),0);
+    const total = getUserTotalDays(u, currentYear);
+    return (total - F) <= SALDO_MIN;
+  }).map(u => {
+    const F = ya.filter(a=>a.userId===u.id&&(a.type==='F'||a.type==='FJ')).reduce((s,a)=>s+countDays(a.start,a.end),0);
+    const total = getUserTotalDays(u, currentYear);
+    return { colaborador: u.name, dias_restantes: total - F, prazo: `31/12/${currentYear}` };
+  });
+
+  // Sobreposições — mesma regra usada em checkAlertsForDashboard (≥50% da equipa, dias futuros)
+  const threshold = Math.ceil(users.length * 0.5);
+  const sobreposicoes = [];
+  if (users.length >= 2) {
+    const todayStr = new Date().toISOString().slice(0, 10);
+    const lookup = {};
+    ya.forEach(a => dateRange(a.start,a.end).forEach(ds => {
+      if (ds < todayStr) return;
+      if (!lookup[ds]) lookup[ds] = new Set();
+      lookup[ds].add(a.userId);
+    }));
+    Object.entries(lookup).forEach(([ds, set]) => {
+      const dow = new Date(ds+'T12:00:00').getDay();
+      if (dow!==0 && dow!==6 && !isHolidayForAnyone(ds) && set.size>=threshold) {
+        sobreposicoes.push({
+          periodo: formatDate(ds),
+          colaboradores: [...set].map(id => getUserById(id)?.name).filter(Boolean)
+        });
+      }
+    });
+    sobreposicoes.sort((a,b) => a.periodo < b.periodo ? -1 : 1);
+  }
+
+  return {
+    ano: currentYear,
+    total_colaboradores: users.length,
+    dias_gozados_total: diasGozadosTotal,
+    alertas_saldo_critico: alertasSaldoCritico,
+    sobreposicoes: sobreposicoes
+  };
+}
+
+async function gerarResumoIA() {
+  const body = document.getElementById('ai-resumo-body');
+  body.innerHTML = `<div style="text-align:center;padding:20px 0;color:var(--acc-gray-600);">A gerar resumo...</div>`;
+  openModal('ai-resumo');
+
+  const payload = collectAISummaryData();
+
+  try {
+    const res = await fetch('http://localhost:8000/api/summary', {
+      method: 'POST',
+      headers: { 'Content-Type': 'application/json' },
+      body: JSON.stringify(payload)
+    });
+    if (!res.ok) throw new Error(`HTTP ${res.status}`);
+    const data = await res.json();
+    body.innerHTML = `<div style="white-space:pre-wrap;">${(data.resumo || '(sem resumo)').replace(/</g,'&lt;')}</div>`;
+  } catch (err) {
+    body.innerHTML = `<div style="background:#FFEBEE;border-left:4px solid var(--acc-red);padding:10px 16px;border-radius:2px;color:#B71C1C;font-size:12px;">Não foi possível gerar o resumo. Verifique se o serviço de IA está disponível e tente novamente.</div>`;
+  }
+}
+
 // ─── PDF EXPORT ──────────────────────────────────────────────
 function initPdfModal() {
   // Use shared selector with prefix 'pdf'
```

## Verificação feita

- `node --check` no script inline do HTML → sintaxe válida.
- Não foi possível testar visualmente no browser nesta sessão (extensão Claude in Chrome não estava configurada).
- Nenhuma outra função, view ou regra de CSS existente foi alterada.
