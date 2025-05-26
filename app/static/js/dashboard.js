const LIMITE_MOVIMIENTOS = 30;

function formatearFecha(fechaISO) {
  const f = new Date(fechaISO);
  const dia = String(f.getDate()).padStart(2, "0");
  const mes = String(f.getMonth() + 1).padStart(2, "0");
  const año = String(f.getFullYear()).slice(-2);
  return `${dia}/${mes}/${año}`;
}

function cargarMovimientos() {
  fetch(`/api/movimientos-dinero?limit=${LIMITE_MOVIMIENTOS}`)
    .then(res => {
      if (!res.ok) throw new Error("Error al cargar movimientos");
      return res.json();
    })
    .then(movimientos => renderTablaDashboard(movimientos))
    .catch(err => {
      console.error(err);
      document.getElementById("tabla-movimientos").innerHTML =
        `<tr><td colspan="3" class="text-danger text-center">Error al cargar movimientos</td></tr>`;
    });
}

function renderTablaDashboard(data) {
  const tbody = document.getElementById("tabla-movimientos");
  tbody.innerHTML = "";

  data.forEach(m => {
    const tr = document.createElement("tr");

    const fecha = `<td>${formatearFecha(m.fecha)}</td>`;

    const concepto = m.tipo === "INGRESO"
      ? `<td class="text-start">${m.concepto}</td>`
      : `<td class="fst-italic ps-3">${m.concepto}</td>`;

    const monto = Math.round(m.importe) + m.metodo_pago.currency;
    const importe = `<td class="text-end fw-bold">${monto}</td>`;

    tr.innerHTML = fecha + concepto + importe;
    tbody.appendChild(tr);
  });
}

cargarMovimientos();
