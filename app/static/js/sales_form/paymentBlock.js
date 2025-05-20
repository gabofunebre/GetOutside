// File: app/static/js/sales_form/paymentBlock.js
////////////////////////////////////////////////////////////////////////////////
// PaymentBlock
// Maneja un bloque de pago: selector de medio y monto
////////////////////////////////////////////////////////////////////////////////
import { TotalsCalculator } from './totals.js';

export class PaymentBlock {
  /**
   * @param {Array} mediosData - lista de medios de pago
   * @param {Object} dom - referencias DOM para recálculo
   */
  constructor(mediosData, dom) {
    this.mediosData = mediosData;
    this.dom = dom;
    this.el = this.render();
    dom.pagos.appendChild(this.el);
    this.bindEvents();
    // Inicializar recálculo
    TotalsCalculator.recalcAll(dom.productos, dom.pagos, dom.totals.venta, dom.totals.pago);
  }

  /** Genera el HTML del bloque */
  render() {
    const options = this.mediosData
      .map(m => `<option value="${m.id}">${m.name}</option>`)
      .join('');
    const div = document.createElement('div');
    div.className = 'pago-block border rounded p-3 mb-3 bg-light';
    div.innerHTML = `
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
    return div;
  }

  /** Asocia eventos de monto, selector y quitar */
  bindEvents() {
    const select = this.el.querySelector('select');
    const amount = this.el.querySelector("[name='amount']");
    select.addEventListener('input', () => TotalsCalculator.recalcAll(
      this.dom.productos,
      this.dom.pagos,
      this.dom.totals.venta,
      this.dom.totals.pago
    ));
    amount.addEventListener('input', () => TotalsCalculator.recalcAll(
      this.dom.productos,
      this.dom.pagos,
      this.dom.totals.venta,
      this.dom.totals.pago
    ));
    this.el.querySelector('.btn-quitar-pago').addEventListener('click', () => {
      this.el.remove();
      TotalsCalculator.recalcAll(
        this.dom.productos,
        this.dom.pagos,
        this.dom.totals.venta,
        this.dom.totals.pago
      );
    });
  }

  /** Devuelve datos para el envío */
  getData() {
    return {
      payment_method_id: Number(this.el.querySelector("[name='payment_method_id']").value),
      amount: Number(this.el.querySelector("[name='amount']").value)
    };
  }
}
