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
  const mostrar = data.slice(0, maxRows);

  mostrar.forEach(m => {
    const tr = document.createElement("tr");
    tr.dataset.id = m.id;
    tr.classList.add("fila-movimiento");
    tr.style.cursor = "pointer";

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

    tr.addEventListener("click", () => {
      fetch(`/api/movimiento/${m.id}`)
        .then(res => res.json())
        .then(data => {
          const body = document.getElementById("modalMovimientoBody");
          const modalContent = document.querySelector("#modalMovimiento .modal-content");

          // Estilo visual del modal según tipo
          modalContent.classList.remove("modal-content-ingreso", "modal-content-egreso");
          if (data.tipo === "INGRESO") {
            modalContent.classList.add("modal-content-ingreso");
          } else if (data.tipo === "EGRESO") {
            modalContent.classList.add("modal-content-egreso");
          }

          const concepto = data.concepto;

          // Detección de enlaces
          let botonDetalleExtra = "";
          const matchVenta = concepto.match(/^V#(\d+)/i);
          const matchCompra = concepto.match(/Egreso por compra\s*#(\d+)/i);

          if (matchVenta) {
            const ventaId = matchVenta[1];
            botonDetalleExtra = `
              <div class="mt-4 text-end">
                <a href="/ventas/${ventaId}" class="btn btn-primary btn-sm">
                  Ver detalle de la venta
                </a>
              </div>
            `;
          } else if (matchCompra) {
            const compraId = matchCompra[1];
            botonDetalleExtra = `
              <div class="mt-4 text-end">
                <a href="/compras/detalle/${compraId}" class="btn btn-warning btn-sm">
                  Ver detalle de la compra
                </a>
              </div>
            `;
          }

          body.innerHTML = `
            <p><strong>Fecha:</strong> ${formatearFecha(data.fecha)}</p>
            <p><strong>Tipo:</strong> ${data.tipo}</p>
            <p><strong>Concepto:</strong> ${concepto}</p>
            <p><strong>Importe:</strong> $${data.importe.toFixed(2)}</p>
            <p><strong>Moneda:</strong> ${data.metodo_pago.currency}</p>
            <p><strong>Método de Pago:</strong> ${data.metodo_pago.name}</p>
            ${botonDetalleExtra}
          `;

          const modal = new bootstrap.Modal(document.getElementById("modalMovimiento"));
          modal.show();
        })
        .catch(err => {
          console.error(err);
          const body = document.getElementById("modalMovimientoBody");
          body.innerHTML = `<div class="text-danger text-center">Error al cargar el movimiento.</div>`;
        });
    });

    tbody.appendChild(tr);
  });

  new Tablesort(document.getElementById("tabla-movimientos"));
}

function cargarMovimientos(params = {}) {
  const url = new URL("/api/movimientos-dinero", window.location.origin);
  Object.entries(params).forEach(([k, v]) => {
    if (v) url.searchParams.append(k, v);
  });
  fetch(url)
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

document.getElementById("btnFiltro").addEventListener("click", () => {
  const modal = new bootstrap.Modal(document.getElementById("modalFiltro"));
  modal.show();
});

function setRangoRapido(dias) {
  const hoy = new Date();
  const inicio = new Date();
  inicio.setDate(hoy.getDate() - dias);
  document.getElementById("fechaDesde").value = inicio.toISOString().slice(0, 10);
  document.getElementById("fechaHasta").value = hoy.toISOString().slice(0, 10);
}

document.getElementById("btnSemana").addEventListener("click", () => setRangoRapido(7));
document.getElementById("btnMes").addEventListener("click", () => setRangoRapido(30));

document.getElementById("filtroForm").addEventListener("submit", e => {
  e.preventDefault();
  const params = {};
  const desde = document.getElementById("fechaDesde").value;
  const hasta = document.getElementById("fechaHasta").value;
  const tipo = document.getElementById("tipoFiltro").value;
  const concepto = document.getElementById("conceptoBuscar").value;
  if (desde) params.start = desde;
  if (hasta) params.end = hasta;
  if (tipo === "VENTA") params.ventas = "1"; else if (tipo) params.tipo = tipo;
  if (concepto) params.concepto = concepto;
  cargarMovimientos(params);
  bootstrap.Modal.getInstance(document.getElementById("modalFiltro")).hide();
});

cargarMovimientos();
window.addEventListener("resize", () => cargarMovimientos());
  
