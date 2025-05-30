////////////////////////////////////////////////////////////////////////////////
// main.js
// Entry point: inicializa SalesForm con Product, Payment y Discount Blocks
////////////////////////////////////////////////////////////////////////////////

import { ProductBlock } from './productBlock.js';
import { PaymentBlock } from './paymentBlock.js';
import { DiscountBlock } from './discountBlock.js';
import { TotalsCalculator } from './totals.js';

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

  bind() {
    this.dom.addItem.addEventListener('click', () => this.addProduct());
    this.dom.addPayment.addEventListener('click', () => this.addPayment());
    this.dom.addDiscount.addEventListener('click', () => this.addDiscount());
    this.dom.submit.addEventListener('click', () => this.showResumenModal());

    const confirmBtn = document.getElementById('confirmar-venta');
    confirmBtn.addEventListener('click', () => this.submit());

    // Limpia mensaje al cerrar modal (por botón Editar)
    document.querySelector('#resumen-modal .btn-secondary')
      .addEventListener('click', () => {
        document.getElementById('modal-message').innerHTML = '';
    });
  }

  init() {
    this.addProduct();
    this.addPayment();
  }

  addProduct() {
    const block = new ProductBlock(this.productosData, this.dom, (bloque) => {
      this.productBlocks = this.productBlocks.filter(b => b !== bloque);
    });
    this.productBlocks.push(block);
  }

  addPayment() {
    const block = new PaymentBlock(this.mediosData, this.dom, (bloque) => {
      this.paymentBlocks = this.paymentBlocks.filter(b => b !== bloque);
    });
    this.paymentBlocks.push(block);
  }

  addDiscount() {
    const block = new DiscountBlock(this.dom, (bloque) => {
      this.discountBlocks = this.discountBlocks.filter(b => b !== bloque);
    });
    this.discountBlocks.push(block);
  }

  async showResumenModal() {
    await TotalsCalculator.recalcAll(
      this.dom.productos,
      this.dom.pagos,
      this.dom.descuentos,
      this.dom.totals.venta,
      this.dom.totals.pago,
      this.dom.totals.descuentos,
      this.dom.totals.faltante
    );

    const detalles   = this.productBlocks.map(b => b.getData());
    const descuentos = this.discountBlocks.map(b => b.getData());
    const pagos      = this.paymentBlocks.map(b => b.getData());

    // Rediseño: resumen menos tabulado, orden tipo ticket
    let texto = '';
    texto += '======= RESUMEN DE VENTA =======\n\n';
    texto += 'Productos:\n';
    let subtotal = 0;
    for (const d of detalles) {
      // Buscar el producto por id para mostrar el código
      const prod = this.productosData.find(p => p.id === d.producto_id);
      const codigo = prod ? prod.codigo_getoutside : `ID:${d.producto_id}`;
      texto += `  ${codigo.padEnd(12)} $${d.precio_unitario.toFixed(2)} x${d.cantidad}\n`;
      subtotal += d.cantidad * d.precio_unitario;
    }
    texto += `\nSUBTOTAL:      $${subtotal.toFixed(2)} NZD\n`;

    let totalDesc = 0;
    if (descuentos.length) {
      texto += '\nDescuentos:\n';
      for (const d of descuentos) {
        texto += `  ${d.concepto.slice(0,12).padEnd(12)} -$${d.amount.toFixed(2)} NZD\n`;
        totalDesc += d.amount;
      }
    }
    const totalFinal = subtotal - totalDesc;
    texto += `\n-------------------------------\n`;
    texto += `TOTAL:         $${totalFinal.toFixed(2)} NZD\n`;

    let totalPagado = 0;
    if (pagos.length) {
      texto += '\nPagos:\n';
      for (const p of pagos) {
        const medio = this.mediosData.find(m => m.id === p.payment_method_id);
        if (!medio) continue;
        let linea = `  ${medio.name.slice(0,12).padEnd(12)} $${p.amount.toFixed(2)} ${medio.currency}`;
        if (medio.currency !== 'NZD') {
          const res = await fetch(`https://api.frankfurter.app/latest?from=${medio.currency}&to=NZD&amount=${p.amount}`);
          const data = await res.json();
          const convertido = data.rates['NZD'];
          totalPagado += convertido;
          linea += ` (=${convertido.toFixed(2)} NZD)`;
        } else {
          totalPagado += p.amount;
        }
        texto += `${linea}\n`;
      }
    }
    texto += `\nTOTAL PAGADO:  $${totalPagado.toFixed(2)} NZD\n`;
    const faltan = Math.max(0, totalFinal - totalPagado);
    texto += `FALTAN:        $${faltan.toFixed(2)} NZD`;

    document.getElementById('resumen-texto').textContent = texto;
    document.getElementById('modal-message').innerHTML = ''; // Limpia mensaje
    const modal = new bootstrap.Modal(document.getElementById('resumen-modal'));
    modal.show();
  }

  async submit() {
    const modalMessage = document.getElementById('modal-message');
    modalMessage.innerHTML = ''; // Limpia el mensaje anterior
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

      // Cierra el modal si está abierto
      const modalEl = document.getElementById('resumen-modal');
      const modalInstancia = bootstrap.Modal.getInstance(modalEl);
      if (modalInstancia) modalInstancia.hide();

      // Muestra mensaje de éxito DENTRO DEL MODAL
      modalMessage.innerHTML = `<div class="alert alert-success" role="alert">
        Venta #${venta.id} registrada. Total: ${venta.total.toFixed(2)}
      </div>`;

      // Limpia y reinicia todo
      this.dom.productos.innerHTML = '';
      this.dom.pagos.innerHTML = '';
      this.dom.descuentos.innerHTML = '';
      this.productBlocks = [];
      this.paymentBlocks = [];
      this.discountBlocks = [];

      this.dom.totals.venta.textContent     = '0.00 NZD';
      this.dom.totals.pago.textContent      = '0.00 NZD';
      this.dom.totals.descuentos.textContent = '0.00 NZD';
      this.dom.totals.faltante.textContent  = '0.00 NZD';

      this.init();
    } catch (e) {
      // Muestra mensaje de error DENTRO DEL MODAL
      modalMessage.innerHTML = `<div class="alert alert-danger" role="alert">${e.message}</div>`;
    } finally {
      this.dom.overlay.style.display = 'none';
    }
  }
}

// Inicialización
document.addEventListener('DOMContentLoaded', () => {
  const dom = {
    productos:   document.getElementById('productos-container'),
    pagos:       document.getElementById('pagos-container'),
    descuentos:  document.getElementById('descuentos-container'),
    totals: {
      venta:    document.getElementById('total-venta'),
      pago:     document.getElementById('total-pago'),
      descuentos: document.getElementById('total-descuentos'),
      faltante: document.getElementById('total-faltante')
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
