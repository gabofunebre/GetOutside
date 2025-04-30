// app/static/js/sales_form.js
document.addEventListener("DOMContentLoaded", () => {
    const alertPlaceholder = document.getElementById("alert-placeholder");
    const itemsTable = document.getElementById("items-table").querySelector("tbody");
    const paymentsTable = document.getElementById("payments-table").querySelector("tbody");
    const addItemBtn = document.getElementById("add-item");
    const addPaymentBtn = document.getElementById("add-payment");
    const totalVentaEl = document.getElementById("total-venta");
    const totalPagoEl = document.getElementById("total-pago");
    const submitBtn = document.getElementById("submit-sale");
  
    // Ahora sí leemos las variables inyectadas en el HTML
    const productos = window.productosData;
    const medios    = window.mediosData;
  
    function formatNum(n) { return n.toFixed(2); }
  
    function recalcTotals() {
      let totalV = 0, totalP = 0;
      itemsTable.querySelectorAll("tr").forEach(row => {
        const qty   = Number(row.querySelector("[name='cantidad']").value) || 0;
        const price = Number(row.querySelector("[name='precio_unitario']").value) || 0;
        const sub   = qty * price;
        row.querySelector(".subtotal").textContent = formatNum(sub);
        totalV += sub;
      });
      totalVentaEl.textContent = formatNum(totalV);
  
      paymentsTable.querySelectorAll("tr").forEach(row => {
        totalP += Number(row.querySelector("[name='amount']").value) || 0;
      });
      totalPagoEl.textContent = formatNum(totalP);
    }
  
    function addRow(table, html) {
      const tr = document.createElement("tr");
      tr.innerHTML = html + `<td><button class="btn btn-sm btn-danger remove">×</button></td>`;
      table.appendChild(tr);
      tr.querySelector(".remove").addEventListener("click", () => {
        tr.remove();
        recalcTotals();
      });
      tr.querySelectorAll("input, select").forEach(el => {
        el.addEventListener("input", recalcTotals);
      });
    }
  
    // Botón + Añadir producto
    addItemBtn.addEventListener("click", () => {
      const options = productos.map(p =>
        `<option value="${p.codigo_getoutside}">${p.codigo_getoutside} — ${p.tipo}</option>`
      ).join("");
      addRow(itemsTable, `
        <td><select name="codigo_getoutside" class="form-select">${options}</select></td>
        <td><input type="number" name="cantidad" class="form-control" value="1" min="1"></td>
        <td><input type="number" name="precio_unitario" class="form-control" step="0.01"></td>
        <td class="subtotal">0.00</td>
      `);
    });
  
    // Botón + Añadir pago
    addPaymentBtn.addEventListener("click", () => {
      const options = medios.map(m =>
        `<option value="${m.id}">${m.name}</option>`
      ).join("");
      addRow(paymentsTable, `
        <td><select name="payment_method_id" class="form-select">${options}</select></td>
        <td><input type="number" name="amount" class="form-control" step="0.01"></td>
      `);
    });
  
    // Enviar la venta
    submitBtn.addEventListener("click", async () => {
      alertPlaceholder.innerHTML = "";
      const detalles = Array.from(itemsTable.querySelectorAll("tr")).map(row => ({
        codigo_getoutside: row.querySelector("[name='codigo_getoutside']").value,
        cantidad:          Number(row.querySelector("[name='cantidad']").value),
        precio_unitario:   Number(row.querySelector("[name='precio_unitario']").value)
      }));
      const pagos = Array.from(paymentsTable.querySelectorAll("tr")).map(row => ({
        payment_method_id: Number(row.querySelector("[name='payment_method_id']").value),
        amount:            Number(row.querySelector("[name='amount']").value)
      }));
      try {
        const res = await fetch("/ventas", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ detalles, pagos })
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
        itemsTable.innerHTML = "";
        paymentsTable.innerHTML = "";
        recalcTotals();
        // agrega una fila para poder seguir usando el form
        addItemBtn.click();
        addPaymentBtn.click();
      } catch (e) {
        alertPlaceholder.innerHTML = `
          <div class="alert alert-danger" role="alert">
            ${e.message}
          </div>`;
      }
    });
  
    // Filas iniciales
    addItemBtn.click();
    addPaymentBtn.click();
  });
  