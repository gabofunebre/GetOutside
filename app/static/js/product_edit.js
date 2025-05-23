// static/js/product_edit.js

// Variables globales de referencia a elementos DOM y datos
let productos = [];
let catalogos = [];
let modal, form, idInput, codigoInput, descripcionInput, precioInput, stockInput, catalogoSelect, btnEliminar;

document.addEventListener("DOMContentLoaded", async () => {
  // Inicialización de referencias a elementos del formulario
  modal = new bootstrap.Modal(document.getElementById("modal-editar"));
  form = document.getElementById("form-editar");

  idInput = document.getElementById("producto-id");
  codigoInput = document.getElementById("codigo");
  descripcionInput = document.getElementById("descripcion");
  precioInput = document.getElementById("precio");
  stockInput = document.getElementById("stock");
  catalogoSelect = document.getElementById("catalogo");
  btnEliminar = document.getElementById("btn-eliminar");

  // Cargar datos iniciales: catálogos y productos
  await cargarCatalogos();
  await cargarProductos();

  // Listeners para formulario y botones
  form.addEventListener("submit", handleFormSubmit);
  btnEliminar.addEventListener("click", handleEliminar);
  codigoInput.addEventListener("blur", validarCodigoUnico);
});

/**
 * Carga todos los productos y los muestra en la tabla.
 */
async function cargarProductos() {
  try {
    const res = await fetch("/productos/");
    if (!res.ok) throw new Error("Error al obtener productos");

    productos = await res.json();

    const tabla = document.querySelector(".tabla-ordenable");
    if (!tabla) {
      console.error("No se encontró la tabla con clase 'tabla-ordenable'");
      return;
    }
    const tbody = tabla.querySelector("tbody");
    if (!tbody) {
      console.error("Error: tbody es null");
      return;
    }
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
    alert("Error cargando productos: " + error.message);
  }
}

/**
 * Carga los catálogos disponibles en el <select> del formulario.
 */
async function cargarCatalogos() {
  try {
    const res = await fetch("/catalogos/api");
    if (!res.ok) throw new Error("Error al obtener catálogos");

    catalogos = await res.json();
    catalogoSelect.innerHTML = "";

    for (const c of catalogos) {
      const option = document.createElement("option");
      option.value = c.id;
      option.textContent = c.filename;
      catalogoSelect.appendChild(option);
    }
  } catch (error) {
    console.error("Error cargando catálogos:", error.message);
    alert("Error cargando catálogos: " + error.message);
  }
}

/**
 * Abre el modal con los datos del producto seleccionado.
 */
function abrirModal(p) {
  idInput.value = p.id;
  codigoInput.value = p.codigo_getoutside;
  descripcionInput.value = p.descripcion;
  precioInput.value = p.precio_venta;
  stockInput.value = p.stock_actual;
  catalogoSelect.value = p.catalogo_id;
  codigoInput.classList.remove("is-invalid");
  modal.show();
}

/**
 * Maneja el envío del formulario para actualizar producto.
 */
async function handleFormSubmit(e) {
  e.preventDefault();
  const id = idInput.value;

  const payload = {
    codigo_getoutside: codigoInput.value,
    descripcion: descripcionInput.value,
    precio_venta: parseFloat(precioInput.value),
    stock_actual: parseInt(stockInput.value),
    catalogo_id: parseInt(catalogoSelect.value),
  };

  const res = await fetch(`/productos/id/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  if (!res.ok) {
    const error = await res.json();
    alert("Error al actualizar producto: " + error.detail);
    return;
  }

  modal.hide();
  await cargarProductos(); // Refresca tabla
}

/**
 * Intenta eliminar el producto si no tiene ventas.
 */
async function handleEliminar() {
  const id = idInput.value;
  if (!confirm("¿Eliminar este producto? Esta acción no se puede deshacer.")) return;

  const res = await fetch(`/productos/id/${id}`, { method: "DELETE" });
  if (!res.ok) {
    const error = await res.json();
    alert("No se pudo eliminar: " + error.detail);
    return;
  }

  modal.hide();
  await cargarProductos();
}

/**
 * Valida que el código ingresado no esté repetido en otro producto.
 */
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
