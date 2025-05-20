// File: app/static/js/sales_form/main.js
////////////////////////////////////////////////////////////////////////////////
// Main entry: inicializa SalesForm
////////////////////////////////////////////////////////////////////////////////
import { ProductBlock }   from './productBlock.js';
import { TotalsCalculator } from './totals.js';
import { Autocomplete }     from './autocomplete.js';

class SalesForm {
  constructor(config) {
    this.data = config.data;
    this.dom  = config.dom;
    this.productBlocks = [];
    this.bind();
    this.init();
  }
  bind() {
    this.dom.addItem.addEventListener('click', () => this.addProduct());
    this.dom.submit.addEventListener('click', () => this.submit());
  }
  init() { this.addProduct(); }
  addProduct() { this.productBlocks.push(new ProductBlock(this.data.productos, this.dom)); }
  async submit() {
    this.dom.alert.innerHTML = '';
    this.dom.overlay.style.display = 'flex';
    const detalles = this.productBlocks.map(b => b.getData());
    try {
      const res = await fetch('/ventas', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({detalles}) });
      if (!res.ok) throw new Error((await res.json()).detail || 'Error');
      const venta = await res.json();
      this.dom.alert.innerHTML = `<div class="alert alert-success">Venta #${venta.id}</div>`;
    } catch(e) {
      this.dom.alert.innerHTML = `<div class="alert alert-danger">${e.message}</div>`;
    } finally { this.dom.overlay.style.display = 'none'; }
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const dom = {
    productos: document.getElementById('productos-container'),
    pagos: document.getElementById('pagos-container'),
    descuentos: document.getElementById('descuentos-container'),
    totals: { venta: document.getElementById('total-venta'), pago: document.getElementById('total-pago') },
    alert: document.getElementById('alert-placeholder'),
    overlay: document.getElementById('overlay'),
    addItem: document.getElementById('add-item'),
    submit: document.getElementById('submit-sale')
  };
  new SalesForm({ data: { productos: window.productosData }, dom });
});
