export function initModalHandler(ctx) {
  const {
    modal,
    aceptarBtn,
    cancelarBtn,
    codigoInput,
    descripcionInput,
    catalogoSelect,
    precioInput,
    stockInfo,
    stockAgregadoInput,
    stockInput,
    submitButton
  } = ctx;

  aceptarBtn.addEventListener("click", () => {
    if (!ctx.productoTemporal) return;

    ctx.productoExistente = true;
    ctx.productoId = ctx.productoTemporal.id;

    codigoInput.classList.remove("is-invalid");
    descripcionInput.value = ctx.productoTemporal.descripcion;
    catalogoSelect.value = ctx.productoTemporal.catalogo_id;
    precioInput.value = ctx.productoTemporal.precio_venta;

    descripcionInput.setAttribute("readonly", true);
    catalogoSelect.setAttribute("disabled", true);
    precioInput.setAttribute("readonly", true);

    ctx.stockLabel.textContent = ctx.productoTemporal.stock_actual;
    stockInfo.classList.remove("d-none");
    stockAgregadoInput.removeAttribute("disabled");
    stockAgregadoInput.setAttribute("required", true);

    stockInput.parentElement.classList.add("d-none");
    stockInput.removeAttribute("required");

    submitButton.textContent = "Agregar stock";

    modal.hide();
  });

  cancelarBtn.addEventListener("click", () => {
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
}
