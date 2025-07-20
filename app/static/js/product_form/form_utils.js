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
    descripcionInput, catalogoSelect, precioInput, costoInput, stockInput,
    fotoInput,
    stockAgregadoInput,
    descripcionLabel, catalogoLabel, precioLabel, costoLabel, stockLabel
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

  costoInput.value = "";
  costoInput.disabled = true;
  costoInput.removeAttribute("required");

  stockInput.value = 0;
  stockInput.disabled = true;
  stockInput.removeAttribute("required");

  stockAgregadoInput.value = 0;
  stockAgregadoInput.disabled = true;
  stockAgregadoInput.removeAttribute("required");

  if (fotoInput) {
    fotoInput.value = "";
    fotoInput.disabled = true;
  }

  descripcionLabel.textContent = "";
  catalogoLabel.textContent = "";
  precioLabel.textContent = "";
  costoLabel.textContent = "";
  stockLabel.textContent = "0";
}
