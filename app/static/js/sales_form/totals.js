// File: app/static/js/sales_form/totals.js
////////////////////////////////////////////////////////////////////////////////
// TotalsCalculator
////////////////////////////////////////////////////////////////////////////////
export class TotalsCalculator {
  static recalcAll(prodContainer, pagoContainer, elVenta, elPago) {
    let venta = 0;
    prodContainer.querySelectorAll('.producto-block').forEach(b => {
      const qty = +b.querySelector("[name='cantidad']").value || 0;
      const price = +b.querySelector("[name='precio_unitario']").value || 0;
      const sub = qty * price;
      b.querySelector('.subtotal').textContent = sub.toFixed(2);
      venta += sub;
    }); elVenta.textContent = venta.toFixed(2);

    let pago = 0;
    pagoContainer.querySelectorAll('.pago-block').forEach(b => { pago += +b.querySelector("[name='amount']").value || 0; });
    elPago.textContent = pago.toFixed(2);
  }
}