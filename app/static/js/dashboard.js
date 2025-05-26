// 📌 Cantidad máxima de movimientos a mostrar en la tabla
const LIMITE_MOVIMIENTOS = 30;

// 🧩 Valor dinámico que determina si se está registrando un ingreso o egreso
let tipoMovimiento = "INGRESO";

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
    .then(movimientos => renderTablaDashboard(movimientos))
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

  data.forEach(m => {
    const tr = document.createElement("tr");

    // Fecha en formato DD/MM/AA
    const fecha = `<td>${formatearFecha(m.fecha)}</td>`;

    // Concepto con estilo diferente según tipo
    const concepto = m.tipo === "INGRESO"
      ? `<td class="text-start">${m.concepto}</td>`
      : `<td class="fst-italic ps-3">${m.concepto}</td>`;

    // Monto como número entero + moneda (ej: 1500ARS)
    const monto = Math.round(m.importe) + m.metodo_pago.currency;
    const importe = `<td class="text-end fw-bold">${monto}</td>`;

    tr.innerHTML = fecha + concepto + importe;
    tbody.appendChild(tr);
  });
}

// 🟢 Establecer tipo de movimiento según botón clickeado (Ingreso/Egreso)
document.querySelectorAll('[data-bs-target="#modalIngreso"]').forEach(btn => {
  btn.addEventListener("click", () => {
    tipoMovimiento = btn.dataset.tipo || "INGRESO";

    // Cambiar título dinámicamente
    document.getElementById("modalIngresoLabel").textContent =
      tipoMovimiento === "EGRESO" ? "Registrar Egreso" : "Registrar Ingreso";

    // Cambiar color del botón "Guardar"
    const guardarBtn = document.querySelector("#formIngreso .btn-guardar");
    guardarBtn.classList.toggle("btn-danger", tipoMovimiento === "EGRESO");
    guardarBtn.classList.toggle("btn-success", tipoMovimiento === "INGRESO");

    // ✅ Cambiar texto del botón guardar
    guardarBtn.innerHTML = tipoMovimiento === "EGRESO"
      ? `<i class="bi bi-box-arrow-down me-1"></i> Registrar Egreso`
      : `<i class="bi bi-box-arrow-in-up me-1"></i> Registrar Ingreso`;
  });
});

// 📝 Enviar formulario +Ingreso o +Egreso
document.getElementById("formIngreso").addEventListener("submit", e => {
  e.preventDefault();
  console.log("Submit ejecutado con tipo:", tipoMovimiento); // ✅ Depuración

  const overlay = document.getElementById("overlay");
  overlay.style.display = "flex";

  const guardarBtn = document.querySelector("#formIngreso .btn-guardar");
  guardarBtn.disabled = true;

  const payload = {
    fecha: document.getElementById("fecha").value,
    concepto: document.getElementById("concepto").value,
    importe: parseFloat(document.getElementById("importe").value),
    payment_method_id: parseInt(document.getElementById("metodo_pago").value),
    tipo: tipoMovimiento
  };

  fetch("/api/movimientos-dinero", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  })
    .then(res => {
      if (!res.ok) throw new Error("Error al guardar movimiento");
      return res.json();
    })
    .then(() => {
      document.getElementById("formIngreso").reset();
      document.getElementById("fecha").value = new Date().toISOString().split("T")[0];

      bootstrap.Modal.getInstance(document.getElementById("modalIngreso")).hide();
      cargarMovimientos(); // Recarga la tabla principal
    })
    .catch(err => alert("Error al guardar: " + err.message))
    .finally(() => {
      overlay.style.display = "none";
      guardarBtn.disabled = false;
    });
});

// 🔁 Cargar la tabla inicial al abrir la página
cargarMovimientos();
