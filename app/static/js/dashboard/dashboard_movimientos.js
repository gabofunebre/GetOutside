document.addEventListener("DOMContentLoaded", () => {
  const fechaInput = document.getElementById("fecha");
  const hoy = new Date().toISOString().split("T")[0];
  fechaInput.value = hoy;

  let tipoMovimiento = "INGRESO"; // valor por defecto

  // Detectar qué botón abre el modal
  document.querySelectorAll(".btn-movimiento").forEach(btn => {
    btn.addEventListener("click", () => {
      tipoMovimiento = btn.dataset.tipo || "INGRESO";

      // Cambiar título del modal
      const titulo = tipoMovimiento === "EGRESO" ? "Registrar Egreso" : "Registrar Ingreso";
      document.getElementById("modalIngresoLabel").textContent = titulo;

      // Cambiar clase del borde del modal
      const modal = document.querySelector("#modalIngreso .modal-content");
      modal.classList.remove("modal-content-ingreso", "modal-content-egreso");
      modal.classList.add(tipoMovimiento === "EGRESO" ? "modal-content-egreso" : "modal-content-ingreso");

      // Cambiar botón Guardar
      const botonGuardar = document.querySelector("#formIngreso .btn-guardar");
      botonGuardar.textContent = tipoMovimiento === "EGRESO" ? "Registrar Egreso" : "Registrar Ingreso";
      botonGuardar.classList.remove("btn-success", "btn-egreso");
      botonGuardar.classList.add(tipoMovimiento === "EGRESO" ? "btn-egreso" : "btn-success");
    });
  });

  // Cargar medios de pago en el select
  fetch("/payment_methods/")
    .then(res => res.json())
    .then(data => {
      const select = document.getElementById("metodo_pago");
      data.forEach(pm => {
        const opt = document.createElement("option");
        opt.value = pm.id;
        opt.textContent = `${pm.name} (${pm.currency})`;
        select.appendChild(opt);
      });
    });

  // Manejar envío del formulario
  document.getElementById("formIngreso").addEventListener("submit", e => {
    e.preventDefault();

    const overlay = document.getElementById("overlay");
    overlay.style.display = "flex";

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
      fechaInput.value = hoy;

      const modal = bootstrap.Modal.getInstance(document.getElementById("modalIngreso"));
      modal.hide();

      if (typeof cargarMovimientos === "function") {
        cargarMovimientos();
      }
    })
    .catch(err => {
      alert("Error al guardar: " + err.message);
    })
    .finally(() => {
      overlay.style.display = "none";
    });
  });
});
