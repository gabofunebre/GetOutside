// app/static/js/main.js

// Importación de módulos de comportamiento
import { initModalHandler } from './modal_handler.js'; // Manejo del modal de producto existente
import { setupFormBehavior } from './field_manager.js'; // Gestión dinámica de campos y validaciones
import { attachCodigoListener } from './producto_api.js'; // Validación del código de producto contra la API

// Espera a que todo el DOM esté cargado
document.addEventListener("DOMContentLoaded", () => {
  // Contexto con referencias a elementos del DOM y estado interno
  const ctx = {
    // Formulario principal y elementos de interfaz
    form: document.getElementById("productForm"),
    alertPlaceholder: document.getElementById("alert-placeholder"),
    overlay: document.getElementById("overlay"),

    // Campos de producto
    codigoInput: document.getElementById("codigo_getoutside"), // Campo único que permanece
    descripcionInput: document.getElementById("descripcion"),
    catalogoSelect: document.getElementById("catalogo_id"),
    precioInput: document.getElementById("precio_venta"),

    // Campos relacionados con stock
    stockInput: document.getElementById("stock_actual"),
    stockInfo: document.getElementById("existing-stock-info"),
    stockLabel: document.getElementById("stock_actual_label"),
    stockAgregadoInput: document.getElementById("stock_agregado"),

    // Botón de envío del formulario
    submitButton: document.getElementById("submit-button"),

    // Modal para confirmar si el producto ya existe
    modal: new bootstrap.Modal(document.getElementById("productoExistenteModal")),
    aceptarBtn: document.getElementById("aceptarProductoExistente"),
    cancelarBtn: document.getElementById("cancelarProductoExistente"),

    // Estado interno\    productoExistente: false,
    productoId: null,
    productoTemporal: null
  };

  // Inicializa el manejo del modal\  initModalHandler(ctx);
  // Adjunta escucha para validar el código de producto con la API\  attachCodigoListener(ctx);
  // Configura comportamiento dinámico del formulario (habilitar/deshabilitar campos)\  setupFormBehavior(ctx);
});
