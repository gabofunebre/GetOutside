// static/js/compra_detalle.js
document.addEventListener('DOMContentLoaded', function () {
    const container = document.getElementById('detalle-compra');
    const compraId = container.dataset.compraId;

    fetch(`/compras/${compraId}`)
        .then(res => res.json())
        .then(data => {
            document.getElementById('fecha').textContent = new Date(data.fecha).toLocaleDateString();
            document.getElementById('concepto').textContent = data.concepto;
            document.getElementById('monto').textContent = data.monto.toFixed(2);
            document.getElementById('metodo-pago').textContent = `${data.payment_method.name} (${data.payment_method.currency})`;

            if (data.archivo) {
                document.getElementById('archivo').innerHTML =
                    `<a href="/static/uploads/${data.archivo.filename}" target="_blank">${data.archivo.filename}</a>`;
            } else {
                document.getElementById('archivo').innerHTML = "<em>(ninguno)</em>";
            }
        })
        .catch(err => {
            document.getElementById('detalle-compra').innerHTML =
                "<div class='alert alert-danger'>Error al cargar la compra.</div>";
            console.error(err);
        });
});
