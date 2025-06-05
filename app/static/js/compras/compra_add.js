// Overlay helper
function showOverlay() {
    document.getElementById('overlay').style.display = 'flex';
}
function hideOverlay() {
    document.getElementById('overlay').style.display = 'none';
}

function formatFechaCompleta(date) {
    const pad = n => String(n).padStart(2, '0');
    return `${pad(date.getDate())}-${pad(date.getMonth() + 1)}-${date.getFullYear()} ` +
           `${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
}

// Setear fecha de hoy por defecto en el input fecha
document.addEventListener('DOMContentLoaded', function () {
    const fechaInput = document.getElementById('fecha');
    if (fechaInput && !fechaInput.value) {
        fetch('/api/server-datetime')
          .then(res => res.json())
          .then(data => {
            const serverDate = new Date(data.datetime);
            const localISO = new Date(serverDate.getTime() - serverDate.getTimezoneOffset() * 60000)
              .toISOString()
              .slice(0, 19);
            fechaInput.value = localISO;
          })
          .catch(() => {
            fechaInput.value = new Date().toISOString().slice(0, 19);
          });
    }

    // 1. Fetch currency labels
    let currencyLabels = {};
    fetch('/payment_methods/currencies_labels')
      .then(resp => resp.json())
      .then(labels => {
        currencyLabels = labels;
        // 2. Fetch payment methods y poblar select
        return fetch('/payment_methods/');
      })
      .then(resp => resp.json())
      .then(paymentMethods => {
        const select = document.getElementById('payment_method_id');
        paymentMethods.forEach(pm => {
          const emoji = currencyLabels[pm.currency] || pm.currency;
          const option = document.createElement('option');
          option.value = pm.id;
          option.text = `${emoji} ${pm.name} (${pm.currency})`;
          select.appendChild(option);
        });
      });
});

const form = document.getElementById('compra-form');
const btnRegistrar = document.getElementById('btn-registrar');
const modalConfirm = new bootstrap.Modal(document.getElementById('modalConfirm'));
const modalResultado = new bootstrap.Modal(document.getElementById('modalResultado'));
let formDataCache = null;

// Click en registrar: validación y mostrar resumen en modal
btnRegistrar.addEventListener('click', function () {
    if (!form.checkValidity()) {
        form.classList.add('was-validated');
        return;
    }
    const concepto = document.getElementById('concepto').value.trim();
    const fecha = document.getElementById('fecha').value;
    const fechaFormatted = formatFechaCompleta(new Date(fecha));
    const monto = document.getElementById('monto').value;
    const archivo = document.getElementById('archivo').files[0];
    const paymentMethodSelect = document.getElementById('payment_method_id');
    const payment_method_id = paymentMethodSelect.value;
    const payment_method_text = paymentMethodSelect.options[paymentMethodSelect.selectedIndex].text;

    let resumen = `<b>Fecha:</b> ${fechaFormatted}<br>`;
    resumen += `<b>Monto:</b> ${monto}<br>`;
    resumen += `<b>Método de pago:</b> ${payment_method_text}<br>`;
    resumen += archivo ? `<b>Archivo:</b> ${archivo.name}<br>` : `<b>Archivo:</b> <i>(ninguno)</i><br>`;
    resumen += `<b>Concepto:</b> ${concepto}`;

    document.getElementById('modalConfirmBody').innerHTML = resumen;

    formDataCache = { concepto, fecha, monto, archivo, payment_method_id };
    modalConfirm.show();
});

// Confirmación real
document.getElementById('btn-confirmar').addEventListener('click', function () {
    modalConfirm.hide();
    showOverlay();

    const data = new FormData();
    data.append('concepto', formDataCache.concepto);
    data.append('fecha', formDataCache.fecha);
    data.append('monto', formDataCache.monto);
    data.append('payment_method_id', formDataCache.payment_method_id);
    if (formDataCache.archivo) {
        data.append('archivo', formDataCache.archivo);
    }

    fetch('/compras/new', {
        method: 'POST',
        body: data
    })
    .then(async resp => {
        hideOverlay();
        if (resp.ok) {
            document.getElementById('modalResultadoBody').innerHTML =
              `<div class="alert alert-success">¡Compra registrada correctamente!</div>`;
            form.reset();
            form.classList.remove('was-validated');
        } else {
            let res;
            try {
                res = await resp.json();
            } catch {
                res = {};
            }
            document.getElementById('modalResultadoBody').innerHTML =
              `<div class="alert alert-danger">Error: ${res.detail || "Error al registrar compra."}</div>`;
        }
        modalResultado.show();
    })
    .catch(err => {
        hideOverlay();
        document.getElementById('modalResultadoBody').innerHTML =
          `<div class="alert alert-danger">Error de conexión o del servidor.</div>`;
        modalResultado.show();
    });
});
