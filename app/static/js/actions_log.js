document.addEventListener('DOMContentLoaded', () => {
  const modal = new bootstrap.Modal(document.getElementById('actionModal'));
  const body = document.getElementById('actionModalBody');
  const link = document.getElementById('detalleLink');

  document.querySelectorAll('#tabla-acciones tbody tr').forEach(tr => {
    tr.addEventListener('click', () => {
      const detail = tr.dataset.detail;
      const entityType = tr.dataset.entity_type;
      const entityId = tr.dataset.entity_id;
      body.textContent = detail;
      let url = null;
      if (entityType && entityId) {
        if (entityType === 'VENTA') url = `/ventas/${entityId}`;
        else if (entityType === 'COMPRA') url = `/compras/detalle/${entityId}`;
        else if (entityType === 'MOVIMIENTO') url = `/movimiento/${entityId}`;
      }
      if (url) {
        link.href = url;
        link.style.display = 'inline-block';
      } else {
        link.style.display = 'none';
      }
      modal.show();
    });
  });
});

