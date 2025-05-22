// app/static/js/product_form/form_utils.js

/**
 * Restaura el formulario a su estado base:
 * - Oculta secciones
 * - Limpia valores
 * - Desactiva todos los inputs
 * - Quita atributos required
 */
export function resetFormularioVisual(ctx) {
  const {
    estadoMsg, submitButton,
    nuevoForm, existenteForm,
    descripcionInput, catalogoSelect, precioInput, stockInput,
    stockAgregadoInput,
    descripcionLabel, catalogoLabel, precioLabel, stockLabel
  } = ctx;

  estadoMsg.textContent = "";
  submitButton.disabled = true;
  submitButton.textContent = "Guardar";

  nuevoForm.classList.add("d-none");
  existenteForm.classList.add("d-none");

  descripcionInput.value = "";
  descripcionInput.disabled = true;
  descripcionInput.removeAttribute("required");

  catalogoSelect.selectedIndex = 0;
  catalogoSelect.disabled = true;
  catalogoSelect.removeAttribute("required");

  precioInput.value = "";
  precioInput.disabled = true;
  precioInput.removeAttribute("required");

  stockInput.value = 0;
  stockInput.disabled = true;
  stockInput.removeAttribute("required");

  stockAgregadoInput.value = 0;
  stockAgregadoInput.disabled = true;
  stockAgregadoInput.removeAttribute("required");

  descripcionLabel.textContent = "";
  catalogoLabel.textContent = "";
  precioLabel.textContent = "";
  stockLabel.textContent = "0";
}
