export function setupFormBehavior(ctx) {
  const {
    form,
    alertPlaceholder,
    overlay,
    codigoInput,
    descripcionInput,
    catalogoSelect,
    precioInput,
    stockInput,
    stockAgregadoInput,
    stockInfo,
    submitButton
  } = ctx;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    alertPlaceholder.innerHTML = "";
    overlay.style.display = "flex";

    try {
      let res;
      if (ctx.productoExistente) {
        const stock_agregado = Number(stockAgregadoInput.value);
        res = await fetch(`/productos/id/${ctx.productoId}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ stock_agregado })
        });
      } else {
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
        throw new Error(typeof err.detail === "string" ? err.detail : JSON.stringify(err.detail));
      }

      const product = await res.json();
      alertPlaceholder.innerHTML = `
        <div class="alert alert-success alert-dismissible fade show" role="alert">
          Producto <strong>${product.codigo_getoutside}</strong> ${ctx.productoExistente ? "actualizado" : "creado"} con éxito.
          <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>`;

      form.reset();

      descripcionInput.removeAttribute("readonly");
      catalogoSelect.removeAttribute("disabled");
      precioInput.removeAttribute("readonly");

      stockInfo.classList.add("d-none");
      stockAgregadoInput.setAttribute("disabled", true);
      stockAgregadoInput.removeAttribute("required");

      stockInput.parentElement.classList.remove("d-none");
      stockInput.setAttribute("required", true);

      codigoInput.classList.remove("is-invalid");
      submitButton.textContent = "Crear Producto";

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
