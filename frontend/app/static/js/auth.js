function showToast(message, type = "error") {
  const container = document.getElementById("toast-container");
  if (!container) return;

  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  container.appendChild(toast);

  setTimeout(() => toast.remove(), 4000);
}

function handleLoginForm() {
  const form = document.getElementById("login-form");
  if (!form) return;

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;

    try {
      const data = await api.post("/auth/login", { email, password });
      setToken(data.access_token);
      window.location.href = "/dashboard";
    } catch (error) {
      showToast(error.message);
    }
  });
}

function handleRegisterForm() {
  const form = document.getElementById("register-form");
  if (!form) return;

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const name = document.getElementById("name").value.trim();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;
    const confirmPassword = document.getElementById("confirm-password").value;

    if (password !== confirmPassword) {
      showToast("As senhas não coincidem");
      return;
    }

    try {
      await api.post("/auth/register", { name, email, password });
      showToast("Cadastro realizado! Faça login.", "success");
      window.location.href = "/login";
    } catch (error) {
      showToast(error.message);
    }
  });
}

document.addEventListener("DOMContentLoaded", () => {
  handleLoginForm();
  handleRegisterForm();
});