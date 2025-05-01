// app/static/js/payment_method_form.js
/**
 * AJAX simple para crear medios de pago sin recargar la página,
 * mostrando alertas de Bootstrap y permitiendo volver al Dashboard.
 */
document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("pmForm");
  const alertPlaceholder = document.getElementById("alert-placeholder");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    alertPlaceholder.innerHTML = "";

    const name = form.name.value.trim();
    if (!name) {
      alertPlaceholder.innerHTML = `
        <div class="alert alert-warning alert-dismissible fade show" role="alert">
          El nombre no puede estar vacío.
          <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>`;
      return;
    }

    try {
      const res = await fetch("/payment_methods", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name })
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Error al crear el medio");
      }
      const pm = await res.json();
      alertPlaceholder.innerHTML = `
        <div class="alert alert-success alert-dismissible fade show" role="alert">
          Medio <strong>${pm.name}</strong> creado (ID: ${pm.id}).
          <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>`;
      form.reset();
    } catch (err) {
      alertPlaceholder.innerHTML = `
        <div class="alert alert-danger alert-dismissible fade show" role="alert">
          ${err.message}
          <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>`;
    }
  });
});
