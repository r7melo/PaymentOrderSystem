# Frontend (`frontend`)

Aplicação web responsável pela interface do PaymentOrderSystem: renderiza as páginas de login, cadastro e dashboard, e delega toda a lógica de negócio ao `api-gateway`, chamado diretamente pelo navegador do usuário.

## Arquitetura e Comunicação

* **Padrão de Comunicação:** Servidor HTTP (`FastAPI` + `Jinja2`) que apenas renderiza templates; nenhuma chamada ao backend é feita pelo servidor — todas as requisições de dados partem do JavaScript no navegador, via `fetch`, direto ao `api-gateway`.
* **Sem Persistência Própria:** Não possui banco de dados; estado de sessão (JWT) é mantido no `localStorage` do navegador.
* **Exposição de Configuração:** A URL pública do `api-gateway` (`PUBLIC_API_URL`) é injetada no HTML via `window.APP_CONFIG`, pois o navegador não resolve nomes internos da rede Docker (ex.: `api-gateway:8000`).

## Rotas HTTP

| Rota | Método | Retorno | Observação |
| :--- | :--- | :--- | :--- |
| `/health` | GET | `200` (`{"status": "ok"}`) | Healthcheck do container |
| `/` | GET | `200` (HTML) | Redireciona visualmente para a tela de login |
| `/login` | GET | `200` (HTML) | Tela de login |
| `/register` | GET | `200` (HTML) | Tela de cadastro |
| `/dashboard` | GET | `200` (HTML) | Menu principal (saldo, vínculos, ordens) |

## Scripts do Cliente (`app/static/js`)

* **`api.js`:** cliente HTTP centralizado — injeta `Authorization: Bearer <token>` em toda chamada, trata `401` limpando o token e redirecionando para `/login`.
* **`auth.js`:** lógica dos formulários de login e cadastro, consumindo `/auth/login` e `/auth/register` do `api-gateway`.
* **`dashboard.js`:** carrega saldo (`/contas/saldo`), vínculos (`/vinculos`) e ordens (`/ordens`); trata os formulários de convite de vínculo e criação de ordem.

## Variáveis de Ambiente

* `PUBLIC_API_URL` (padrão `http://localhost:8000`): URL do `api-gateway` visível pelo navegador.
* `API_GATEWAY_URL` (padrão `http://api-gateway:8000`): reservada para uso interno via rede Docker, não utilizada no fluxo atual (todas as chamadas partem do navegador).
* `SECRET_KEY`: placeholder para uso futuro (sessão/cookies), não utilizada na autenticação atual (JWT é opaco ao frontend).