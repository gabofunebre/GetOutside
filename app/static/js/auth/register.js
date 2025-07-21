document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('registerForm');
  if (!form) return;
  const firstName = form.querySelector('[name="first_name"]');
  const lastName = form.querySelector('[name="last_name"]');
  const email = form.querySelector('[name="email"]');
  const password = form.querySelector('[name="password"]');
  const confirm = form.querySelector('[name="password_confirm"]');

  const validateEmail = (val) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val);

  const clear = (input) => input.classList.remove('is-invalid');
  [firstName, lastName, email, password, confirm].forEach(i => {
    i.addEventListener('input', () => clear(i));
  });

  form.addEventListener('submit', (e) => {
    let valid = true;

    if (!firstName.value.trim()) {
      firstName.nextElementSibling.textContent = 'Ingrese el nombre';
      firstName.classList.add('is-invalid');
      valid = false;
    }
    if (!lastName.value.trim()) {
      lastName.nextElementSibling.textContent = 'Ingrese el apellido';
      lastName.classList.add('is-invalid');
      valid = false;
    }

    if (!email.value.trim()) {
      email.nextElementSibling.textContent = 'Ingrese el email';
      email.classList.add('is-invalid');
      valid = false;
    } else if (!validateEmail(email.value.trim())) {
      email.nextElementSibling.textContent = 'Ingrese un email válido';
      email.classList.add('is-invalid');
      valid = false;
    }

    if (!password.value.trim()) {
      password.nextElementSibling.textContent = 'Ingrese una contraseña';
      password.classList.add('is-invalid');
      valid = false;
    }

    if (!confirm.value.trim()) {
      confirm.nextElementSibling.textContent = 'Repita la contraseña';
      confirm.classList.add('is-invalid');
      valid = false;
    } else if (confirm.value !== password.value) {
      confirm.nextElementSibling.textContent = 'Las contraseñas no coinciden';
      confirm.classList.add('is-invalid');
      valid = false;
    }

    if (!valid) e.preventDefault();
  });
});
