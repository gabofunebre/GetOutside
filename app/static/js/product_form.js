document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("productForm");
  const alertPlaceholder = document.getElementById("alert-placeholder");
  const overlay = document.getElementById("overlay");

  const codigoInput = document.getElementById("codigo_getoutside");
  const descripcionInput = document.getElementById("descripcion");
  const catalogoSelect = document.getElementById("catalogo_id");
  const precioInput = document.getElementById("precio_venta");
  const stockInput = document.getElementById("stock_actual");
  const stockInfo = document.getElementById("existing-stock-info");
  const stockLabel = document.getElementById("stock_actual_label");
  const stockAgregadoInput = document.getElementById("stock_agregado");
  const submitButton = document.getElementById("submit-button");

  const modal = new bootstrap.Modal(document.getElementById("productoExistenteModal"));
  const aceptarBtn = document.getElementById("aceptarProductoExistente");
  const cancelarBtn = document.getElementById("cancelarProductoExistente");

  let productoExistente = false;
  let productoId = null;
  let productoTemporal = null;

  codigoInput.addEventListener("blur", async () => {
    const codigo = codigoInput.value.trim();
    if (!codigo) return;

    try {
      const res = await fetch(`/productos?codigo=${encodeURIComponent(codigo)}`);
      if (!res.ok) throw new Error("not found");

      const prod = await res.json();
      productoTemporal = prod;
      modal.show();
    } catch (e) {
      productoExistente = false;
      productoId = null;
      productoTemporal = null;

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
    }
  });

  aceptarBtn.addEventListener("click", () => {
    if (!productoTemporal) return;
    productoExistente = true;
    productoId = productoTemporal.id;

    codigoInput.classList.remove("is-invalid");
    descripcionInput.value = productoTemporal.descripcion;
    catalogoSelect.value = productoTemporal.catalogo_id;
    precioInput.value = productoTemporal.precio_venta;

    descripcionInput.setAttribute("readonly", true);
    catalogoSelect.setAttribute("disabled", true);
    precioInput.setAttribute("readonly", true);

    stockLabel.textContent = productoTemporal.stock_actual;
    stockInfo.classList.remove("d-none");
    stockAgregadoInput.removeAttribute("disabled");
    stockAgregadoInput.setAttribute("required", true);

    stockInput.parentElement.classList.add("d-none");
    stockInput.removeAttribute("required");

    submitButton.textContent = "Agregar stock";

    modal.hide();
  });

  cancelarBtn.addEventListener("click", () => {
    productoExistente = false;
    productoId = null;
    productoTemporal = null;

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

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    alertPlaceholder.innerHTML = "";
    overlay.style.display = "flex";

    try {
      let res;
      if (productoExistente) {
        const stock_agregado = Number(stockAgregadoInput.value);
        res = await fetch(`/productos/id/${productoId}`, {
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
          Producto <strong>${product.codigo_getoutside}</strong> ${productoExistente ? "actualizado" : "creado"} con éxito.
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
      productoExistente = false;
      productoId = null;
      productoTemporal = null;
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
    codigoInput.addEventListener("input", () => {
    codigoInput.classList.remove("is-invalid");
  });
