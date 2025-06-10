////////////////////////////////////////////////////////////////////////////////
// ChangeBlock: registra un vuelto con medio de pago y monto
////////////////////////////////////////////////////////////////////////////////
import { TotalsCalculator } from './totals.js';

export class ChangeBlock {
  constructor(mediosData, dom, onRemove, defaultAmount = 0) {
    this.mediosData = mediosData;
    this.dom = dom;
    this.onRemove = onRemove;
    this.el = this.render(defaultAmount);
    dom.vueltos.appendChild(this.el);
    this.bindEvents();
    this.recalc();
  }

  render(defaultAmount) {
    const options = this.mediosData
      .map(m => `<option value="${m.id}" data-currency="${m.currency}">${m.name} - ${m.currency_label} ${m.currency}</option>`)
      .join('');
    const div = document.createElement('div');
    div.className = 'vuelto-block border rounded p-3 mb-3 position-relative';
    div.innerHTML = `
      <button type="button" class="btn-close btn-sm btn-quitar-vuelto position-absolute top-0 end-0 m-2" aria-label="Quitar"></button>
      <div class="row mb-1">
        <div class="col"><label class="form-label">Medio del Vuelto</label></div>
      </div>
      <div class="row align-items-end g-2">
        <div class="col">
          <select name="payment_method_id" class="form-select">${options}</select>
        </div>
        <div class="col-auto">
          <input type="number" name="amount" class="form-control amount-input" step="0.01" value="${defaultAmount}">
        </div>
      </div>`;
    return div;
  }

  bindEvents() {
    const select = this.el.querySelector('select');
    const amount = this.el.querySelector("[name='amount']");
    select.addEventListener('input', () => this.recalc());
    amount.addEventListener('input', () => this.recalc());

    this.el.querySelector('.btn-quitar-vuelto').addEventListener('click', () => {
      this.el.remove();
      if (typeof this.onRemove === 'function') {
        this.onRemove(this);
      }
      this.recalc();
    });
  }

  recalc() {
    TotalsCalculator.recalcFromDom(this.dom);
  }

  getData() {
    return {
      payment_method_id: Number(this.el.querySelector("[name='payment_method_id']").value),
      amount: Number(this.el.querySelector("[name='amount']").value)
    };
  }
}
