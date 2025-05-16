document.addEventListener("DOMContentLoaded", () => {
  const btnLast30 = document.getElementById("btn-last30");
  const btnLast7  = document.getElementById("btn-last7");
  const btnAll    = document.getElementById("btn-all");

  if (btnLast30) {
    btnLast30.addEventListener("click", () => {
      const today = new Date();
      const prior = new Date();
      prior.setDate(today.getDate() - 30);
      const start = prior.toISOString().slice(0, 10);
      const end   = today.toISOString().slice(0, 10);
      location.href = `/ventas/list?start=${start}&end=${end}`;
    });
  }

  if (btnLast7) {
    btnLast7.addEventListener("click", () => {
      const today = new Date();
      const prior = new Date();
      prior.setDate(today.getDate() - 7);
      const start = prior.toISOString().slice(0, 10);
      const end   = today.toISOString().slice(0, 10);
      location.href = `/ventas/list?start=${start}&end=${end}`;
    });
  }

  if (btnAll) {
    btnAll.addEventListener("click", () => {
      location.href = `/ventas/list`;
    });
  }
});
