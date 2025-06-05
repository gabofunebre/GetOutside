document.addEventListener("DOMContentLoaded", () => {
  const fechaInput = document.getElementById("fecha");
  const btnModificarFecha = document.getElementById("btnModificarFecha");

  let localISO = "";

  // Obtener fecha desde el servidor
  fetch("/api/server-datetime")
    .then(res => res.json())
    .then(data => {
      const serverDate = new Date(data.datetime);
      localISO = new Date(serverDate.getTime() - serverDate.getTimezoneOffset() * 60000)
        .toISOString()
        .slice(0, 19);
      fechaInput.value = localISO;
    })
    .catch(err => {
      console.error("Error al obtener fecha del servidor:", err);
    });

  fechaInput.readOnly = true;

  btnModificarFecha.addEventListener("click", () => {
    fechaInput.readOnly = false;
    fechaInput.focus();
    btnModificarFecha.style.display = "none";
  });

  let tipoMovimiento = "INGRESO";
  let saldoDisponible = 0;

  document.querySelectorAll(".btn-movimiento").forEach(btn => {
    btn.addEventListener("click", () => {
      tipoMovimiento = btn.dataset.tipo || "INGRESO";

      const titulo = tipoMovimiento === "EGRESO" ? "Registrar Egreso" : "Registrar Ingreso";
      document.getElementById("modalIngresoLabel").textContent = titulo;

      const modal = document.querySelector("#modalIngreso .modal-content");
      modal.classList.remove("modal-content-ingreso", "modal-content-egreso");
      modal.classList.add(tipoMovimiento === "EGRESO" ? "modal-content-egreso" : "modal-content-ingreso");

      const botonGuardar = document.querySelector("#formIngreso .btn-guardar");
      botonGuardar.textContent = tipoMovimiento === "EGRESO" ? "Registrar Egreso" : "Registrar Ingreso";
      botonGuardar.classList.remove("btn-success", "btn-egreso");
      botonGuardar.classList.add(tipoMovimiento === "EGRESO" ? "btn-egreso" : "btn-success");

      fechaInput.value = localISO;
      fechaInput.readOnly = true;
      btnModificarFecha.style.display = "inline-block";
    });
  });

  fetch("/payment_methods/")
    .then(res => res.json())
    .then(data => {
      const select = document.getElementById("metodo_pago");
      const saldoLabel = document.getElementById("saldoDisponible");
      data.forEach(pm => {
        const opt = document.createElement("option");
        opt.value = pm.id;
        opt.textContent = `${pm.name} (${pm.currency})`;
        select.appendChild(opt);
      });

      select.addEventListener("change", () => {
        const id = select.value;
        saldoLabel.textContent = "";
        document.getElementById("errorSaldo").textContent = "";
        if (!id) return;
        fetch(`/payment_methods/id/${id}/balance`)
          .then(r => r.json())
          .then(bal => {
            saldoDisponible = bal.amount;
            saldoLabel.textContent = `Disponible: ${bal.amount.toFixed(2)} ${bal.currency}`;
          });
      });

      select.dispatchEvent(new Event("change"));
    });

  document.getElementById("formIngreso").addEventListener("submit", e => {
    if (
      tipoMovimiento === "EGRESO" &&
      parseFloat(document.getElementById("importe").value) > saldoDisponible
    ) {
      e.preventDefault();
      document.getElementById("errorSaldo").textContent = "No hay dinero suficiente";
      return;
    }

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
        fechaInput.value = localISO;
        fechaInput.readOnly = true;
        btnModificarFecha.style.display = "inline-block";

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
