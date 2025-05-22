// app/static/js/product_form/field_manager.js

import { resetFormularioVisual } from './form_utils.js';

export function setupFormBehavior(ctx) {
  const {
    form, overlay, alertPlaceholder,
    stockAgregadoInput, submitButton,
    descripcionInput, precioInput
  } = ctx;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    alertPlaceholder.innerHTML = "";
    overlay.style.display = "flex";

    // Seguridad: asegurarse que solo el campo activo sea enviado
    if (ctx.productoExistente) {
      descripcionInput.removeAttribute("required");
      precioInput.removeAttribute("required");
    } else {
      stockAgregadoInput.disabled = true;
      stockAgregadoInput.removeAttribute("required");
    }

    try {
      let res;

      if (ctx.productoExistente && ctx.productoId) {
        // === AGREGAR STOCK ===
        const payload = {
          stock_agregado: Number(stockAgregadoInput.value)
        };

        res = await fetch(`/productos/id/${ctx.productoId}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
      } else {
        // === CREAR NUEVO PRODUCTO ===
        const formData = new FormData(form);
        const payload = {};

        formData.forEach((value, key) => {
          if (["precio_venta", "stock_actual", "catalogo_id"].includes(key)) {
            payload[key] = value === "" ? null : Number(value);
          } else {
            payload[key] = value;
          }
        });

        res = await fetch("/productos/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
      }

      if (!res.ok) {
        const err = await res.json();
        const msg = typeof err.detail === "string" ? err.detail : JSON.stringify(err.detail);
        throw new Error(msg);
      }

      const product = await res.json();
      alertPlaceholder.innerHTML = `
        <div class="alert alert-success alert-dismissible fade show" role="alert">
          Producto <strong>${product.codigo_getoutside}</strong> ${ctx.productoExistente ? "actualizado" : "creado"} con éxito.
          <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>`;

      resetFormularioVisual(ctx); // 👈 función reutilizada
      ctx.productoExistente = false;
      ctx.productoId = null;
      ctx.productoTemporal = null;
    } catch (error) {
      alertPlaceholder.innerHTML = `
        <div class="alert alert-danger alert-dismissible fade show" role="alert">
          ${error.message}
          <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>`;
    } finally {
      overlay.style.display = "none";
    }
  });
}
