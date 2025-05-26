document.addEventListener("DOMContentLoaded", () => {
  const fechaInput = document.getElementById("fecha");
  const hoy = new Date().toISOString().split("T")[0];
  fechaInput.value = hoy;

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

    const overlay = document.getElementById("overlay"); // usa tu id existente
    overlay.style.display = "flex"; // mostrar spinner

    const payload = {
      fecha: document.getElementById("fecha").value,
      concepto: document.getElementById("concepto").value,
      importe: parseFloat(document.getElementById("importe").value),
      payment_method_id: parseInt(document.getElementById("metodo_pago").value),
      tipo: "INGRESO"
    };

    fetch("/api/movimientos-dinero", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    })
    .then(res => {
      if (!res.ok) throw new Error("Error al guardar ingreso");
      return res.json();
    })
    .then(() => {
      // Reset, cerrar modal y refrescar si hace falta
      document.getElementById("formIngreso").reset();
      fechaInput.value = hoy;

      const modal = bootstrap.Modal.getInstance(document.getElementById("modalIngreso"));
      modal.hide();

      if (typeof cargarMovimientos === "function") {
        cargarMovimientos();
      }
    })
    .catch(err => {
      alert("Error al guardar ingreso: " + err.message);
    })
    .finally(() => {
      overlay.style.display = "none"; // ocultar
    });
  });
});
