// File: app/static/js/sales_form/paymentBlock.js
////////////////////////////////////////////////////////////////////////////////
// PaymentBlock con TotalsCalculator.recalcFromDom y callback onRemove
////////////////////////////////////////////////////////////////////////////////

import { TotalsCalculator } from './totals.js';

export class PaymentBlock {
  constructor(mediosData, dom, onRemove) {
    this.mediosData = mediosData;
    this.dom = dom;
    this.onRemove = onRemove;
    this.el = this.render();
    dom.pagos.appendChild(this.el);
    this.bindEvents();
    this.recalc();
  }

  /** Genera el HTML del bloque */
  render() {
    const options = this.mediosData
      .map(m => `<option value="${m.id}" data-currency="${m.currency}">${m.name} - ${m.currency_label} ${m.currency}</option>`)
      .join('');
    const div = document.createElement('div');
    div.className = 'pago-block border rounded p-3 mb-3 bg-light';
    div.innerHTML = `
      <div class="mb-2">
        <label class="form-label">Medio de Pago</label>
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

  /** Asocia eventos para recalcular totales dinámicamente */
  bindEvents() {
    const select = this.el.querySelector('select');
    const amount = this.el.querySelector("[name='amount']");

    select.addEventListener('input', () => this.recalc());
    amount.addEventListener('input', () => this.recalc());

    this.el.querySelector('.btn-quitar-pago').addEventListener('click', () => {
      this.el.remove();
      if (typeof this.onRemove === 'function') {
        this.onRemove(this);
      }
      this.recalc();
    });
  }

  /** Recalcula todos los totales */
  recalc() {
    TotalsCalculator.recalcFromDom(this.dom);
  }

  /** Devuelve datos para el envío */
  getData() {
    return {
      payment_method_id: Number(this.el.querySelector("[name='payment_method_id']").value),
      amount: Number(this.el.querySelector("[name='amount']").value)
    };
  }
}
