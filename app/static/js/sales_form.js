// app/static/js/sales_form.js

document.addEventListener("DOMContentLoaded", () => {
  const productos = window.productosData;
  const medios = window.mediosData;

  const productosContainer = document.getElementById("productos-container");
  const pagosContainer = document.getElementById("pagos-container");
  const descuentosContainer = document.getElementById("descuentos-container");
  const addItemBtn = document.getElementById("add-item");
  const addPaymentBtn = document.getElementById("add-payment");
  const addDiscountBtn = document.getElementById("add-discount");
  const totalVentaEl = document.getElementById("total-venta");
  const totalPagoEl = document.getElementById("total-pago");
  const submitBtn = document.getElementById("submit-sale");
  const alertPlaceholder = document.getElementById("alert-placeholder");

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

  function addProductoItem() {
    const options = productos.map(p =>
      `<option value="${p.codigo_getoutside}" data-precio="${p.precio_venta}">${p.codigo_getoutside} — ${p.descripcion}</option>`
    ).join("");

    const block = document.createElement("div");
    block.className = "producto-block border rounded p-3 mb-3 bg-light";
    block.innerHTML = `
      <div class="mb-2">
        <label class="form-label">Producto</label>
        <select name="codigo_getoutside" class="form-select">${options}</select>
      </div>
      <div class="row mb-2">
        <div class="col">
          <label class="form-label">Cantidad</label>
          <input type="number" name="cantidad" class="form-control" value="1" min="1">
        </div>
        <div class="col">
          <label class="form-label">Precio</label>
          <input type="number" name="precio_unitario" class="form-control" step="0.01">
        </div>
      </div>
      <div class="d-flex justify-content-between align-items-center">
        <span>Total: $<span class="subtotal">0.00</span></span>
        <button class="btn btn-danger btn-sm btn-quitar-producto">Quitar</button>
      </div>
    `;
    productosContainer.appendChild(block);

    const select = block.querySelector("select");
    const precioInput = block.querySelector("[name='precio_unitario']");
    const qtyInput = block.querySelector("[name='cantidad']");

    select.addEventListener("change", () => {
      const selected = select.selectedOptions[0];
      if (selected) {
        precioInput.value = selected.dataset.precio;
      }
      recalcTotals();
    });

    [precioInput, qtyInput].forEach(input =>
      input.addEventListener("input", () => recalcTotals())
    );

    block.querySelector(".btn-quitar-producto").addEventListener("click", () => {
      block.remove();
      recalcTotals();
    });

    select.dispatchEvent(new Event("change"));
  }

  function addPaymentRow() {
    const options = medios.map(m =>
      `<option value="${m.id}">${m.name}</option>`
    ).join("");

    const block = document.createElement("div");
    block.className = "pago-block border rounded p-3 mb-3 bg-light";
    block.innerHTML = `
      <div class="mb-2">
        <label class="form-label">Medio</label>
        <select name="payment_method_id" class="form-select">${options}</select>
      </div>
      <div class="row mb-2">
        <div class="col">
          <label class="form-label">Monto</label>
          <input type="number" name="amount" class="form-control" step="0.01">
        </div>
        <div class="col-auto d-flex flex-column justify-content-end">
          <label class="form-label invisible">Quitar</label>
          <button class="btn btn-danger btn-quitar-pago">Quitar</button>
        </div>
      </div>
    `;
    pagosContainer.appendChild(block);

    block.querySelector(".btn-quitar-pago").addEventListener("click", () => {
      block.remove();
      recalcTotals();
    });

    block.querySelectorAll("input, select").forEach(el => {
      el.addEventListener("input", recalcTotals);
    });
  }

  function addDiscountRow() {
    const block = document.createElement("div");
    block.className = "descuento-block border rounded p-3 mb-3 bg-light";
    block.innerHTML = `
      <div class="mb-2">
        <label class="form-label">Concepto de Descuento</label>
        <input type="text" name="concepto" class="form-control">
      </div>
      <div class="row mb-2">
        <div class="col">
          <label class="form-label">Monto</label>
          <input type="number" name="amount" class="form-control" step="0.01">
        </div>
        <div class="col-auto d-flex flex-column justify-content-end">
          <label class="form-label invisible">Quitar</label>
          <button class="btn btn-danger btn-quitar-descuento">Quitar</button>
        </div>
      </div>
    `;
    descuentosContainer.appendChild(block);

    block.querySelector(".btn-quitar-descuento").addEventListener("click", () => {
      block.remove();
    });
  }

  addItemBtn.addEventListener("click", addProductoItem);
  addPaymentBtn.addEventListener("click", addPaymentRow);
  addDiscountBtn.addEventListener("click", addDiscountRow);

  submitBtn.addEventListener("click", async () => {
    alertPlaceholder.innerHTML = "";
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
    }
  });

  addProductoItem();
  addPaymentRow();
});
