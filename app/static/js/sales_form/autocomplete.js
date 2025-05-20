// File: app/static/js/sales_form/autocomplete.js
////////////////////////////////////////////////////////////////////////////////
// Autocomplete (sin dependencias)
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
    this.input.addEventListener('blur', () => setTimeout(() => this.hide(), 150));
    this.list.addEventListener('click', e => this.onClick(e));
    this.input.addEventListener('keydown', e => this.onKeyDown(e));
  }
  render() {
    const filter = this.input.value.trim().toLowerCase();
    this.list.innerHTML = '';
    this.matches = this.items.filter(p =>
      p.codigo_getoutside.toLowerCase().includes(filter) ||
      p.descripcion.toLowerCase().includes(filter)
    );
    this.matches.forEach(p => {
      const li = document.createElement('li');
      li.textContent = `${p.codigo_getoutside} — ${p.descripcion}`;
      li.dataset.codigo = p.codigo_getoutside;
      li.dataset.precio = p.precio_venta;
      this.list.appendChild(li);
    });
    this.list.style.display = this.matches.length ? 'block' : 'none';
  }
  hide() { this.list.style.display = 'none'; }
  onClick(e) { if (e.target.tagName === 'LI') this.select(e.target); }
  onKeyDown(e) {
    const items = this.list.querySelectorAll('li'); if (!items.length) return;
    if (e.key === 'ArrowDown') { this.index = (this.index + 1) % items.length; this.updateActive(items); e.preventDefault(); }
    else if (e.key === 'ArrowUp') { this.index = (this.index - 1 + items.length) % items.length; this.updateActive(items); e.preventDefault(); }
    else if (e.key === 'Enter' && this.index >= 0) { this.select(items[this.index]); e.preventDefault(); }
  }
  updateActive(items) { items.forEach(li => li.classList.remove('active')); items[this.index].classList.add('active'); }
  select(li) {
    this.input.value = li.dataset.codigo;
    this.onSelect(li.dataset);
    this.hide();
  }
}