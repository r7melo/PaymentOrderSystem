# Sistema de Ordens de Pagamento e Confirmação Assíncrona

Este projeto implementa uma arquitetura baseada em microsserviços orientada a eventos para um fluxo de ordens de pagamento, confirmação e atualização de saldos em contas. A solução utiliza **FastAPI** para as APIs, **RabbitMQ** para mensageria assíncrona, **Docker / Docker Compose** e **Kubernetes (K3s/Minikube)** para orquestração, **Nginx** para servir o frontend estático, e **Dozzle** para monitoramento dos logs dos microsserviços.

---

## 📐 Arquitetura do Sistema

A solução é composta pelos seguintes microsserviços e componentes:

1. **Frontend (`frontend`)**:
   - Interface Web em HTML/JS servida por Nginx.
   - Oferece abas para a **Tela PAGADOR** e **Tela RECEBEDOR**.
2. **Serviço de Ordens de Pagamento (`orders_service`)**:
   - Responsável por criar as ordens de pagamento (`CreateOrdem`) e listá-las (`GetOrdens`).
   - Contém a classe `TRA` vazia pronta para receber regras de validação da ordem.
   - Publica o evento `ORDEM_CRIADA` na fila `payment_orders` do RabbitMQ.
3. **Serviço de Confirmação de Ordens (`confirmation_service`)**:
   - Consome a fila `payment_orders` para manter a lista de ordens pendentes (`ListOrdens`).
   - Contém a classe `TRA` vazia pronta para receber regras de validação se a ordem pode ser confirmada ou não.
   - Ao confirmar (`ConfirmeOrdem`), publica o evento `ORDEM_CONFIRMADA` na fila `confirmed_orders` do RabbitMQ.
4. **Serviço de Gestão de Contas (`accounts_service`)**:
   - Mantém os saldos dos usuários (`PAGADOR_1`, `RECEBEDOR_1`).
   - Escuta a fila `confirmed_orders` do RabbitMQ para debitar do pagador e creditar no recebedor assim que a confirmação ocorre.
   - Fornece consulta de saldo para ambas as telas do Frontend.
5. **RabbitMQ (`rabbitmq`)**:
   - Broker de mensagens (AMQP na porta `5672`, Management UI na porta `15672`).
6. **Dozzle (`dozzle`)**:
   - Interface para visualização de logs dos containers/pods em tempo real.

---

## 🛠️ Tecnologias Utilizadas

- **Python 3.10** + **FastAPI** + **Uvicorn**
- **Pika** (Cliente RabbitMQ para Python)
- **RabbitMQ** (Message Broker)
- **HTML5 / JavaScript (ES6)** + **Nginx**
- **Docker** & **Docker Compose**
- **Kubernetes (K3s / Minikube)**
- **Dozzle** (Visualizador de logs)

---

## 📂 Estrutura de Pastas

```text
PaymentOrderSystem/
├── README.md
├── docker-compose.yml
├── k8s/
│   ├── rabbitmq.yaml
│   ├── accounts-service.yaml
│   ├── orders-service.yaml
│   ├── confirmation-service.yaml
│   ├── frontend.yaml
│   └── dozzle.yaml
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

## 🚀 Como Executar em Desenvolvimento Local (Docker Compose)

### Passo a Passo

1. **Clone ou navegue até o diretório do projeto**:
   ```bash
   cd PaymentOrderSystem
   ```

2. **Inicie os serviços utilizando o Docker Compose**:
   ```bash
   docker-compose up --build -d
   ```

3. **URLs de Acesso Local**:
   - **Frontend**: [http://localhost:8080](http://localhost:8080)
   - **Dozzle Logs**: [http://localhost:8888](http://localhost:8888)
   - **RabbitMQ Dashboard**: [http://localhost:15672](http://localhost:15672) *(guest/guest)*

---

## ☁️ Como Executar em Produção na AWS EC2 usando K3s

### 1. Pré-requisitos na AWS

1. Crie uma instância **EC2 Linux** (Ubuntu Server 22.04 LTS ou superior recomendado).
2. No **Security Group** da instância, libere as seguintes portas de entrada (Inbound Rules):
   - **22 (SSH)**: Acesso ao terminal.
   - **30080 (TCP)**: Acesso ao Frontend Web.
   - **30888 (TCP)**: Acesso ao Dozzle (Logs).
   - **30001 - 30003 (TCP)**: Serviços de backend (opcional se acessado via IP público diretamente).

### 2. Passo a Passo de Implantação no EC2

1. **Acesse a sua instância EC2 via SSH**:
   ```bash
   ssh -i "seu-keypair.pem" ubuntu@<IP-PUBLICO-EC2>
   ```

2. **Instale o Docker e o K3s**:
   ```bash
   # Instalar Docker
   sudo apt update && sudo apt install -y docker.io
   sudo usermod -aG docker $USER

   # Instalar K3s
   curl -sfL https://get.k3s.io | sh -
   ```

3. **Clone o repositório do projeto no servidor**:
   ```bash
   git clone <URL_DO_SEU_REPOSITORIO>
   cd PaymentOrderSystem
   ```

4. **Gerar as imagens Docker e importar para o K3s (`containerd`)**:
   ```bash
   # Build das imagens locais
   docker build -t orders-service:latest ./orders_service
   docker build -t confirmation-service:latest ./confirmation_service
   docker build -t accounts-service:latest ./accounts_service
   docker build -t frontend:latest ./frontend

   # Exportar e importar diretamente para o runtime do K3s
   docker save orders-service:latest confirmation-service:latest accounts-service:latest frontend:latest | sudo k3s ctr images import -
   ```

5. **Aplicar os manifestos do Kubernetes**:
   ```bash
   # Aplicar RabbitMQ primeiro
   sudo k3s kubectl apply -f k8s/rabbitmq.yaml

   # Aplicar os demais serviços e deployments
   sudo k3s kubectl apply -f k8s/
   ```

6. **Verificar a subida dos Pods**:
   ```bash
   sudo k3s kubectl get pods,svc -w
   ```
   Aguarde até que todos os Pods estejam no status `Running`.

### 3. URLs de Acesso em Produção (AWS EC2)

Substitua `<IP-PUBLICO-EC2>` pelo IP público ou DNS da sua instância AWS:

- **Frontend Web**: `http://<IP-PUBLICO-EC2>:30080`
- **Dozzle (Logs em Tempo Real)**: `http://<IP-PUBLICO-EC2>:30888`
- **RabbitMQ Manager**: `http://<IP-PUBLICO-EC2>:15672`

---

## 🧪 Roteiro de Teste do Fluxo Completo

1. Abra o navegador no Frontend (Local ou EC2).
2. Na aba **Tela PAGADOR**:
   - Verifique o saldo inicial de `PAGADOR_1` (R$ 1000.00).
   - Insira o recebedor `RECEBEDOR_1` e o valor (ex: `50.00`).
   - Clique em **CreateOrdem**.
3. Acompanhe os logs no Dozzle (`:8888` ou `:30888`):
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