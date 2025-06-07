// app/static/js/stock_overview_filter.js
// Filtro dinámico para la tabla de stock

document.addEventListener("DOMContentLoaded", () => {
  const input = document.getElementById("stock-search");
  if (!input) return;

  const rows = Array.from(document.querySelectorAll(".tabla-ordenable tbody tr"));

  input.addEventListener("input", () => {
    const value = input.value.trim().toLowerCase();
    rows.forEach(row => {
      const text = row.textContent.toLowerCase();
      row.style.display = text.includes(value) ? "" : "none";
    });
  });
});
