// app/static/js/stock_overview_grid.js

// Filtrado simple y modal para el grid de productos

document.addEventListener("DOMContentLoaded", () => {
  const searchInput = document.getElementById("stock-search");
  const cards = Array.from(document.querySelectorAll(".product-card"));
  const modalEl = document.getElementById("product-modal");
  const modal = new bootstrap.Modal(modalEl);

  const fotoEl = document.getElementById("modal-foto");
  const descEl = document.getElementById("modal-descripcion");
  const precioEl = document.getElementById("modal-precio");
  const costoEl = document.getElementById("modal-costo");
  const stockEl = document.getElementById("modal-stock");
  const codigoEl = document.getElementById("modal-codigo");
  const catalogoEl = document.getElementById("modal-catalogo");

  searchInput.addEventListener("input", () => {
    const val = searchInput.value.toLowerCase();
    cards.forEach(c => {
      const text = c.dataset.codigo.toLowerCase() + " " + c.dataset.descripcion.toLowerCase();
      c.style.display = text.includes(val) ? "" : "none";
    });
  });

  cards.forEach(c => {
    c.addEventListener("click", () => {
      fotoEl.src = c.dataset.foto ? `/static/uploads/products_photos/${c.dataset.foto}` : '/static/images/no-image.png';
      descEl.textContent = c.dataset.descripcion;
      precioEl.textContent = parseFloat(c.dataset.precio).toFixed(2);
      costoEl.textContent = c.dataset.costo
        ? parseFloat(c.dataset.costo).toFixed(2)
        : "-";
      stockEl.textContent = c.dataset.stock;
      codigoEl.textContent = c.dataset.codigo;
      const catId = c.dataset.catalogoId;
      if (catId && catId !== 'None') {
        catalogoEl.innerHTML = `<a href="/catalogos/download/${catId}" target="_blank">${catId}</a>`;
      } else {
        catalogoEl.textContent = '-';
      }
      modal.show();
    });
  });
});
