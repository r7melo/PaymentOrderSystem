async function loadSaldo() {
  const el = document.getElementById("saldo-valor");
  if (!el) return;

  try {
    const data = await api.get("/contas/saldo");
    el.textContent = formatCurrency(data.saldo);
  } catch (error) {
    showToast(error.message);
  }
}

async function loadVinculos() {
  const list = document.getElementById("vinculos-list");
  let vinculos = [];

  try {
    vinculos = await api.get("/vinculos");
  } catch (error) {
    vinculos = [];
  }

  if (list) {
    list.innerHTML = "";
    if (vinculos.length === 0) {
      list.innerHTML = '<li class="empty-state">Nenhum vínculo ainda</li>';
    } else {
      vinculos.forEach((v) => {
        const li = document.createElement("li");
        li.className = "vinculo-item";
        li.innerHTML = `
          <span>${v.email}</span>
          <span class="badge badge-${v.status}">${v.status}</span>
        `;
        list.appendChild(li);
      });
    }
  }

  popularDestinosOrdem(vinculos);
}

function popularDestinosOrdem(vinculos) {
  const container = document.getElementById("ordem-destinos-container");
  if (!container) return;

  const aceitos = vinculos.filter((v) => v.status === "aceito");
  container.innerHTML = "";

  if (aceitos.length === 0) {
    container.innerHTML =
      '<p class="empty-state">Nenhum vínculo aceito ainda</p>';
    return;
  }

  aceitos.forEach((v) => {
    const label = document.createElement("label");
    label.className = "destino-checkbox";
    label.innerHTML = `
      <input type="checkbox" name="ordem-destinos" value="${v.id}" />
      <span>${v.email}</span>
    `;
    container.appendChild(label);
  });
}

async function loadOrdens() {
  const list = document.getElementById("ordens-list");
  if (!list) return;

  try {
    const ordens = await api.get("/ordens");
    list.innerHTML = "";

    if (ordens.length === 0) {
      list.innerHTML = '<li class="empty-state">Nenhuma ordem ainda</li>';
      return;
    }

    ordens.forEach((o) => {
      const li = document.createElement("li");
      li.className = "ordem-item";
      li.innerHTML = `
        <span>Ordem #${o.id}</span>
        <span>${formatCurrency(o.valor_total)}</span>
        <span class="badge badge-${o.status}">${o.status}</span>
      `;
      list.appendChild(li);
    });
  } catch (error) {
    showToast(error.message);
  }
}

function handleVinculoForm() {
  const form = document.getElementById("vinculo-form");
  if (!form) return;

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const email = document.getElementById("vinculo-email").value.trim();

    try {
      await api.post("/vinculos", { email });
      showToast("Solicitação de vínculo enviada", "success");
      form.reset();
      loadVinculos();
    } catch (error) {
      showToast(error.message);
    }
  });
}

function handleOrdemForm() {
  const form = document.getElementById("ordem-form");
  if (!form) return;

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const valor = parseFloat(document.getElementById("ordem-valor").value);
    const checkboxes = document.querySelectorAll(
      'input[name="ordem-destinos"]:checked'
    );
    const destinos = Array.from(checkboxes).map((c) => c.value);

    if (destinos.length === 0) {
      showToast("Selecione ao menos um vínculo destino");
      return;
    }

    try {
      await api.post("/ordens", { valor_por_destino: valor, destinos });
      showToast("Ordem criada", "success");
      form.reset();
      loadOrdens();
      loadSaldo();
    } catch (error) {
      showToast(error.message);
    }
  });
}

function handleLogout() {
  const btn = document.getElementById("logout-btn");
  if (!btn) return;

  btn.addEventListener("click", () => {
    disconnectNotificationsSocket();
    clearToken();
    window.location.href = "/login";
  });
}

function formatCurrency(value) {
  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
  }).format(value);
}

document.addEventListener("DOMContentLoaded", () => {
  if (!isAuthenticated()) {
    window.location.href = "/login";
    return;
  }

  loadSaldo();
  loadVinculos();
  loadOrdens();
  handleVinculoForm();
  handleOrdemForm();
  handleLogout();
  loadNotificacoesHistorico();
  connectNotificationsSocket();
});