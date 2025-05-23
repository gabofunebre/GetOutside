// static/js/catalogos_edit.js

// ==========================
// VARIABLES Y MODALES
// ==========================
const tableBody = document.getElementById("catalogos-body");
const overlay = document.getElementById("overlay");

const deleteModal = new bootstrap.Modal(document.getElementById("confirmDeleteModal"));
const confirmDeleteBtn = document.getElementById("confirmDeleteBtn");
const modalNombre = document.getElementById("modal-catalogo-nombre");

const editModal = new bootstrap.Modal(document.getElementById("editModal"));
const editForm = document.getElementById("editForm");
const filenameInput = document.getElementById("editFilenameInput");

const errorModal = new bootstrap.Modal(document.getElementById("errorModal"));
const errorMsg = document.getElementById("errorModalMsg");

let idAEditar = null;
let idAEliminar = null;
let rowAEditar = null;
let rowAEliminar = null;

// ==========================
// CARGA INICIAL
// ==========================
document.addEventListener("DOMContentLoaded", () => {
  cargarCatalogos();
});

async function cargarCatalogos() {
  try {
    overlay.style.display = "flex";
    const res = await fetch("/catalogos/api");
    const catalogos = await res.json();
    tableBody.innerHTML = "";

    for (const c of catalogos) {
      const tr = document.createElement("tr");
      tr.setAttribute("data-id", c.id);
      tr.innerHTML = `
        <td>${c.filename}</td>
        <td class="text-end">
          <button class="btn btn-sm btn-outline-primary me-2" title="Editar"><i class="bi bi-pencil"></i></button>
          <button class="btn btn-sm btn-outline-danger" title="Eliminar"><i class="bi bi-x"></i></button>
        </td>
      `;
      tableBody.appendChild(tr);
    }
  } catch (err) {
    mostrarError("Error al cargar catálogos: " + err.message);
  } finally {
    overlay.style.display = "none";
  }
}

// ==========================
// EVENTOS EN TABLA
// ==========================
tableBody.addEventListener("click", (e) => {
  const row = e.target.closest("tr");
  const id = row.getAttribute("data-id");
  const filename = row.querySelector("td").textContent;

  if (e.target.closest(".btn-outline-primary")) {
    idAEditar = id;
    rowAEditar = row;
    filenameInput.value = filename;
    editModal.show();
  }

  if (e.target.closest(".btn-outline-danger")) {
    idAEliminar = id;
    rowAEliminar = row;
    modalNombre.textContent = filename;
    confirmDeleteBtn.disabled = false;
    confirmDeleteBtn.innerHTML = 'Sí, eliminar';
    deleteModal.show();
  }
});

// ==========================
// FORMULARIO EDICIÓN
// ==========================
editForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  if (!idAEditar || !rowAEditar) return;

  const nuevoNombre = filenameInput.value.trim();
  if (!nuevoNombre) return mostrarError("Nombre inválido");

  overlay.style.display = "flex";

  try {
    const res = await fetch(`/catalogos/id/${idAEditar}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ filename: nuevoNombre })
    });

    if (!res.ok) throw new Error("Error al actualizar");
    rowAEditar.querySelector("td").textContent = nuevoNombre;
    editModal.hide();
  } catch (err) {
    mostrarError("Error al editar: " + err.message);
  } finally {
    overlay.style.display = "none";
    idAEditar = null;
    rowAEditar = null;
  }
});

// ==========================
// CONFIRMACIÓN ELIMINACIÓN
// ==========================
confirmDeleteBtn.addEventListener("click", async () => {
  if (!idAEliminar || !rowAEliminar) return;

  confirmDeleteBtn.disabled = true;
  confirmDeleteBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span> Eliminando...`;

  try {
    const res = await fetch(`/catalogos/id/${idAEliminar}`, { method: "DELETE" });
    if (!res.ok) throw new Error("No se pudo eliminar (puede estar en uso)");
    rowAEliminar.remove();
    deleteModal.hide();
  } catch (err) {
    mostrarError("Error: " + err.message);
  } finally {
    confirmDeleteBtn.disabled = false;
    confirmDeleteBtn.innerHTML = 'Sí, eliminar';
    idAEliminar = null;
    rowAEliminar = null;
  }
});

// ==========================
// FUNCIONES AUXILIARES
// ==========================
function mostrarError(mensaje) {
  errorMsg.textContent = mensaje;
  errorModal.show();
}
