// app/static/js/product_form/producto_api.js

import { resetFormularioVisual } from './form_utils.js';

/**
 * Adjunta un listener al campo de código de producto para validar existencia
 * y configurar el formulario dinámicamente según corresponda.
 */
export function attachCodigoListener(ctx) {
  const {
    codigoInput, estadoMsg, submitButton,
    descripcionInput, catalogoSelect, precioInput, costoInput, stockInput, fotoInput,
    descripcionLabel, catalogoLabel, precioLabel, costoLabel, stockLabel,
    stockAgregadoInput,
    nuevoForm, existenteForm
  } = ctx;

  codigoInput.addEventListener("blur", async () => {
    const codigo = codigoInput.value.trim();
    if (!codigo) return;

    resetFormularioVisual(ctx); // 👈 uso de la función común

    try {
      const res = await fetch(`/productos?codigo=${encodeURIComponent(codigo)}`);
      const data = await res.json();

      if (data.exists === false) {
        // === NUEVO PRODUCTO ===
        estadoMsg.textContent = "Nuevo producto. Complete los datos.";
        submitButton.textContent = "Crear producto";
        submitButton.disabled = false;

        nuevoForm.classList.remove("d-none");

        descripcionInput.disabled = false;
        descripcionInput.required = true;

        catalogoSelect.disabled = false;
        catalogoSelect.removeAttribute("required");

        precioInput.disabled = false;
        precioInput.required = true;

        costoInput.disabled = false;
        costoInput.removeAttribute("required");


        stockInput.disabled = false;
        stockInput.required = true;

        if (fotoInput) {
          fotoInput.disabled = false;
          fotoInput.value = "";
        }

        ctx.productoExistente = false;
        ctx.productoId = null;
        ctx.productoTemporal = null;
      } else {
        // === PRODUCTO EXISTENTE ===
        const prod = data;

        estadoMsg.textContent = "Producto existente. Puede agregar stock.";
        submitButton.textContent = "Agregar stock";
        submitButton.disabled = false;

        existenteForm.classList.remove("d-none");

        descripcionLabel.textContent = prod.descripcion;
        catalogoLabel.textContent = prod.catalogo_id;
        precioLabel.textContent = `$${prod.precio_venta.toFixed(2)}`;
        costoLabel.textContent = prod.costo_produccion != null
          ? `$${parseFloat(prod.costo_produccion).toFixed(2)}`
          : "-";
        stockLabel.textContent = prod.stock_actual;

        stockAgregadoInput.disabled = false;
        stockAgregadoInput.required = true;
        stockAgregadoInput.value = 1;

        if (fotoInput) {
          fotoInput.disabled = true;
          fotoInput.value = "";
        }

        costoInput.disabled = true;
        costoInput.removeAttribute("required");

        ctx.productoExistente = true;
        ctx.productoId = prod.id;
        ctx.productoTemporal = prod;
      }
    } catch (err) {
      console.error("Error al validar código:", err);
    }
  });

  codigoInput.addEventListener("input", () => {
    codigoInput.classList.remove("is-invalid");
    estadoMsg.textContent = "";
  });
}
