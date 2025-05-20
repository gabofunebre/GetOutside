////////////////////////////////////////////////////////////////////////////////
// main.js
// Entry point: inicializa SalesForm con Product, Payment y Discount Blocks
////////////////////////////////////////////////////////////////////////////////

import { ProductBlock } from './productBlock.js';
import { PaymentBlock } from './paymentBlock.js';
import { DiscountBlock } from './discountBlock.js';

class SalesForm {
  constructor({ productosData, mediosData, dom }) {
    this.productosData = productosData;
    this.mediosData    = mediosData;
    this.dom           = dom;
    this.productBlocks = [];
    this.paymentBlocks = [];
    this.discountBlocks = [];
    this.bind();
    this.init();
  }

  // Asocia eventos a botones estáticos
  bind() {
    this.dom.addItem.addEventListener('click', () => this.addProduct());
    this.dom.addPayment.addEventListener('click', () => this.addPayment());
    this.dom.addDiscount.addEventListener('click', () => this.addDiscount());
    this.dom.submit.addEventListener('click', () => this.submit());
  }

  // Inicializa bloques por defecto
  init() {
    this.addProduct();
    this.addPayment();
  }

  // Añade un bloque de producto
  addProduct() {
    const block = new ProductBlock(this.productosData, this.dom);
    this.productBlocks.push(block);
  }

  // Añade un bloque de pago
  addPayment() {
    const block = new PaymentBlock(this.mediosData, this.dom);
    this.paymentBlocks.push(block);
  }

  // Añade un bloque de descuento
  addDiscount() {
    const block = new DiscountBlock(this.dom);
    this.discountBlocks.push(block);
  }

  // Maneja el envío del formulario
  async submit() {
    this.dom.alert.innerHTML = '';
    this.dom.overlay.style.display = 'flex';

    const detalles   = this.productBlocks.map(b => b.getData());
    const pagos      = this.paymentBlocks.map(b => b.getData());
    const descuentos = this.discountBlocks.map(b => b.getData());

    try {
      const res = await fetch('/ventas', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ detalles, pagos, descuentos })
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Error al registrar la venta');
      }
      const venta = await res.json();
      this.dom.alert.innerHTML = `<div class="alert alert-success" role="alert">
        Venta #${venta.id} registrada. Total: ${venta.total.toFixed(2)}
      </div>`;

      // Limpia y reinicia bloques y totales
      this.dom.productos.innerHTML   = '';
      this.dom.pagos.innerHTML       = '';
      this.dom.descuentos.innerHTML  = '';
      this.productBlocks = [];
      this.paymentBlocks = [];
      this.discountBlocks = [];

      this.dom.totals.venta.textContent = '0.00';
      this.dom.totals.pago.textContent  = '0.00';

      this.init();
    } catch (e) {
      this.dom.alert.innerHTML = `<div class="alert alert-danger" role="alert">
        ${e.message}
      </div>`;
    } finally {
      this.dom.overlay.style.display = 'none';
    }
  }
}

// Inicialización al cargar página
document.addEventListener('DOMContentLoaded', () => {
  const dom = {
    productos:   document.getElementById('productos-container'),
    pagos:       document.getElementById('pagos-container'),
    descuentos:  document.getElementById('descuentos-container'),
    totals: {
      venta: document.getElementById('total-venta'),
      pago:  document.getElementById('total-pago')
    },
    alert:       document.getElementById('alert-placeholder'),
    overlay:     document.getElementById('overlay'),
    addItem:     document.getElementById('add-item'),
    addPayment:  document.getElementById('add-payment'),
    addDiscount: document.getElementById('add-discount'),
    submit:      document.getElementById('submit-sale')
  };

  new SalesForm({
    productosData: window.productosData,
    mediosData:    window.mediosData,
    dom
  });
});
