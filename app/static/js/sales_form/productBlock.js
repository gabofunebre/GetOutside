// File: app/static/js/sales_form/productBlock.js
////////////////////////////////////////////////////////////////////////////////
// ProductBlock actualizado con TotalsCalculator.recalcFromDom y callback onRemove
////////////////////////////////////////////////////////////////////////////////

import { Autocomplete } from './autocomplete.js';
import { TotalsCalculator } from './totals.js';

export class ProductBlock {
  constructor(data, dom, onRemove) {
    this.data = data;
    this.dom = dom;
    this.onRemove = onRemove;
    this.el = this.render();
    dom.productos.appendChild(this.el);
    this.bind();
    this.recalc();
  }

  // Renderiza el bloque de producto con campos necesarios
  render() {
    const d = document.createElement('div');
    d.className = 'producto-block border rounded p-3 mb-3 position-relative';
    d.innerHTML = `
      <button type="button" class="btn-close btn-sm btn-quitar-producto position-absolute top-0 end-0 m-2" aria-label="Quitar"></button>
      <div class="mb-2">
        <label class="form-label">Producto</label>
        <div class="autocomplete">
          <input type="text" name="codigo_getoutside" class="form-control autocomplete-input" placeholder="Buscar…" autocomplete="off" required>
          <input type="hidden" name="producto_id">
          <ul class="autocomplete-list"></ul>
        </div>
      </div>
      <div class="row mb-1">
        <div class="col"><label class="form-label">Cantidad</label></div>
        <div class="col"><label class="form-label">Precio</label></div>
        <div class="col text-end"><label class="form-label">Subtotal</label></div>
      </div>
      <div class="row align-items-center g-2">
        <div class="col">
          <input type="number" name="cantidad" class="form-control" value="1" min="1">
        </div>
        <div class="col-auto">&times;</div>
        <div class="col">
          <input type="number" name="precio_unitario" class="form-control" step="0.01">
        </div>
        <div class="col-auto">=</div>
        <div class="col">
          <span class="total-line">$<span class="subtotal">0.00</span></span>
        </div>
      </div>`;
    return d;
  }

  // Asocia eventos y lógica del bloque
  bind() {
    const inp = this.el.querySelector('.autocomplete-input');
    const list = this.el.querySelector('.autocomplete-list');
    const precioI = this.el.querySelector("[name='precio_unitario']");
    const qtyI = this.el.querySelector("[name='cantidad']");
    const idInput = this.el.querySelector("[name='producto_id']");

    new Autocomplete(inp, list, this.data, ds => {
      idInput.value = ds.id;
      precioI.value = ds.precio_venta;
      this.recalc();
    });

    [precioI, qtyI].forEach(i =>
      i.addEventListener('input', () => this.recalc())
    );

    this.el.querySelector('.btn-quitar-producto').addEventListener('click', () => {
      this.el.remove();
      if (typeof this.onRemove === 'function') {
        this.onRemove(this);
      }
      this.recalc();
    });
  }

  // Recalcula usando helper
  recalc() {
    TotalsCalculator.recalcFromDom(this.dom);
  }

  // Devuelve datos del producto para el backend
  getData() {
    return {
      producto_id: +this.el.querySelector("[name='producto_id']").value,
      cantidad: +this.el.querySelector("[name='cantidad']").value,
      precio_unitario: +this.el.querySelector("[name='precio_unitario']").value
    };
  }
}
