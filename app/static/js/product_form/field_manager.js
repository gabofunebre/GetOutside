// app/static/js/product_form/field_manager.js

import { resetFormularioVisual } from './form_utils.js';

/**
 * Configura el comportamiento del formulario de producto,
 * diferenciando entre creación de nuevo producto o agregado de stock.
 */
export function setupFormBehavior(ctx) {
  const {
    form, overlay, alertPlaceholder,
    stockAgregadoInput, submitButton,
    descripcionInput, precioInput, costoInput,
    stockInput, catalogoSelect,

    fotoInput
  } = ctx;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    alertPlaceholder.innerHTML = "";
    overlay.style.display = "flex";

    // Seguridad: asegura que solo el campo activo sea enviado
    if (ctx.productoExistente) {
      descripcionInput.removeAttribute("required");
      precioInput.removeAttribute("required");
      costoInput.removeAttribute("required");
    } else {
      stockAgregadoInput.disabled = true;
      stockAgregadoInput.removeAttribute("required");
    }

    try {
      let res;

      if (ctx.productoExistente && ctx.productoId) {
        // === AGREGAR STOCK A PRODUCTO EXISTENTE ===
        const payload = {
          stock_agregado: Number(stockAgregadoInput.value)
        };

        res = await fetch(`/productos/id/${ctx.productoId}/stock`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
      } else {
        // === CREAR NUEVO PRODUCTO ===
        const formData = new FormData();
        formData.append("codigo_getoutside", ctx.codigoInput.value);
        formData.append("descripcion", descripcionInput.value);
        formData.append("catalogo_id", ctx.catalogoSelect.value);
        formData.append("precio_venta", parseFloat(precioInput.value));
        if (costoInput.value !== "") {
          formData.append("costo_produccion", parseFloat(costoInput.value));
        }
        formData.append("stock_actual", parseInt(stockInput.value));
        if (fotoInput && fotoInput.files.length > 0) {
          formData.append("foto", fotoInput.files[0]);
        }
        res = await fetch("/productos/", {
          method: "POST",
          body: formData
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

      resetFormularioVisual(ctx);
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
