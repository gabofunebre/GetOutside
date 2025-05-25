// Guarda los filtros activos desde /ventas/list en sessionStorage
function storeVentasFilters() {
  const params = new URLSearchParams(window.location.search);
  sessionStorage.setItem("lastVentasParams", params.toString());
}

// Vuelve al listado con los filtros anteriores si existen
function goBackToFilteredList() {
  const params = sessionStorage.getItem("lastVentasParams");
  if (params) {
    window.location.href = "/ventas/list?" + params;
  } else {
    window.location.href = "/ventas";
  }
}

// Ejecutar automáticamente en la vista de listado
if (window.location.pathname === "/ventas/list") {
  document.addEventListener("DOMContentLoaded", storeVentasFilters);
} // No ejecutar en otras vistas automáticamente