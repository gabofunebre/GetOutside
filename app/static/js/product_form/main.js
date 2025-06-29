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
    fotoInput: document.getElementById("foto"),

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

  resetFormularioVisual(ctx);


  let productosCache = [];

  async function cargarProductos() {
    try {
      const res = await fetch("/productos/");
      if (!res.ok) throw new Error("Error loading products");
      productosCache = await res.json();

    } catch (err) {
      console.error("Error cargando lista de códigos", err);
    }
  }

  function actualizarDatalist(termino) {
    const datalist = document.getElementById("codigo_datalist");
    if (!datalist) return;
    datalist.innerHTML = "";
    if (!termino) return;
    const lower = termino.toLowerCase();
    const filtrados = productosCache.filter(p =>
      p.codigo_getoutside.toLowerCase().includes(lower) ||
      (p.descripcion && p.descripcion.toLowerCase().includes(lower))
    );
    for (const p of filtrados) {
      const opt = document.createElement("option");
      opt.value = p.codigo_getoutside;
      opt.textContent = `${p.codigo_getoutside} - ${p.descripcion || ""}`.trim();
      datalist.appendChild(opt);
    }
  }

  cargarProductos().then(() => {
    ctx.codigoInput.addEventListener("input", (e) => {
      actualizarDatalist(e.target.value);
    });
  });


  attachCodigoListener(ctx);
  setupFormBehavior(ctx);
});
