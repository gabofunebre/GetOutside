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
    d.className = 'producto-block border rounded p-3 mb-3';
    d.innerHTML = `
      <div class="mb-2">
        <label class="form-label">Producto</label>
        <div class="autocomplete">
          <input type="text" name="codigo_getoutside" class="form-control autocomplete-input" placeholder="Buscar…" autocomplete="off" required>
          <input type="hidden" name="producto_id">
          <ul class="autocomplete-list"></ul>
        </div>
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
        <span class="total-line">Total: $<span class="subtotal">0.00</span></span>
        <button class="btn btn-danger btn-sm btn-quitar-producto">Quitar</button>
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
