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

    const formSenha = document.querySelector("form");
    formSenha.addEventListener("submit", function (e) {
      const senha = document.getElementById("senha").value;
      const confirmar = document.getElementById("confirmar_senha").value;

      const senhaForte = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{8,}$/;

      if (senha !== confirmar) {
        e.preventDefault();
        alert("As senhas não coincidem.");
        return;
      }

      if (!senhaForte.test(senha)) {
        e.preventDefault();
        alert("A senha deve ter no mínimo 8 caracteres, com letras maiúsculas, minúsculas, números e símbolos.");
      }
    });

});

function login(event) {
  event.preventDefault();

  const usuario = document.getElementById("usuario").value;
  const senha = document.getElementById("senha").value;
  const tipo = document.getElementById("tipoUsuario").value;

 
  if (usuario && senha) {
    if (tipo === "funcionario") {
      window.location.href = "menu_funcionario.html";
    } else {
      window.location.href = "menu_cliente.html";
    }
  } else {
    alert("Usuário ou senha inválidos");
  }
}
