// Guarda los filtros activos desde cualquier vista /ventas...
function storeVentasFilters(paramsString = null) {
  const params = paramsString || new URLSearchParams(window.location.search).toString();
  sessionStorage.setItem("lastVentasParams", params);
}

// Vuelve al listado con los filtros anteriores si existen
function goBackToFilteredList() {
  window.history.back();
}

// Construye los parámetros del formulario actual
function buildCurrentQueryParams() {
  const params = new URLSearchParams();
  const start = document.getElementById("start")?.value;
  const end = document.getElementById("end")?.value;
  const metodo = document.getElementById("payment_method_id")?.value;
  const codigo = document.getElementById("codigo_getoutside")?.value;

  if (start) params.append("start", start);
  if (end) params.append("end", end);
  if (metodo) params.append("payment_method_id", metodo);
  if (codigo) params.append("codigo_getoutside", codigo.trim());

  return params.toString();
}

// Botones de rango rápido con todos los filtros actuales incluidos
document.addEventListener("DOMContentLoaded", () => {
  const btnLast30 = document.getElementById("btn-last30");
  const btnLast7  = document.getElementById("btn-last7");

  if (btnLast30) {
    btnLast30.addEventListener("click", () => {
      const today = new Date();
      const prior = new Date();
      prior.setDate(today.getDate() - 30);
      const start = prior.toISOString().slice(0, 10);
      const end   = today.toISOString().slice(0, 10);
      const params = buildCurrentQueryParams();
      const query = new URLSearchParams(params);
      query.set("start", start);
      query.set("end", end);
      const finalParams = query.toString();
      storeVentasFilters(finalParams);
      location.href = "/ventas/list?" + finalParams;
    });
  }

  if (btnLast7) {
    btnLast7.addEventListener("click", () => {
      const today = new Date();
      const prior = new Date();
      prior.setDate(today.getDate() - 7);
      const start = prior.toISOString().slice(0, 10);
      const end   = today.toISOString().slice(0, 10);
      const params = buildCurrentQueryParams();
      const query = new URLSearchParams(params);
      query.set("start", start);
      query.set("end", end);
      const finalParams = query.toString();
      storeVentasFilters(finalParams);
      location.href = "/ventas/list?" + finalParams;
    });
  }

  // Captura filtros al enviar manualmente el formulario
  const form = document.getElementById("filterForm");
  if (form) {
    form.addEventListener("submit", () => {
      const params = buildCurrentQueryParams();
      storeVentasFilters(params);
    });
  }
});

// Actualiza el estado visual del botón según los filtros
function updateFilterButton() {
  const btn = document.querySelector("#filterForm button[type='submit']");
  const start = document.getElementById("start").value;
  const end = document.getElementById("end").value;
  const metodo = document.getElementById("payment_method_id").value;
  const codigo = document.getElementById("codigo_getoutside").value.trim();

  const tieneFiltros = start || end || metodo || codigo;

  if (tieneFiltros) {
    btn.textContent = "Filtrar";
    btn.classList.remove("btn-primary");
    btn.classList.add("btn-info");
  } else {
    btn.textContent = "Todo";
    btn.classList.remove("btn-info");
    btn.classList.add("btn-primary");
  }
}

// Aplicar en vista filtros si existe el formulario
document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("filterForm");
  if (form) {
    updateFilterButton();
    ["start", "end", "payment_method_id", "codigo_getoutside"].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.addEventListener("input", updateFilterButton);
    });
  }
});
