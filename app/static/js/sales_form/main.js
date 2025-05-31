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
    let hasError = false;

    // === Validación de productos ===
    this.productBlocks.forEach(b => {
      const codigoInput = b.el.querySelector("[name='codigo_getoutside']");
      const idInput = b.el.querySelector("[name='producto_id']");
      const qty = b.el.querySelector("[name='cantidad']");
      const price = b.el.querySelector("[name='precio_unitario']");

      if (!idInput.value) {
        codigoInput.classList.add("is-invalid");
        hasError = true;
      } else {
        codigoInput.classList.remove("is-invalid");
      }

      if (!qty.value || qty.value <= 0) {
        qty.classList.add("is-invalid");
        hasError = true;
      } else {
        qty.classList.remove("is-invalid");
      }

      if (!price.value || price.value <= 0) {
        price.classList.add("is-invalid");
        hasError = true;
      } else {
        price.classList.remove("is-invalid");
      }
    });

    // === Validación de pagos ===
    this.paymentBlocks.forEach(b => {
      const medio = b.el.querySelector("[name='payment_method_id']");
      const monto = b.el.querySelector("[name='amount']");

      if (!medio.value) {
        medio.classList.add("is-invalid");
        hasError = true;
      } else {
        medio.classList.remove("is-invalid");
      }

      if (!monto.value || monto.value <= 0) {
        monto.classList.add("is-invalid");
        hasError = true;
      } else {
        monto.classList.remove("is-invalid");
      }
    });

    // === Validación de descuentos ===
    this.discountBlocks.forEach(b => {
      const concepto = b.el.querySelector("[name='concepto']");
      const monto = b.el.querySelector("[name='amount']");

      if (concepto.value.trim() === "" && monto.value) {
        concepto.classList.add("is-invalid");
        hasError = true;
      } else {
        concepto.classList.remove("is-invalid");
      }

      if (monto.value < 0) {
        monto.classList.add("is-invalid");
        hasError = true;
      } else {
        monto.classList.remove("is-invalid");
      }
    });

    if (hasError) {
      return; // no abrir modal si hay errores
    }

    // === Si todo está OK, recalcula y abre el modal ===
    await TotalsCalculator.recalcAll(
      this.dom.productos,
      this.dom.pagos,
      this.dom.descuentos,
      this.dom.totals.venta,
      this.dom.totals.pago,
      this.dom.totals.descuentos,
      this.dom.totals.faltante
    );

    // El resto del código para armar el resumen sigue igual...
    // (no es necesario modificarlo)
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
