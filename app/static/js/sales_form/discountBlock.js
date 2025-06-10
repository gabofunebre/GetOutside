// File: app/static/js/sales_form/discountBlock.js
////////////////////////////////////////////////////////////////////////////////
// DiscountBlock con recálculo dinámico usando TotalsCalculator.recalcFromDom y callback onRemove
////////////////////////////////////////////////////////////////////////////////

import { TotalsCalculator } from './totals.js';

export class DiscountBlock {
  /**
   * @param {Object} dom - referencias DOM para recálculo
   * @param {Function} onRemove - callback para eliminar instancia del array principal
   */
  constructor(dom, onRemove) {
    this.dom = dom;
    this.onRemove = onRemove;
    this.el = this.render();
    dom.descuentos.appendChild(this.el);
    this.bind();
    this.recalc();
  }

  /** Genera el HTML del bloque */
  render() {
    const div = document.createElement('div');
    div.className = 'descuento-block border rounded p-3 mb-3 position-relative';
    div.innerHTML = `
      <button type="button" class="btn-close btn-sm btn-quitar-descuento position-absolute top-0 end-0 m-2" aria-label="Quitar"></button>
      <div class="row mb-1">
        <div class="col"><label class="form-label">Concepto</label></div>
      </div>
      <div class="row align-items-end g-2">
        <div class="col">
          <input type="text" name="concepto" class="form-control">
        </div>
        <div class="col-auto">
          <input type="number" name="amount" class="form-control amount-input" step="0.01">
        </div>
      </div>
    `;
    return div;
  }

  /** Asocia evento de cambio y quitar */
  bind() {
    const amountInput = this.el.querySelector("[name='amount']");
    amountInput.addEventListener('input', () => this.recalc());

    this.el.querySelector('.btn-quitar-descuento').addEventListener('click', () => {
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
      concepto: this.el.querySelector("[name='concepto']").value,
      amount: Number(this.el.querySelector("[name='amount']").value)
    };
  }
}
