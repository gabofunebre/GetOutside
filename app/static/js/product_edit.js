// static/js/product_edit.js

let productos = [];
let catalogos = [];

let modal, form, idInput, codigoInput, descripcionInput, precioInput, costoInput, stockInput, catalogoSelect, btnEliminar;
let modalConfirmar, modalError, overlay, confirmarEliminarBtn;

let idPendienteEliminar = null;

document.addEventListener("DOMContentLoaded", async () => {
  // Referencias a elementos DOM
  modal = new bootstrap.Modal(document.getElementById("modal-editar"));
  modalConfirmar = new bootstrap.Modal(document.getElementById("modal-confirmar-eliminar"));
  modalError = new bootstrap.Modal(document.getElementById("modal-error"));

  overlay = document.getElementById("overlay");
  form = document.getElementById("form-editar");

  idInput = document.getElementById("producto-id");
  codigoInput = document.getElementById("codigo");
  descripcionInput = document.getElementById("descripcion");
  precioInput = document.getElementById("precio");
  costoInput = document.getElementById("costo");
  stockInput = document.getElementById("stock");
  catalogoSelect = document.getElementById("catalogo");
  btnEliminar = document.getElementById("btn-eliminar");
  confirmarEliminarBtn = document.getElementById("confirmar-eliminar");

  // Carga inicial
  await cargarCatalogos();
  await cargarProductos();

  // Eventos
  form.addEventListener("submit", handleFormSubmit);
  btnEliminar.addEventListener("click", prepararEliminar);
  confirmarEliminarBtn.addEventListener("click", confirmarEliminar);
  codigoInput.addEventListener("blur", validarCodigoUnico);
});

async function cargarProductos() {
  try {
    const res = await fetch("/productos/");
    if (!res.ok) throw new Error("Error al obtener productos");
    productos = await res.json();

    const tabla = document.querySelector(".tabla-ordenable");
    const tbody = tabla.querySelector("tbody");
    tbody.innerHTML = "";

    for (const p of productos) {
      const row = document.createElement("tr");
      row.dataset.id = p.id;
      row.innerHTML = `
        <td>${p.codigo_getoutside}</td>
        <td>${p.descripcion}</td>
        <td>$${p.precio_venta.toFixed(2)}</td>
        <td>${p.stock_actual}</td>
        <td>${(catalogos.find(c => Number(c.id) === Number(p.catalogo_id)) || {}).filename || "?"}</td>
      `;
      row.addEventListener("click", () => abrirModal(p));
      tbody.appendChild(row);
    }
    new Tablesort(document.getElementById("tabla-ordenable"));

  } catch (error) {
    console.error("Error cargando productos:", error.message);
    mostrarError("Error cargando productos: " + error.message);
  }
}

async function cargarCatalogos() {
  try {
    const res = await fetch("/catalogos/api");
    if (!res.ok) throw new Error("Error al obtener catálogos");
    catalogos = await res.json();

    catalogoSelect.innerHTML = "";
    const optEmpty = document.createElement("option");
    optEmpty.value = "";
    optEmpty.textContent = "-- Sin catálogo --";
    catalogoSelect.appendChild(optEmpty);

    for (const c of catalogos) {
      const option = document.createElement("option");
      option.value = c.id;
      option.textContent = c.filename;
      catalogoSelect.appendChild(option);
    }
  } catch (error) {
    console.error("Error cargando catálogos:", error.message);
    mostrarError("Error cargando catálogos: " + error.message);
  }
}

function abrirModal(p) {
  idInput.value = p.id;
  codigoInput.value = p.codigo_getoutside;
  descripcionInput.value = p.descripcion;
  precioInput.value = p.precio_venta;
  costoInput.value = p.costo_produccion ?? "";
  stockInput.value = p.stock_actual;
  catalogoSelect.value = p.catalogo_id ?? "";
  codigoInput.classList.remove("is-invalid");
  modal.show();
}

async function handleFormSubmit(e) {
  e.preventDefault();
  overlay.style.display = "flex";

  const id = idInput.value;
  const catalogoVal = catalogoSelect.value;
  const formData = new FormData();
  formData.append("codigo_getoutside", codigoInput.value);
  formData.append("descripcion", descripcionInput.value);
  formData.append("precio_venta", parseFloat(precioInput.value));
  formData.append("costo_produccion", parseFloat(costoInput.value));
  formData.append("stock_actual", parseInt(stockInput.value));
  formData.append(
    "catalogo_id",
    catalogoVal === "" ? "" : parseInt(catalogoVal)
  );

  const res = await fetch(`/productos/id/${id}`, {
    method: "PUT",
    body: formData,
  });

  overlay.style.display = "none";

  if (!res.ok) {
    const error = await res.json();
    mostrarError("Error al actualizar producto: " + error.detail);
    return;
  }

  modal.hide();
  await cargarProductos();
}

function prepararEliminar() {
  idPendienteEliminar = idInput.value;
  modalConfirmar.show();
}

async function confirmarEliminar() {
  if (!idPendienteEliminar) return;

  const res = await fetch(`/productos/id/${idPendienteEliminar}`, { method: "DELETE" });
  idPendienteEliminar = null;
  if (!res.ok) {
    const error = await res.json();
    modalConfirmar.hide();
    mostrarError("No se pudo eliminar: " + error.detail);
    return;
  }

  modalConfirmar.hide();
  modal.hide();
  await cargarProductos();
}

function mostrarError(mensaje) {
  const mensajeEl = document.getElementById("modal-error-mensaje");
  if (mensajeEl) mensajeEl.textContent = mensaje;
  modalError.show();
}

function validarCodigoUnico() {
  const nuevoCodigo = codigoInput.value.trim();
  const id = parseInt(idInput.value);

  const duplicado = productos.some(p => p.codigo_getoutside === nuevoCodigo && p.id !== id);
  if (duplicado) {
    codigoInput.classList.add("is-invalid");
  } else {
    codigoInput.classList.remove("is-invalid");
  }
}
  