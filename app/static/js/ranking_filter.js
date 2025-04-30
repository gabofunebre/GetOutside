// app/static/js/ranking_filter.js
document.addEventListener("DOMContentLoaded", () => {
    const form      = document.getElementById("rankFilterForm");
    const btnLast30 = document.getElementById("btn-last30");
    const btnAll    = document.getElementById("btn-all");
  
    btnLast30.addEventListener("click", () => {
      const today = new Date();
      const prior = new Date();
      prior.setMonth(today.getMonth() - 1);
      document.getElementById("start").value = prior.toISOString().slice(0,10);
      document.getElementById("end").value   = today.toISOString().slice(0,10);
      form.submit();
    });
  
    btnAll.addEventListener("click", () => {
      form.reset();
      form.submit();
    });
  });
  