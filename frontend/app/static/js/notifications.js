let socket = null;
let reconnectTimeout = null;

function connectNotificationsSocket() {
  const token = getToken();
  if (!token) return;

  const wsBase = window.APP_CONFIG.API_BASE_URL.replace(/^http/, "ws");
  socket = new WebSocket(`${wsBase}/ws/notificacoes?token=${token}`);

  socket.onopen = () => {
    console.log("Conectado às notificações");
  };

  socket.onmessage = (event) => {
    const notificacao = JSON.parse(event.data);
    prependNotificacao(notificacao);
    showToast(notificacao.mensagem, "success");
  };

  socket.onclose = () => {
    reconnectTimeout = setTimeout(connectNotificationsSocket, 3000);
  };

  socket.onerror = () => {
    socket.close();
  };
}

function disconnectNotificationsSocket() {
  if (reconnectTimeout) clearTimeout(reconnectTimeout);
  if (socket) socket.close();
}

async function loadNotificacoesHistorico() {
  const list = document.getElementById("notificacoes-list");
  if (!list) return;

  try {
    const notificacoes = await api.get("/notificacoes");
    list.innerHTML = "";

    if (notificacoes.length === 0) {
      list.innerHTML = '<li class="empty-state">Nenhuma notificação</li>';
      return;
    }

    notificacoes.forEach((n) => appendNotificacao(n));
  } catch (error) {
    showToast(error.message);
  }
}

function prependNotificacao(n) {
  const list = document.getElementById("notificacoes-list");
  if (!list) return;

  const empty = list.querySelector(".empty-state");
  if (empty) empty.remove();

  const li = buildNotificacaoItem(n);
  list.prepend(li);
}

function appendNotificacao(n) {
  const list = document.getElementById("notificacoes-list");
  if (!list) return;

  const li = buildNotificacaoItem(n);
  list.appendChild(li);
}

function buildNotificacaoItem(n) {
  const li = document.createElement("li");
  li.className = "notificacao-item";
  li.innerHTML = `
    <span>${n.mensagem}</span>
    <span class="notificacao-data">${formatDataHora(n.criado_em)}</span>
  `;
  return li;
}

function formatDataHora(isoString) {
  return new Date(isoString).toLocaleString("pt-BR");
}