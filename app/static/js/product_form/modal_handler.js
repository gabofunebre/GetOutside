// app/static/js/modal_handler.js

/**
 * Inicializa el manejo del modal que confirma productos existentes.
 * @param {Object} ctx - Contexto con referencias DOM y estado interno.
 */
export function initModalHandler(ctx) {
  const {
    modal,               // Instancia del modal Bootstrap
    aceptarBtn,          // Botón para aceptar producto existente
    cancelarBtn,         // Botón para cancelar selección
    codigoInput,         // Input de código identificador
    descripcionInput,    // Input de descripción del producto
    catalogoSelect,      // Select de catálogo asociado
    precioInput,         // Input de precio de venta
    stockInfo,           // Contenedor para mostrar stock actual
    stockAgregadoInput,  // Input para la cantidad a agregar al stock
    stockInput,          // Input de stock inicial (creación)
    submitButton         // Botón principal de envío del formulario
  } = ctx;

  // === OPCIÓN: Aceptar producto existente ===
  aceptarBtn.addEventListener("click", () => {
    if (!ctx.productoTemporal) return;  // Si no hay producto temporal, salir

    // Marcar que se editará stock del producto existente
    ctx.productoExistente = true;
    ctx.productoId = ctx.productoTemporal.id;

    // Ajustar estado de clase y campos a modo "edición"
    codigoInput.classList.remove("is-invalid");
    descripcionInput.value = ctx.productoTemporal.descripcion;
    catalogoSelect.value = ctx.productoTemporal.catalogo_id;
    precioInput.value = ctx.productoTemporal.precio_venta;

    // Bloquear cambios en campos que no deben editarse
    descripcionInput.setAttribute("readonly", true);
    catalogoSelect.setAttribute("disabled", true);
    precioInput.setAttribute("readonly", true);

    // Mostrar stock actual e habilitar agregar stock
    ctx.stockLabel.textContent = ctx.productoTemporal.stock_actual;
    stockInfo.classList.remove("d-none");
    stockAgregadoInput.removeAttribute("disabled");
    stockAgregadoInput.setAttribute("required", true);

    // Ocultar y deshabilitar stock inicial
    stockInput.parentElement.classList.add("d-none");
    stockInput.removeAttribute("required");

    // Cambiar texto del botón a "Agregar stock"
    submitButton.textContent = "Agregar stock";

    // Cerrar modal
    modal.hide();
  });

  // === OPCIÓN: Cancelar selección de producto existente ===
  cancelarBtn.addEventListener("click", () => {
    // Reiniciar estado interno
    ctx.productoExistente = false;
    ctx.productoId = null;
    ctx.productoTemporal = null;

    // Marcar código como inválido
    codigoInput.classList.add("is-invalid");

    // Limpiar todos los campos
    descripcionInput.value = "";
    catalogoSelect.selectedIndex = 0;
    precioInput.value = "";
    stockAgregadoInput.value = 0;

    // Desbloquear campos para nueva creación
    descripcionInput.removeAttribute("readonly");
    catalogoSelect.removeAttribute("disabled");
    precioInput.removeAttribute("readonly");

    // Ocultar sección de stock actual y deshabilitar agregar stock
    stockInfo.classList.add("d-none");
    stockAgregadoInput.setAttribute("disabled", true);
    stockAgregadoInput.removeAttribute("required");

    // Mostrar y habilitar input de stock inicial
    stockInput.parentElement.classList.remove("d-none");
    stockInput.setAttribute("required", true);

    // Restablecer texto del botón a creación
    submitButton.textContent = "Crear Producto";

    // Cerrar modal
    modal.hide();
  });
}
