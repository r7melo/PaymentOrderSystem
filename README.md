# Sistema de Ordens de Pagamento e Confirmação Assíncrona

Este projeto implementa uma arquitetura baseada em microsserviços orientada a eventos para um fluxo de ordens de pagamento, confirmação e atualização de saldos em contas. A solução utiliza **FastAPI** para as APIs, **RabbitMQ** para mensageria assíncrona, **Docker / Docker Compose** para orquestração, **Nginx** para servir o frontend estático, e **Dozzle** para monitoramento dos logs dos microsserviços.

---

## 📐 Arquitetura do Sistema

A solução é composta pelos seguintes microsserviços e componentes:

1. **Frontend (`frontend`)**:
   - Interface Web em HTML/JS servida por Nginx na porta `8080`.
   - Oferece abas para a **Tela PAGADOR** e **Tela RECEBEDOR**.
2. **Serviço de Ordens de Pagamento (`orders_service`)**:
   - Porta `8001`.
   - Responsável por criar as ordens de pagamento (`CreateOrdem`) e listá-las (`GetOrdens`).
   - Contém a classe `TRA` vazia pronta para receber regras de validação da ordem.
   - Publica o evento `ORDEM_CRIADA` na fila `payment_orders` do RabbitMQ.
3. **Serviço de Confirmação de Ordens (`confirmation_service`)**:
   - Porta `8002`.
   - Consome a fila `payment_orders` para manter a lista de ordens pendentes (`ListOrdens`).
   - Contém a classe `TRA` vazia pronta para receber regras de validação se a ordem pode ser confirmada ou não.
   - Ao confirmar (`ConfirmeOrdem`), publica o evento `ORDEM_CONFIRMADA` na fila `confirmed_orders` do RabbitMQ.
4. **Serviço de Gestão de Contas (`accounts_service`)**:
   - Porta `8003`.
   - Mantém os saldos dos usuários (`PAGADOR_1`, `RECEBEDOR_1`).
   - Escuta a fila `confirmed_orders` do RabbitMQ para debitar do pagador e creditar no recebedor assim que a confirmação ocorre.
   - Fornece consulta de saldo para ambas as telas do Frontend.
5. **RabbitMQ (`rabbitmq`)**:
   - Broker de mensagens (AMQP na porta `5672`, Management UI na porta `15672`).
6. **Dozzle (`dozzle`)**:
   - Interface para visualização de logs dos containers Docker em tempo real na porta `8888`.

---

## 🛠️ Tecnologias Utilizadas

- **Python 3.10** + **FastAPI** + **Uvicorn**
- **Pika** (Cliente RabbitMQ para Python)
- **RabbitMQ** (Message Broker)
- **HTML5 / JavaScript (ES6)** + **Nginx**
- **Docker** & **Docker Compose**
- **Dozzle** (Visualizador de logs)

---

## 📂 Estrutura de Pastas

```text
SistemaOrdens/
├── README.md
├── docker-compose.yml
├── frontend/
│   ├── Dockerfile
│   ├── nginx.conf
│   └── index.html
├── orders_service/
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
├── confirmation_service/
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
└── accounts_service/
    ├── Dockerfile
    ├── main.py
    └── requirements.txt
```

---

## 🚀 Como Executar o Projeto

### Pré-requisitos

- **Docker** e **Docker Compose** instalados em sua máquina.

### Passo a Passo

1. **Clone ou navegue até o diretório do projeto**:
   ```bash
   cd SistemaOrdens
   ```

2. **Inicie os serviços utilizando o Docker Compose**:
   ```bash
   docker-compose up --build -d
   ```

3. **Aguarde a inicialização**:
   O RabbitMQ passará pela verificação de saúde (`healthcheck`) e em seguida todos os serviços de backend e frontend estarão ativos.

---

## 🌐 URLs de Acesso

- **Frontend (Painel de Operações)**: [http://localhost:8080](http://localhost:8080)
- **Dozzle (Logs dos Containers)**: [http://localhost:8888](http://localhost:8888)
- **Painel de Gestão do RabbitMQ**: [http://localhost:15672](http://localhost:15672) *(Login: `guest` / Senha: `guest`)*
- **Swagger Docs - Serviço de Ordens**: [http://localhost:8001/docs](http://localhost:8001/docs)
- **Swagger Docs - Serviço de Confirmação**: [http://localhost:8002/docs](http://localhost:8002/docs)
- **Swagger Docs - Serviço de Contas**: [http://localhost:8003/docs](http://localhost:8003/docs)

---

## 🧪 Roteiro de Teste do Fluxo Completo

1. Abra o navegador em [http://localhost:8080](http://localhost:8080) e abra o Dozzle em [http://localhost:8888](http://localhost:8888).
2. Na aba **Tela PAGADOR**:
   - Verifique o saldo inicial de `PAGADOR_1` (R$ 1000.00).
   - Insira o recebedor `RECEBEDOR_1` e o valor (ex: `50.00`).
   - Clique em **CreateOrdem**.
3. Acompanhe os logs no Dozzle:
   - Veja o log do `orders_service` publicando a ordem no RabbitMQ.
   - Veja o log do `confirmation_service` consumindo e armazenando a ordem.
4. Mude para a aba **Tela RECEBEDOR**:
   - Verifique o saldo inicial de `RECEBEDOR_1` (R$ 100.00).
   - Clique no botão **ListOrdens**. A ordem recém-criada estará visível.
   - Clique no botão **ConfirmeOrdem**.
5. Finalização do Fluxo:
   - A confirmação aciona o envio de um evento para a fila `confirmed_orders`.
   - O `accounts_service` consome essa mensagem e efetua a transferência de saldos (`PAGADOR_1`: 950.00 / `RECEBEDOR_1`: 150.00).
   - Clique no botão **Atualizar Saldo** nas telas do Pagador e do Recebedor para verificar a atualização dos valores na tela.

---

## 🧩 Inserindo Regras de Negócio na Classe `TRA`

As classes `TRA` estão preparadas para receber suas regras customizadas:

1. **`orders_service/main.py`**:
   ```python
   class TRA:
       @staticmethod
       def validar_ordem(pagador: str, recebedor: str, valor: float) -> bool:
           # Implemente aqui suas regras para aceitar/rejeitar a criação da ordem
           return True
   ```

2. **`confirmation_service/main.py`**:
   ```python
   class TRA:
       @staticmethod
       def validar_confirmacao(order_data: dict) -> bool:
           # Implemente aqui suas regras para autorizar/rejeitar a confirmação do usuário
           return True
   ```