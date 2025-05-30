// 📌 Cantidad máxima de movimientos a mostrar en la tabla
const LIMITE_MOVIMIENTOS = 30;

// 🗓️ Formatear fecha ISO a formato DD/MM/AA
function formatearFecha(fechaISO) {
  const f = new Date(fechaISO);
  const dia = String(f.getDate()).padStart(2, "0");
  const mes = String(f.getMonth() + 1).padStart(2, "0");
  const año = String(f.getFullYear()).slice(-2);
  return `${dia}/${mes}/${año}`;
}

// 🔄 Cargar últimos movimientos y renderizarlos en la tabla del dashboard
function cargarMovimientos() {
  fetch(`/api/movimientos-dinero?limit=${LIMITE_MOVIMIENTOS}`)
    .then(res => {
      if (!res.ok) throw new Error("Error al cargar movimientos");
      return res.json();
    })
    .then(movimientos => {
      renderTablaDashboard(movimientos);
    })
    .catch(err => {
      console.error(err);
      document.getElementById("tabla-movimientos").innerHTML =
        `<tr><td colspan="3" class="text-danger text-center">Error al cargar movimientos</td></tr>`;
    });
}

// 📋 Mostrar movimientos en la tabla del dashboard (versión compacta)
function renderTablaDashboard(data) {
  const tbody = document.getElementById("tabla-movimientos");
  tbody.innerHTML = "";

  const isMobile = window.innerWidth < 768;

  data.forEach(m => {
    const tr = document.createElement("tr");

    const fecha = `<td>${formatearFecha(m.fecha)}</td>`;

    const concepto = m.tipo === "INGRESO"
      ? `<td class="text-start">${m.concepto}</td>`
      : `<td class="fst-italic ps-3">${m.concepto}</td>`;

    const importe = m.tipo === "INGRESO"
      ? `<td class="fw-bold text-success">${Math.round(m.importe)}</td>`
      : `<td class="fw-bold text-danger">${Math.round(m.importe)}</td>`;

    if (isMobile) {
      const montoMoneda = `${Math.round(m.importe)}${m.metodo_pago.currency}`;
      const importeMobile = m.tipo === "INGRESO"
        ? `<td class="text-end fw-bold text-success">${montoMoneda}</td>`
        : `<td class="text-end fw-bold text-danger">${montoMoneda}</td>`;
      tr.innerHTML = fecha + concepto + importeMobile;
    } else {
      const moneda = m.tipo === "INGRESO"
        ? `<td class="text-center d-none d-md-table-cell text-success">${m.metodo_pago.currency}</td>`
        : `<td class="text-center d-none d-md-table-cell text-danger">${m.metodo_pago.currency}</td>`;
      tr.innerHTML = fecha + concepto + moneda + importe;
    }

    tbody.appendChild(tr);
  });
}

// 🔁 Cargar la tabla inicial al abrir la página
cargarMovimientos();