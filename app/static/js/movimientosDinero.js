function formatearFecha(fechaISO) {
  const f = new Date(fechaISO);
  const dia = String(f.getDate()).padStart(2, "0");
  const mes = String(f.getMonth() + 1).padStart(2, "0");
  const año = String(f.getFullYear()).slice(-2);
  return `${dia}/${mes}/${año}`;
}

function renderTabla(data) {
  const tbody = document.getElementById("tabla-body");
  tbody.innerHTML = "";

  const isMobile = window.innerWidth < 768;
  const maxRows = isMobile ? 12 : 40;

  // Limitar la cantidad de registros a mostrar
  const mostrar = data.slice(0, maxRows);

  mostrar.forEach(m => {
    const tr = document.createElement("tr");

    const fechaSort = new Date(m.fecha).toISOString();
    const fecha = `<td class="col-fecha" data-sort="${fechaSort}">${formatearFecha(m.fecha)}</td>`;

    const concepto = m.tipo === "INGRESO"
      ? `<td class="col-concepto text-start">${m.concepto}</td>`
      : `<td class="col-concepto fst-italic ps-3">${m.concepto}</td>`;

    const moneda = `<td class="col-moneda d-none d-md-table-cell text-center">${m.metodo_pago.currency}</td>`;

    const importeSort = m.importe.toFixed(2);
    const importeMobile = `${Math.round(m.importe)}${m.metodo_pago.currency}`;
    const importeDesktop = `$ ${importeSort}`;

    const importe = m.tipo === "INGRESO"
      ? `<td class="col-importe text-success fw-bold text-end" data-sort="${importeSort}">${isMobile ? importeMobile : importeDesktop}</td>`
      : `<td class="col-importe text-danger fw-bold text-end" data-sort="${importeSort}">${isMobile ? importeMobile : importeDesktop}</td>`;

    tr.innerHTML = fecha + concepto + moneda + importe;
    tbody.appendChild(tr);
  });

  new Tablesort(document.getElementById("tabla-movimientos"));
}

function cargarMovimientos() {
  fetch("/api/movimientos-dinero")
    .then(res => {
      if (!res.ok) throw new Error("Error al cargar los movimientos");
      return res.json();
    })
    .then(renderTabla)
    .catch(err => {
      console.error(err);
      const tbody = document.getElementById("tabla-body");
      tbody.innerHTML = `<tr><td colspan="4" class="text-center text-danger">Error al cargar datos</td></tr>`;
    });
}

cargarMovimientos();

// Re-renderizar en resize
window.addEventListener("resize", cargarMovimientos);
