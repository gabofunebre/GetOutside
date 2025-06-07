// app/static/js/stock_overview_filter.js
// Filtro dinámico para la tabla de stock

document.addEventListener("DOMContentLoaded", () => {
  const input = document.getElementById("stock-search");
  const tbody = document.querySelector(".tabla-ordenable tbody");
  if (!input || !tbody) return;

  input.addEventListener("input", () => {
    const value = input.value.trim().toLowerCase();
    const rows = Array.from(tbody.querySelectorAll("tr"));
    rows.forEach(row => {
      const text = row.textContent.toLowerCase();
      row.style.display = text.includes(value) ? "" : "none";
    });
  });
});
