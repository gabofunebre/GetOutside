////////////////////////////////////////////////////////////////////////////////
// TotalsCalculator con helper recalcFromDom
////////////////////////////////////////////////////////////////////////////////

export class TotalsCalculator {
  static conversionCache = {};

  static async recalcAll(
    prodContainer,
    pagoContainer,
    cambioContainer,
    descContainer,
    elVenta,
    elPago,
    elDesc,
    elFaltan,
    elTotal = null,
    elSobrante = null,
    elProductos = null
  ) {
    // === 1. Calcular subtotal de productos ===
    let venta = 0;
    prodContainer.querySelectorAll('.producto-block').forEach(b => {
      const qty = +b.querySelector("[name='cantidad']").value || 0;
      const price = +b.querySelector("[name='precio_unitario']").value || 0;
      const sub = qty * price;
      b.querySelector('.subtotal').textContent = sub.toFixed(2);
      venta += sub;
    });
    elVenta.textContent = `${venta.toFixed(2)} NZD`;
    if (elProductos) elProductos.textContent = venta.toFixed(2);

    // === 2. Calcular total de descuentos ===
    let descuentos = 0;
    descContainer.querySelectorAll('.descuento-block').forEach(b => {
      descuentos += +b.querySelector("[name='amount']").value || 0;
    });
    elDesc.textContent = `- ${descuentos.toFixed(2)} NZD`;

    // === 3. Calcular total pagado convertido a NZD ===
    let pagadoNZD = 0; // suma de montos de pago sin considerar vueltos
    let netoPagadoNZD = 0; // pagos menos vueltos, util para otras operaciones
    const pagos = pagoContainer.querySelectorAll('.pago-block');
    const cambios = cambioContainer.querySelectorAll('.vuelto-block');

    for (const b of pagos) {
      const amount = +b.querySelector("[name='amount']").value || 0;
      const select = b.querySelector("[name='payment_method_id']");
      const medio = select.options[select.selectedIndex];
      const currency = medio.dataset.currency;

      if (currency === "NZD") {
        pagadoNZD += amount;
        netoPagadoNZD += amount;
      } else {
        const key = `${currency}->NZD:${amount}`;
        if (!this.conversionCache[key]) {
          const url = `https://api.frankfurter.app/latest?from=${currency}&to=NZD&amount=${amount}`;
          try {
            const resp = await fetch(url);
            const data = await resp.json();
            this.conversionCache[key] = data.rates["NZD"];
          } catch {
            this.conversionCache[key] = 0;
          }
        }
        pagadoNZD += this.conversionCache[key];
        netoPagadoNZD += this.conversionCache[key];
      }
    }
    // === 3b. Restar vueltos ===
    for (const b of cambios) {
      const amount = +b.querySelector("[name='amount']").value || 0;
      const select = b.querySelector("[name='payment_method_id']");
      const medio = select.options[select.selectedIndex];
      const currency = medio.dataset.currency;

      if (currency === "NZD") {
        netoPagadoNZD -= amount;
      } else {
        const key = `${currency}->NZD:${amount}`;
        if (!this.conversionCache[key]) {
          const url = `https://api.frankfurter.app/latest?from=${currency}&to=NZD&amount=${amount}`;
          try {
            const resp = await fetch(url);
            const data = await resp.json();
            this.conversionCache[key] = data.rates["NZD"];
          } catch {
            this.conversionCache[key] = 0;
          }
        }
        netoPagadoNZD -= this.conversionCache[key];
      }
    }

    elPago.textContent = `${pagadoNZD.toFixed(2)} NZD`;

    // === 4. Calcular total final y faltante/sobrante ===
    const totalFinal = venta - descuentos;
    if (elTotal) elTotal.textContent = `${totalFinal.toFixed(2)} NZD`;

    const faltan = Math.max(0, totalFinal - pagadoNZD);
    elFaltan.textContent = `${faltan.toFixed(2)} NZD`;
    const sobrante = Math.max(0, netoPagadoNZD - totalFinal);
    if (elSobrante) elSobrante.textContent = `${sobrante.toFixed(2)} NZD`;
  }

  /** Método auxiliar para evitar duplicar llamadas a recalcAll */
  static recalcFromDom(dom) {
    return this.recalcAll(
      dom.productos,
      dom.pagos,
      dom.vueltos,
      dom.descuentos,
      dom.totals.venta,
      dom.totals.pago,
      dom.totals.descuentos,
      dom.totals.faltante,
      dom.totals.total,
      dom.totals.sobrante,
      dom.totals.productos
    );
  }
}
