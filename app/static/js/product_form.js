// app/static/js/product_form.js
document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("productForm");
    const alertPlaceholder = document.getElementById("alert-placeholder");
  
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      alertPlaceholder.innerHTML = "";
  
      const formData = new FormData(form);
      const payload = {};
      formData.forEach((value, key) => {
        payload[key] = isNaN(value) ? value : Number(value);
      });
  
      try {
        const res = await fetch("/productos", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
  
        if (!res.ok) {
          const err = await res.json();
          throw new Error(err.detail || "Error al crear el producto");
        }
  
        const product = await res.json();
        alertPlaceholder.innerHTML = `
          <div class="alert alert-success alert-dismissible fade show" role="alert">
            Producto <strong>${product.codigo_getoutside}</strong> creado con éxito.
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
          </div>
        `;
        form.reset();
      } catch (error) {
        alertPlaceholder.innerHTML = `
          <div class="alert alert-danger alert-dismissible fade show" role="alert">
            ${error.message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
          </div>
        `;
      }
    });
  });
  