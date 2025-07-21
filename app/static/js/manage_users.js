document.addEventListener('DOMContentLoaded', () => {
  const userSelect = document.getElementById('userSelect');
  const roleSelect = document.getElementById('roleSelect');
  const modifyBtn = document.getElementById('modifyBtn');
  const deleteBtn = document.getElementById('deleteBtn');
  const overlay = document.getElementById('overlay');

  const modifyModal = new bootstrap.Modal(document.getElementById('modifyModal'));
  const deleteModal = new bootstrap.Modal(document.getElementById('deleteModal'));

  const modifyBody = document.getElementById('modifyModalBody');
  const deleteBody = document.getElementById('deleteModalBody');
  const confirmModifyBtn = document.getElementById('confirmModifyBtn');
  const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');

  const getSelectedEmail = () => {
    const opt = userSelect.options[userSelect.selectedIndex];
    return opt ? (opt.dataset.email || opt.textContent) : '';
  };

  modifyBtn.addEventListener('click', () => {
    modifyBody.textContent = `CONFIRMA QUE QUIERE MODIFICAR EL ROL PARA EL USUARIO: ${getSelectedEmail()}`;
    confirmModifyBtn.disabled = false;
    confirmModifyBtn.textContent = 'Modificar';
    modifyModal.show();
  });

  confirmModifyBtn.addEventListener('click', async () => {
    confirmModifyBtn.disabled = true;
    confirmModifyBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span> Modificando...`;
    overlay.style.display = 'flex';
    try {
      const res = await fetch('/admin/users/change', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({ user_id: userSelect.value, role: roleSelect.value })
      });
      if (res.redirected) {
        window.location.href = res.url;
      } else {
        window.location.reload();
      }
    } catch (err) {
      window.location.reload();
    }
  });

  deleteBtn.addEventListener('click', () => {
    deleteBody.textContent = `ELIMINAR EL USUARIO: ${getSelectedEmail()} DEL SISTEMA?`;
    confirmDeleteBtn.disabled = false;
    confirmDeleteBtn.textContent = 'Eliminar';
    deleteModal.show();
  });

  confirmDeleteBtn.addEventListener('click', async () => {
    confirmDeleteBtn.disabled = true;
    confirmDeleteBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span> Eliminando...`;
    overlay.style.display = 'flex';
    try {
      const res = await fetch('/admin/users/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({ user_id: userSelect.value })
      });
      if (res.redirected) {
        window.location.href = res.url;
      } else {
        window.location.reload();
      }
    } catch (err) {
      window.location.reload();
    }
  });
});
