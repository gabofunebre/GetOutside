// File: app/static/js/sales_form/discountBlock.js
////////////////////////////////////////////////////////////////////////////////
// DiscountBlock
// Maneja un bloque de descuento: concepto y monto
////////////////////////////////////////////////////////////////////////////////

export class DiscountBlock {
  /**
   * @param {Object} dom - referencias DOM para recálculo
   */
  constructor(dom) {
    this.dom = dom;
    this.el = this.render();
    dom.descuentos.appendChild(this.el);
    this.bind();
  }

  /** Genera el HTML del bloque */
  render() {
    const div = document.createElement('div');
    div.className = 'descuento-block border rounded p-3 mb-3 bg-light';
    div.innerHTML = `
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
    return div;
  }

  /** Asocia evento quitar */
  bind() {
    this.el.querySelector('.btn-quitar-descuento').addEventListener('click', () => this.el.remove());
  }

  /** Devuelve datos para el envío */
  getData() {
    return {
      concepto: this.el.querySelector("[name='concepto']").value,
      amount: Number(this.el.querySelector("[name='amount']").value)
    };
  }
}
