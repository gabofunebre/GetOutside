// Overlay helper
function showOverlay() {
    document.getElementById('overlay').style.display = 'flex';
}
function hideOverlay() {
    document.getElementById('overlay').style.display = 'none';
}

// Setear fecha de hoy por defecto en el input fecha
document.addEventListener('DOMContentLoaded', function () {
    const fechaInput = document.getElementById('fecha');
    if (fechaInput && !fechaInput.value) {
        const hoy = new Date().toISOString().split('T')[0];
        fechaInput.value = hoy;
    }
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
    const archivo = document.getElementById('archivo').files[0];

    let resumen = `<b>Fecha:</b> ${fecha}<br>`;
    resumen += archivo ? `<b>Archivo:</b> ${archivo.name}<br>` : `<b>Archivo:</b> <i>(ninguno)</i><br>`;
    resumen += `<b>Concepto:</b> ${concepto}`;

    document.getElementById('modalConfirmBody').innerHTML = resumen;

    formDataCache = { concepto, fecha, archivo };
    modalConfirm.show();
});

// Confirmación real
document.getElementById('btn-confirmar').addEventListener('click', function () {
    modalConfirm.hide();
    showOverlay();

    const data = new FormData();
    data.append('concepto', formDataCache.concepto);
    data.append('fecha', formDataCache.fecha);
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
