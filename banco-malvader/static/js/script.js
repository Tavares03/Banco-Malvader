document.addEventListener("DOMContentLoaded", function () {
  const telefoneInput = document.getElementById("telefone");
  if (telefoneInput) {
    telefoneInput.addEventListener("input", function (e) {
      let x = e.target.value.replace(/\D/g, "").slice(0, 11);
      let formatted = x;

      if (x.length >= 2) {
        formatted = "(" + x.slice(0, 2) + ") " + x.slice(2);
      }
      if (x.length >= 7) {
        formatted = "(" + x.slice(0, 2) + ") " + x.slice(2, 7) + "-" + x.slice(7);
      }

      e.target.value = formatted;
    });
  }

});


