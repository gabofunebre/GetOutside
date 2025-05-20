document.addEventListener("DOMContentLoaded", () => {
  const productos = window.productosData;
  const medios = window.mediosData;

  const productosContainer = document.getElementById("productos-container");
  const pagosContainer     = document.getElementById("pagos-container");
  const descuentosContainer= document.getElementById("descuentos-container");
  const addItemBtn         = document.getElementById("add-item");
  const addPaymentBtn      = document.getElementById("add-payment");
  const addDiscountBtn     = document.getElementById("add-discount");
  const totalVentaEl       = document.getElementById("total-venta");
  const totalPagoEl        = document.getElementById("total-pago");
  const submitBtn          = document.getElementById("submit-sale");
  const alertPlaceholder   = document.getElementById("alert-placeholder");
  const overlay            = document.getElementById("overlay"); // ← overlay

  function formatNum(n) {
    return n.toFixed(2);
  }

  function recalcTotals() {
    let totalV = 0;
    productosContainer.querySelectorAll(".producto-block").forEach(block => {
      const qty = Number(block.querySelector("[name='cantidad']").value) || 0;
      const price = Number(block.querySelector("[name='precio_unitario']").value) || 0;
      const sub = qty * price;
      block.querySelector(".subtotal").textContent = formatNum(sub);
      totalV += sub;
    });
    totalVentaEl.textContent = formatNum(totalV);

    let totalP = 0;
    pagosContainer.querySelectorAll(".pago-block").forEach(block => {
      totalP += Number(block.querySelector("[name='amount']").value) || 0;
    });
    totalPagoEl.textContent = formatNum(totalP);
  }

  // ... funciones addProductoItem, addPaymentRow, addDiscountRow idénticas ...

  addItemBtn.addEventListener("click", addProductoItem);
  addPaymentBtn.addEventListener("click", addPaymentRow);
  addDiscountBtn.addEventListener("click", addDiscountRow);

  submitBtn.addEventListener("click", async () => {
    alertPlaceholder.innerHTML = "";
    overlay.style.display = "flex";  // ← muestra spinner

    const detalles = Array.from(productosContainer.querySelectorAll(".producto-block")).map(block => ({
      codigo_getoutside: block.querySelector("[name='codigo_getoutside']").value,
      cantidad: Number(block.querySelector("[name='cantidad']").value),
      precio_unitario: Number(block.querySelector("[name='precio_unitario']").value)
    }));
    const pagos = Array.from(pagosContainer.querySelectorAll(".pago-block")).map(block => ({
      payment_method_id: Number(block.querySelector("[name='payment_method_id']").value),
      amount: Number(block.querySelector("[name='amount']").value)
    }));
    const descuentos = Array.from(descuentosContainer.querySelectorAll(".descuento-block")).map(block => ({
      concepto: block.querySelector("[name='concepto']").value,
      amount: Number(block.querySelector("[name='amount']").value)
    }));

    try {
      const res = await fetch("/ventas", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ detalles, pagos, descuentos })
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Error al registrar la venta");
      }
      const venta = await res.json();
      alertPlaceholder.innerHTML = `
        <div class="alert alert-success" role="alert">
          Venta #${venta.id} registrada. Total: ${venta.total.toFixed(2)}
        </div>`;
      productosContainer.innerHTML = "";
      pagosContainer.innerHTML = "";
      descuentosContainer.innerHTML = "";
      recalcTotals();
      addProductoItem();
      addPaymentRow();
    } catch (e) {
      alertPlaceholder.innerHTML = `
        <div class="alert alert-danger" role="alert">
          ${e.message}
        </div>`;
    } finally {
      overlay.style.display = "none"; // ← oculta spinner
    }
  });

  // Inicializa un bloque por defecto
  addProductoItem();
  addPaymentRow();
});
