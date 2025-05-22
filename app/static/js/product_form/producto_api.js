// app/static/js/producto_api.js

/**
 * Adjunta un listener al campo de código de producto para verificar si existe en la base.
 * Si existe, muestra un modal para gestionar actualización de stock;
 * si no, prepara el formulario para creación.
 * @param {Object} ctx - Contexto con referencias al DOM y estado interno.
 */
export function attachCodigoListener(ctx) {
  const {
    codigoInput,        // Input de código identificador de producto
    descripcionInput,   // Input de descripción del producto
    catalogoSelect,     // Selector de catálogo asociado
    precioInput,        // Input de precio de venta
    stockInput,         // Input de stock inicial para nuevos productos
    stockInfo,          // Contenedor con información de stock actual
    stockLabel,         // Etiqueta que muestra stock actual
    stockAgregadoInput, // Input para cantidad a agregar en edición
    submitButton,       // Botón de envío del formulario
    modal               // Instancia del modal para producto existente
  } = ctx;

  // Al perder foco del campo de código, consultamos la API
  codigoInput.addEventListener("blur", async () => {
    const codigo = codigoInput.value.trim();
    if (!codigo) return; // Si está vacío, no hacemos nada

    try {
      // Llamada a la API que verifica existencia de código
      const res = await fetch(`/productos?codigo=${encodeURIComponent(codigo)}`);
      const data = await res.json();

      if (data.exists === false) {
        // No existe: limpiar estados y campos para creación
        ctx.productoExistente = false;
        ctx.productoId = null;
        ctx.productoTemporal = null;

        codigoInput.classList.remove("is-invalid");
        descripcionInput.value = "";
        catalogoSelect.selectedIndex = 0;
        precioInput.value = "";
        stockAgregadoInput.value = 0;

        descripcionInput.removeAttribute("readonly");
        catalogoSelect.removeAttribute("disabled");
        precioInput.removeAttribute("readonly");

        stockInfo.classList.add("d-none");
        stockAgregadoInput.setAttribute("disabled", true);
        stockAgregadoInput.removeAttribute("required");

        stockInput.parentElement.classList.remove("d-none");
        stockInput.setAttribute("required", true);

        submitButton.textContent = "Crear Producto";
      } else {
        // Existe: guardar datos temporales y mostrar modal para aceptar o cancelar
        ctx.productoTemporal = data;
        modal.show();
      }
    } catch (error) {
      console.error("Error al verificar producto:", error);
    }
  });

  // Cuando se confirme en el modal que el producto existe:
  ctx.aceptarBtn.addEventListener("click", () => {
    const prod = ctx.productoTemporal;
    if (!prod) return;

    ctx.productoExistente = true;
    ctx.productoId = prod.id;

    codigoInput.classList.remove("is-invalid");
    descripcionInput.value = prod.descripcion;
    catalogoSelect.value = prod.catalogo_id;
    precioInput.value = prod.precio_venta;

    descripcionInput.setAttribute("readonly", true);
    catalogoSelect.setAttribute("disabled", true);
    precioInput.setAttribute("readonly", true);

    stockLabel.textContent = prod.stock_actual;
    stockInfo.classList.remove("d-none");
    stockAgregadoInput.removeAttribute("disabled");
    stockAgregadoInput.setAttribute("required", true);

    stockInput.parentElement.classList.add("d-none");
    stockInput.removeAttribute("required");

    submitButton.textContent = "Agregar stock";
    modal.hide();
  });

  // Si se cancela en el modal, restaurar formulario a estado creación:
  ctx.cancelarBtn.addEventListener("click", () => {
    ctx.productoExistente = false;
    ctx.productoId = null;
    ctx.productoTemporal = null;

    codigoInput.classList.add("is-invalid");

    descripcionInput.value = "";
    catalogoSelect.selectedIndex = 0;
    precioInput.value = "";
    stockAgregadoInput.value = 0;

    descripcionInput.removeAttribute("readonly");
    catalogoSelect.removeAttribute("disabled");
    precioInput.removeAttribute("readonly");

    stockInfo.classList.add("d-none");
    stockAgregadoInput.setAttribute("disabled", true);
    stockAgregadoInput.removeAttribute("required");

    stockInput.parentElement.classList.remove("d-none");
    stockInput.setAttribute("required", true);

    submitButton.textContent = "Crear Producto";
    modal.hide();
  });

  // Al escribir código, limpiar estilo de error
  codigoInput.addEventListener("input", () => {
    codigoInput.classList.remove("is-invalid");
  });
}
