////////////////////////////////////////////////////////////////////////////////
// ChangeBlock: registra un vuelto con medio de pago y monto
////////////////////////////////////////////////////////////////////////////////
import { TotalsCalculator } from './totals.js';

export class ChangeBlock {
  constructor(mediosData, dom, onRemove) {
    this.mediosData = mediosData;
    this.dom = dom;
    this.onRemove = onRemove;
    this.el = this.render();
    dom.vueltos.appendChild(this.el);
    this.bindEvents();
    this.recalc();
  }

  render() {
    const options = this.mediosData
      .map(m => `<option value="${m.id}" data-currency="${m.currency}">${m.name} - ${m.currency_label} ${m.currency}</option>`)
      .join('');
    const div = document.createElement('div');
    div.className = 'vuelto-block border rounded p-3 mb-3';
    div.innerHTML = `
      <div class="mb-2">
        <label class="form-label">Medio del Vuelto</label>
        <select name="payment_method_id" class="form-select">${options}</select>
      </div>
      <div class="row mb-2">
        <div class="col">
          <label class="form-label">Monto</label>
          <input type="number" name="amount" class="form-control" step="0.01">
        </div>
        <div class="col-auto d-flex flex-column justify-content-end">
          <label class="form-label invisible">Quitar</label>
          <button class="btn btn-danger btn-quitar-vuelto">Quitar</button>
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
