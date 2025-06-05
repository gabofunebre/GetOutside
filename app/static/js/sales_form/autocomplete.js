// File: app/static/js/sales_form/autocomplete.js
////////////////////////////////////////////////////////////////////////////////
// Autocomplete (actualizado para pasar objeto completo del producto)
////////////////////////////////////////////////////////////////////////////////
export class Autocomplete {
  constructor(input, list, items, onSelect) {
    this.input = input;
    this.list = list;
    this.items = items;
    this.onSelect = onSelect;
    this.index = -1;
    this.bind();
  }

  bind() {
    this.input.addEventListener('input', () => this.render());
    this.input.addEventListener('focus', () => this.render());
    this.list.addEventListener('mousedown', e => {
      e.preventDefault();
      this.onClick(e);
    });
    this.list.addEventListener('click', e => this.onClick(e));
    this.input.addEventListener('keydown', e => this.onKeyDown(e));
  }

  render() {
    const filter = this.input.value.trim().toLowerCase();
    this.list.innerHTML = '';
    // Filtrar solo productos con stock_actual > 0
    this.matches = this.items
      .filter(p => p.stock_actual > 0)
      .filter(p =>
        p.codigo_getoutside.toLowerCase().includes(filter) ||
        p.descripcion.toLowerCase().includes(filter)
      );
    this.matches.forEach((p, index) => {
      const li = document.createElement('li');
      li.textContent = `${p.codigo_getoutside} — ${p.descripcion}`;
      li.dataset.index = index; // Usamos índice para referencia interna
      this.list.appendChild(li);
    });
    this.list.style.display = this.matches.length ? 'block' : 'none';
  }

  hide() {
    this.list.style.display = 'none';
  }

  onClick(e) {
    if (e.target.tagName === 'LI') this.select(e.target);
  }

  onKeyDown(e) {
    const items = this.list.querySelectorAll('li');
    if (!items.length) return;
    if (e.key === 'ArrowDown') {
      this.index = (this.index + 1) % items.length;
      this.updateActive(items);
      e.preventDefault();
    } else if (e.key === 'ArrowUp') {
      this.index = (this.index - 1 + items.length) % items.length;
      this.updateActive(items);
      e.preventDefault();
    } else if (e.key === 'Enter' && this.index >= 0) {
      this.select(items[this.index]);
      e.preventDefault();
    }
  }

  updateActive(items) {
    items.forEach(li => li.classList.remove('active'));
    items[this.index].classList.add('active');
  }

  select(li) {
    const index = +li.dataset.index;
    const selectedItem = this.matches[index];
    this.input.value = selectedItem.codigo_getoutside;
    this.onSelect(selectedItem); // Pasamos el objeto completo
    this.hide();
  }
}
