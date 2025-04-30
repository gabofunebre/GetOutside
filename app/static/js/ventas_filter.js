// app/static/js/ventas_filter.js
document.addEventListener("DOMContentLoaded", () => {
    const form      = document.getElementById("filterForm");
    const btnLast30 = document.getElementById("btn-last30");
    const btnAll    = document.getElementById("btn-all");
  
    btnLast30.addEventListener("click", () => {
      const today = new Date();
      const prior = new Date();
      prior.setDate(today.getDate() - 30);
      document.getElementById("start").value = prior.toISOString().slice(0,10);
      document.getElementById("end").value   = today.toISOString().slice(0,10);
      form.submit();
    });
  
    btnAll.addEventListener("click", () => {
      form.reset();
      form.submit();
    });
  });
  