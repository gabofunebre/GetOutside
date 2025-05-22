// app/static/js/field_manager.js

/**
 * Configura el comportamiento dinámico del formulario de productos,
 * gestionando tanto la creación de nuevos productos como la actualización de stock.
 * @param {Object} ctx - Contexto con referencias al DOM y estado interno.
 */
export function setupFormBehavior(ctx) {
  const {
    form,               // Formulario principal
    alertPlaceholder,   // Contenedor para mostrar mensajes de alerta
    overlay,            // Capa de "cargando"
    codigoInput,        // Campo de código único del producto
    descripcionInput,   // Campo de descripción del producto
    catalogoSelect,     // Selector de catálogo
    precioInput,        // Campo de precio de venta
    stockInput,         // Campo de stock inicial (solo para nuevos productos)
    stockAgregadoInput, // Campo de cantidad a agregar (edición de stock)
    stockInfo,          // Contenedor que muestra stock actual
    submitButton        // Botón de envío del formulario
  } = ctx;

  // Estado inicial seguro para evitar errores de validación
  if (stockInfo.classList.contains("d-none")) {
    stockAgregadoInput.disabled = true;
    stockAgregadoInput.required = false;
  }

  // Escucha el evento de envío del formulario
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    alertPlaceholder.innerHTML = "";
    overlay.style.display = "flex";

    try {
      let res;

      // Validación condicional para evitar errores con campos ocultos
      if (ctx.productoExistente && ctx.productoId) {
        stockAgregadoInput.disabled = false;
        stockAgregadoInput.required = true;
        stockInput.disabled = true;
        stockInput.required = false;

        // === ACTUALIZACIÓN DE STOCK EXISTENTE ===
        const payload = { stock_agregado: Number(stockAgregadoInput.value) };
        res = await fetch(`/productos/id/${ctx.productoId}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
      } else {
        stockAgregadoInput.disabled = true;
        stockAgregadoInput.required = false;
        stockInput.disabled = false;
        stockInput.required = true;

        // === CREACIÓN DE NUEVO PRODUCTO ===
        const formData = new FormData(form);
        const payload = {};
        formData.forEach((value, key) => {
          // Convertir ciertos campos a número
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

      // Manejo de respuestas con error
      if (!res.ok) {
        const err = await res.json();
        const message = typeof err.detail === "string" ? err.detail : JSON.stringify(err.detail);
        throw new Error(message);
      }

      // Procesar respuesta exitosa
      const product = await res.json();
      alertPlaceholder.innerHTML = `
        <div class="alert alert-success alert-dismissible fade show" role="alert">
          Producto <strong>${product.codigo_getoutside}</strong> ${ctx.productoExistente ? "actualizado" : "creado"} con éxito.
          <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>`;

      // Resetear la interfaz del formulario
      form.reset();
      descripcionInput.removeAttribute("readonly");
      catalogoSelect.removeAttribute("disabled");
      precioInput.removeAttribute("readonly");
      stockInfo.classList.add("d-none");
      stockAgregadoInput.setAttribute("disabled", true);
      stockAgregadoInput.removeAttribute("required");
      stockInput.parentElement.classList.remove("d-none");
      stockInput.removeAttribute("disabled");
      stockInput.setAttribute("required", true);
      codigoInput.classList.remove("is-invalid");
      submitButton.textContent = "Crear Producto";

      // Limpiar estado interno
      ctx.productoExistente = false;
      ctx.productoId = null;
      ctx.productoTemporal = null;
    } catch (error) {
      // Mostrar alerta de error
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
