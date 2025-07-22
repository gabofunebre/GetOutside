document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('loginForm');
  if (!form) return;
  const emailInput = form.querySelector('[name="email"]');
  const passwordInput = form.querySelector('[name="password"]');

  const validateEmail = (email) => {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  };

  const clearError = (input) => {
    input.classList.remove('is-invalid');
  };

  emailInput.addEventListener('input', () => clearError(emailInput));
  passwordInput.addEventListener('input', () => clearError(passwordInput));

  form.addEventListener('submit', (e) => {
    let valid = true;

    if (!emailInput.value.trim()) {
      emailInput.nextElementSibling.textContent = 'Ingrese su email';
      emailInput.classList.add('is-invalid');
      valid = false;
    } else if (!validateEmail(emailInput.value.trim())) {
      emailInput.nextElementSibling.textContent = 'Ingrese un email válido';
      emailInput.classList.add('is-invalid');
      valid = false;
    }

    if (!passwordInput.value.trim()) {
      passwordInput.nextElementSibling.textContent = 'Ingrese su contraseña';
      passwordInput.classList.add('is-invalid');
      valid = false;
    }

    if (!valid) {
      e.preventDefault();
    }
  });

});
