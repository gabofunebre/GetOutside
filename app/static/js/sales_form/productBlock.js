// File: app/static/js/sales_form/productBlock.js
////////////////////////////////////////////////////////////////////////////////
// ProductBlock
////////////////////////////////////////////////////////////////////////////////
import { Autocomplete } from './autocomplete.js';
import { TotalsCalculator } from './totals.js';

export class ProductBlock {
  constructor(data, dom) {
    this.data = data;
    this.dom = dom;
    this.el = this.render();
    dom.productos.appendChild(this.el);
    this.bind();
    TotalsCalculator.recalcAll(dom.productos, dom.pagos, dom.totals.venta, dom.totals.pago);
  }
  render() {
    const d = document.createElement('div'); d.className = 'producto-block border rounded p-3 mb-3 bg-light';
    d.innerHTML = `
      <div class="mb-2">
        <label class="form-label">Producto</label>
        <div class="autocomplete">
          <input type="text" name="codigo_getoutside" class="form-control autocomplete-input" placeholder="Buscar…" autocomplete="off" required>
          <ul class="autocomplete-list"></ul>
        </div>
      </div>
      <div class="row mb-2">
        <div class="col"><label class="form-label">Cantidad</label><input type="number" name="cantidad" class="form-control" value="1" min="1"></div>
        <div class="col"><label class="form-label">Precio</label><input type="number" name="precio_unitario" class="form-control" step="0.01"></div>
      </div>
      <div class="d-flex justify-content-between align-items-center">
        <span>Total: $<span class="subtotal">0.00</span></span>
        <button class="btn btn-danger btn-sm btn-quitar-producto">Quitar</button>
      </div>`;
    return d;
  }
  bind() {
    const inp = this.el.querySelector('.autocomplete-input');
    const list= this.el.querySelector('.autocomplete-list');
    const precioI = this.el.querySelector("[name='precio_unitario']");
    const qtyI = this.el.querySelector("[name='cantidad']");
    new Autocomplete(inp, list, this.data, ds => { precioI.value = ds.precio; TotalsCalculator.recalcAll(this.dom.productos, this.dom.pagos, this.dom.totals.venta, this.dom.totals.pago); });
    [precioI, qtyI].forEach(i => i.addEventListener('input', () => TotalsCalculator.recalcAll(this.dom.productos, this.dom.pagos, this.dom.totals.venta, this.dom.totals.pago)));
    this.el.querySelector('.btn-quitar-producto').addEventListener('click', () => { this.el.remove(); TotalsCalculator.recalcAll(this.dom.productos, this.dom.pagos, this.dom.totals.venta, this.dom.totals.pago); });
  }
  getData() {
    return {
      codigo_getoutside: this.el.querySelector("[name='codigo_getoutside']").value,
      cantidad: +this.el.querySelector("[name='cantidad']").value,
      precio_unitario: +this.el.querySelector("[name='precio_unitario']").value
    };
  }
}