// app/static/js/product_form/main.js

import { setupFormBehavior } from './field_manager.js';
import { attachCodigoListener } from './producto_api.js';
import { resetFormularioVisual } from './form_utils.js'; // 👈 si querés usarlo también acá

document.addEventListener("DOMContentLoaded", () => {
  const ctx = {
    form: document.getElementById("productForm"),
    alertPlaceholder: document.getElementById("alert-placeholder"),
    overlay: document.getElementById("overlay"),
    estadoMsg: document.getElementById("estado-producto"),

    codigoInput: document.getElementById("codigo_getoutside"),

    // Nuevo producto
    nuevoForm: document.getElementById("form-nuevo-producto"),
    descripcionInput: document.getElementById("descripcion"),
    catalogoSelect: document.getElementById("catalogo_id"),
    precioInput: document.getElementById("precio_venta"),
    stockInput: document.getElementById("stock_actual"),

    // Existente
    existenteForm: document.getElementById("form-existente"),
    descripcionLabel: document.getElementById("descripcion_label"),
    catalogoLabel: document.getElementById("catalogo_label"),
    precioLabel: document.getElementById("precio_label"),
    stockLabel: document.getElementById("stock_label"),
    stockAgregadoInput: document.getElementById("stock_agregado"),

    submitButton: document.getElementById("submit-button"),

    productoExistente: false,
    productoId: null,
    productoTemporal: null
  };

  attachCodigoListener(ctx);
  setupFormBehavior(ctx);
});
