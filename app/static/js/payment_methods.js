document.addEventListener("DOMContentLoaded", () => {
  const table = document.getElementById("payment-methods-body");

  // MODAL ELIMINAR
  const deleteModal = new bootstrap.Modal(document.getElementById("confirmDeleteModal"));
  const modalName = document.getElementById("modal-payment-name");
  const confirmDeleteBtn = document.getElementById("confirmDeleteBtn");

  // MODAL EDITAR
  const editModal = new bootstrap.Modal(document.getElementById("editModal"));
  const editInput = document.getElementById("editInput");
  const editForm = document.getElementById("editForm");

  let idAEliminar = null;
  let rowAEliminar = null;
  let idAEditar = null;
  let rowAEditar = null;

  // --- ELIMINAR ---
  table.addEventListener("click", (e) => {
    const btn = e.target.closest("button.btn-outline-danger");
    if (!btn) return;

    const row = btn.closest("tr");
    const name = row.querySelector("td").textContent;
    const id = row.getAttribute("data-id");

    modalName.textContent = name;
    idAEliminar = id;
    rowAEliminar = row;

    confirmDeleteBtn.disabled = false;
    confirmDeleteBtn.innerHTML = 'Sí, eliminar';
    deleteModal.show();
  });

  confirmDeleteBtn.addEventListener("click", async () => {
    if (!idAEliminar || !rowAEliminar) return;

    confirmDeleteBtn.disabled = true;
    confirmDeleteBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span> Eliminando...`;

    try {
      const res = await fetch(`/payment_methods/id/${idAEliminar}`, {
        method: "DELETE"
      });

      if (!res.ok) throw new Error("Error al eliminar");

      rowAEliminar.remove();
    } catch (err) {
      alert("Hubo un problema al eliminar: " + err.message);
    } finally {
      deleteModal.hide();
      confirmDeleteBtn.disabled = false;
      confirmDeleteBtn.innerHTML = 'Sí, eliminar';
      idAEliminar = null;
      rowAEliminar = null;
    }
  });

  // --- EDITAR ---
  table.addEventListener("click", (e) => {
    const btn = e.target.closest("button.btn-outline-primary");
    if (!btn) return;

    const row = btn.closest("tr");
    const id = row.getAttribute("data-id");
    const currentName = row.querySelector("td").textContent;

    editInput.value = currentName;
    idAEditar = id;
    rowAEditar = row;

    editModal.show();
  });

  editForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const newName = editInput.value.trim();
    if (!newName || !idAEditar || !rowAEditar) {
      alert("Error al editar: datos incompletos.");
      return;
    }

    const submitBtn = editForm.querySelector("button[type='submit']");
    submitBtn.disabled = true;
    submitBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span> Guardando...`;

    try {
      const res = await fetch(`/payment_methods/id/${idAEditar}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: newName })
      });

      if (!res.ok) throw new Error("Error al actualizar");

      rowAEditar.querySelector("td").textContent = newName;
      editModal.hide();
    } catch (err) {
      alert("Error al editar: " + err.message);
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerHTML = "Guardar cambios";
      idAEditar = null;
      rowAEditar = null;
    }
  });
});
