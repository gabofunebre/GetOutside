// payment_method_form.js
document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("pmForm");
  const alertPlaceholder = document.getElementById("alert-placeholder");
  const overlay = document.getElementById("overlay");
  const currencySelect = document.getElementById("currency");

  async function loadCurrencies() {
    try {
      const res = await fetch("/payment_methods/currencies");
      const data = await res.json();
      data.forEach(({ code, label }) => {
        const opt = document.createElement("option");
        opt.value = code;
        opt.textContent = label;
        currencySelect.appendChild(opt);
      });
    } catch (err) {
      console.error("Error cargando monedas:", err);
    }
  }

  loadCurrencies();

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    alertPlaceholder.innerHTML = "";
    overlay.style.display = "flex";

    const name = form.name.value.trim();
    const currency = form.currency.value;

    if (!name) {
      overlay.style.display = "none";
      alertPlaceholder.innerHTML = `
        <div class="alert alert-warning alert-dismissible fade show" role="alert">
          El nombre no puede estar vacío.
          <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>`;
      return;
    }

    try {
      const res = await fetch("/payment_methods/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, currency })
      });

      if (!res.ok) {
        const err = await res.json();
        if (err.detail && err.detail.includes("ya existe")) {
          throw new Error("Ya existe un medio de pago con ese nombre.");
        }
        throw new Error(err.detail || "Error al crear el medio");
      }

      const pm = await res.json();
      alertPlaceholder.innerHTML = `
        <div class="alert alert-success alert-dismissible fade show" role="alert">
          Medio <strong>${pm.name}</strong> (${pm.currency}) creado (ID: ${pm.id}).
          <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>`;
      form.reset();
    } catch (err) {
      alertPlaceholder.innerHTML = `
        <div class="alert alert-danger alert-dismissible fade show" role="alert">
          ${err.message}
          <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>`;
    } finally {
      overlay.style.display = "none";
    }
  });
});
