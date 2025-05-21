import { initModalHandler } from './modal_handler.js';
import { setupFormBehavior } from './field_manager.js';
import { attachCodigoListener } from './producto_api.js';

document.addEventListener("DOMContentLoaded", () => {
  const ctx = {
    form: document.getElementById("productForm"),
    alertPlaceholder: document.getElementById("alert-placeholder"),
    overlay: document.getElementById("overlay"),

    codigoInput: document.getElementById("codigo_getoutside"),
    descripcionInput: document.getElementById("descripcion"),
    catalogoSelect: document.getElementById("catalogo_id"),
    precioInput: document.getElementById("precio_venta"),
    stockInput: document.getElementById("stock_actual"),
    stockInfo: document.getElementById("existing-stock-info"),
    stockLabel: document.getElementById("stock_actual_label"),
    stockAgregadoInput: document.getElementById("stock_agregado"),
    submitButton: document.getElementById("submit-button"),

    modal: new bootstrap.Modal(document.getElementById("productoExistenteModal")),
    aceptarBtn: document.getElementById("aceptarProductoExistente"),
    cancelarBtn: document.getElementById("cancelarProductoExistente"),

    productoExistente: false,
    productoId: null,
    productoTemporal: null
  };

  initModalHandler(ctx);
  attachCodigoListener(ctx);
  setupFormBehavior(ctx);
});
