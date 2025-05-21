export function attachCodigoListener(ctx) {
  const {
    codigoInput,
    descripcionInput,
    catalogoSelect,
    precioInput,
    stockInput,
    stockInfo,
    stockLabel,
    stockAgregadoInput,
    submitButton,
    modal,
    aceptarBtn,
    cancelarBtn
  } = ctx;

  codigoInput.addEventListener("blur", async () => {
    const codigo = codigoInput.value.trim();
    if (!codigo) return;

    try {
      const res = await fetch(`/productos?codigo=${encodeURIComponent(codigo)}`);
      const data = await res.json();

      if (data.exists === false) {
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
        ctx.productoTemporal = data;
        modal.show();
      }
    } catch (error) {
      console.error("Error al verificar producto:", error);
    }
  });

  aceptarBtn.addEventListener("click", () => {
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

  codigoInput.addEventListener("input", () => {
    codigoInput.classList.remove("is-invalid");
  });
}
