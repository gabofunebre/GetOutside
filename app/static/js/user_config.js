document.addEventListener("DOMContentLoaded", () => {
  const deleteBtn = document.getElementById("deleteAccountBtn");
  const confirmBtn = document.getElementById("confirmDeleteAccountBtn");
  const modal = new bootstrap.Modal(document.getElementById("deleteAccountModal"));

  if (deleteBtn) {
    deleteBtn.addEventListener("click", () => {
      confirmBtn.disabled = false;
      confirmBtn.innerHTML = 'Eliminar';
      modal.show();
    });
  }

  if (confirmBtn) {
    confirmBtn.addEventListener("click", async () => {
      confirmBtn.disabled = true;
      confirmBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span> Eliminando...`;
      try {
        const res = await fetch("/config/delete", { method: "POST" });
        if (res.redirected) {
          window.location.href = res.url;
        } else {
          window.location.href = "/login";
        }
      } catch (err) {
        window.location.href = "/login";
      }
    });
  }
});
