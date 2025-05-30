// app/static/js/payment_methods.js
document.addEventListener("DOMContentLoaded", () => {
  const table = document.getElementById("payment-methods-body");

  const deleteModalEl = document.getElementById("confirmDeleteModal");
  const deleteModal = new bootstrap.Modal(deleteModalEl);
  const modalName = document.getElementById("modal-payment-name");
  const confirmDeleteBtn = document.getElementById("confirmDeleteBtn");
  const deleteErrorMsg = document.getElementById("delete-error-msg");

  const editModal = new bootstrap.Modal(document.getElementById("editModal"));
  const editForm = document.getElementById("editForm");
  const nameInput = document.getElementById("editNameInput");
  const currencySelect = document.getElementById("editCurrencySelect");

  let idAEliminar = null;
  let rowAEliminar = null;
  let idAEditar = null;
  let rowAEditar = null;

  async function loadCurrencies() {
    try {
      const res = await fetch("/payment_methods/currencies");
      const data = await res.json();
      currencySelect.innerHTML = "";
      data.forEach(({ code, label }) => {
        const opt = document.createElement("option");
        opt.value = code;
        opt.textContent = label;
        currencySelect.appendChild(opt);
      });
    } catch (err) {
      console.error("Error cargando monedas:", err);
    }
  }

  loadCurrencies();

  table.addEventListener("click", (e) => {
    const btn = e.target.closest("button.btn-outline-danger");
    if (!btn) return;

    const row = btn.closest("tr");
    const name = row.querySelector("td").textContent;
    const id = row.getAttribute("data-id");

    modalName.textContent = name;
    idAEliminar = id;
    rowAEliminar = row;

    deleteErrorMsg.classList.add("d-none");
    deleteErrorMsg.textContent = "";

    confirmDeleteBtn.disabled = false;
    confirmDeleteBtn.innerHTML = 'Sí, eliminar';
    deleteModal.show();
  });

  confirmDeleteBtn.addEventListener("click", async () => {
    if (!idAEliminar || !rowAEliminar) return;

    confirmDeleteBtn.disabled = true;
    confirmDeleteBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span> Eliminando...`;

    deleteErrorMsg.classList.add("d-none");
    deleteErrorMsg.textContent = "";

    try {
      const res = await fetch(`/payment_methods/id/${idAEliminar}`, { method: "DELETE" });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Error al eliminar");
      }

      rowAEliminar.remove();
      deleteModal.hide();
    } catch (err) {
      deleteErrorMsg.textContent = err.message;
      deleteErrorMsg.classList.remove("d-none");
    } finally {
      confirmDeleteBtn.disabled = false;
      confirmDeleteBtn.innerHTML = 'Sí, eliminar';
      idAEliminar = null;
      rowAEliminar = null;
    }
  });

  table.addEventListener("click", (e) => {
    const btn = e.target.closest("button.btn-outline-primary");
    if (!btn) return;

    const row = btn.closest("tr");
    idAEditar = row.getAttribute("data-id");
    rowAEditar = row;
    const cells = row.querySelectorAll("td");
    nameInput.value = cells[0].textContent;
    currencySelect.value = cells[1].textContent;

    editModal.show();
  });

  editForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!idAEditar || !rowAEditar) {
      alert("Error al editar: datos incompletos.");
      return;
    }

    const newName = nameInput.value.trim();
    const newCurrency = currencySelect.value;
    if (!newName || !newCurrency) {
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
        body: JSON.stringify({ name: newName, currency: newCurrency })
      });
      if (!res.ok) throw new Error("Error al actualizar");

      const cells = rowAEditar.querySelectorAll("td");
      cells[0].textContent = newName;
      cells[1].textContent = newCurrency;
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

  // ✅ Limpieza de error al cerrar el modal de eliminación
  deleteModalEl.addEventListener("hidden.bs.modal", () => {
    deleteErrorMsg.classList.add("d-none");
    deleteErrorMsg.textContent = "";
  });
});
