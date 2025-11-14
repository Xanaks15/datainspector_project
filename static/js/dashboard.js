// Dashboard simplificado que muestra solo lo esencial para limpieza de datos
let state = {
  datasetId: null,
  charts: {},
};

async function api(path) {
  const res = await fetch(path);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

function fmtBytes(bytes) {
  if (bytes === 0) return "0 B";
  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB", "TB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
}

function setKPI(id, value) {
  const el = document.getElementById(id);
  if (el) el.textContent = value;
}

function ensureChart(ctxId, type, data, options = {}) {
  if (state.charts[ctxId]) {
    state.charts[ctxId].destroy();
  }
  const ctx = document.getElementById(ctxId);
  if (!ctx) return;

  const chart = new Chart(ctx, {
    type,
    data,
    options: Object.assign(
      {
        responsive: true,
        aspectRatio: 2,
        plugins: { legend: { display: false } },
        layout: { padding: 4 },
      },
      options
    ),
  });

  state.charts[ctxId] = chart;
  return chart;
}

async function refreshAll() {
  if (!state.datasetId) return;

  const base = `/api/datasets/${state.datasetId}`;

  // 1) Summary
  const ov = await api(`${base}/summary/`);
  setKPI("kpi-rows", ov.rows);
  setKPI("kpi-cols", ov.columns);
  setKPI("kpi-mem", fmtBytes(ov.memory_bytes));
  setKPI("kpi-dup", ov.duplicate_rows);
  setKPI("kpi-miss", `${ov.missing_total} (${ov.missing_pct.toFixed(2)}%)`);

  // 2) Nulos
  const miss = await api(`${base}/missing/`);
  const missFiltered = miss.missing_by_column
    .filter((d) => d.missing > 0)
    .sort((a, b) => b.missing - a.missing);

  ensureChart("chart-missing", "bar", {
    labels: missFiltered.map((d) => d.column),
    datasets: [{
      label: "Nulos",
      data: missFiltered.map((d) => d.missing),
      backgroundColor: "#93c5fd"
    }]
  });

  // 3) Cardinalidad
  const nu = await api(`${base}/nunique/`);
  const card = nu.nunique
    .map(d => ({
      column: d.column,
      pctUnique: (d.unique / ov.rows) * 100
    }))
    .sort((a, b) => b.pctUnique - a.pctUnique);

  ensureChart("chart-nunique", "bar", {
    labels: card.map(d => d.column),
    datasets: [{
      label: "% únicos",
      data: card.map(d => d.pctUnique)
    }]
  }, { indexAxis: "y" });


  // 5) Outliers aquí
  const outliers = await api(`${base}/outliers/`);
  renderTable("outliers-table", outliers.outliers);

  // 6) Duplicados
  const dups = await api(`${base}/duplicates/`);
  renderTable("dups-table", dups.duplicates_sample);
}


// === 8️⃣ Render de tablas ===
function renderTable(id, rows) {
  const el = document.getElementById(id);
  el.innerHTML = "";
  if (!rows || rows.length === 0) {
    el.innerHTML =
      "<tr><td class='text-center text-slate-500 p-2'>Sin datos</td></tr>";
    return;
  }

  const cols = Object.keys(rows[0]);
  let html = "<thead><tr>";
  cols.forEach((c) => {
    html += `<th class='border bg-slate-100 p-1 text-xs'>${c}</th>`;
  });
  html += "</tr></thead><tbody>";

  rows.forEach((r) => {
    html += "<tr>";
    cols.forEach((c) => {
      html += `<td class='border p-1 text-xs truncate max-w-[150px]'>${r[c]}</td>`;
    });
    html += "</tr>";
  });
  html += "</tbody>";
  el.innerHTML = html;
}

// === 9️⃣ Upload handler ===
async function onUpload(e) {
  e.preventDefault();
  const form = document.getElementById("upload-form");
  const body = new FormData(form);
  const res = await fetch("/api/datasets/", { method: "POST", body });
  if (!res.ok) {
    alert(await res.text());
    return;
  }
  const data = await res.json();
  state.datasetId = data.id;
  await refreshAll();
}

// === 🔟 Init ===
async function init() {
  try {
    const ds = await api("/api/datasets/");
    if (ds.datasets.length) {
      state.datasetId = ds.datasets[0].id;
    }
  
  } catch (e) {
    console.warn("Sin datasets previos");
  }

  document.getElementById("upload-form")
    .addEventListener("submit", onUpload);

  await refreshAll();
}

document.addEventListener("DOMContentLoaded", init);
