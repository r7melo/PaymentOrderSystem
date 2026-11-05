# Sistema de Ordens de Pagamento e Confirmação Assíncrona

Este projeto implementa uma arquitetura baseada em microsserviços orientada a eventos para um fluxo de ordens de pagamento, confirmação e atualização de saldos em contas. A solução utiliza **FastAPI** para as APIs, **RabbitMQ** para mensageria assíncrona, **Docker / Docker Compose** e **Kubernetes (K3s)** para orquestração, **Nginx** para servir o frontend estático, e **Dozzle** para monitorização de logs em tempo real.

---

## 📐 Arquitetura do Sistema

1. **Frontend (`frontend`)**:
   - Interface Web em HTML/JS servida por Nginx na porta `30080`.
   - Oferece abas para a **Tela PAGADOR** e **Tela RECEBEDOR**.
2. **Serviço de Ordens de Pagamento (`orders_service`)**:
   - Cria as ordens (`CreateOrdem`) e lista as existentes (`GetOrdens`), gravando no seu próprio banco (`orders_db`).
   - Publica o evento na fila `payment_orders` do RabbitMQ.
3. **Serviço de Confirmação de Ordens (`confirmation_service`)**:
   - Consome a fila `payment_orders` e mantém as ordens pendentes no seu próprio banco (`confirmation_db`).
   - Ao confirmar (`ConfirmeOrdem`), marca a ordem como `CONFIRMADA` e publica o evento na fila `confirmed_orders`.
4. **Serviço de Gestão de Contas (`accounts_service`)**:
   - Escuta a fila `confirmed_orders` para efetuar os débitos e créditos.
   - Fornece consulta de saldos para o Frontend.
5. **RabbitMQ (`rabbitmq`)**:
   - Broker de mensagens (AMQP na porta `5672`, Management UI exposta na porta `31672`).
6. **Dozzle (`dozzle`)**:
   - Interface Web para visualização dos logs do cluster em tempo real na porta `30888`.

---

## 🛠️ Tecnologias Utilizadas

- **Python 3.10** + **FastAPI** + **Uvicorn**
- **Pika** (Cliente RabbitMQ)
- **RabbitMQ** (Message Broker)
- **HTML5 / JavaScript** + **Nginx**
- **Docker** & **Docker Compose**
- **Kubernetes (K3s)**
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
│   ├── orders-db.yaml
│   ├── confirmation-service.yaml
│   ├── confirmation-db.yaml
│   ├── frontend.yaml
│   └── dozzle.yaml
├── frontend/
│   ├── Dockerfile
│   ├── nginx.conf
│   └── index.html
├── accounts_db/            # schema e dados de teste do banco de contas
│   ├── init.sql
│   └── seed.sql
├── orders_db/              # schema do banco de ordens
│   └── init.sql
├── confirmation_db/        # schema do banco de confirmações
│   └── init.sql
├── accounts_service/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/                # config, database, routes, service, repository, consumer
├── orders_service/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/                # config, database, routes, repository, publisher, tra, acoes/
│       └── acoes/          # criar_ordem.py, listar_ordens.py
└── confirmation_service/
    ├── Dockerfile
    ├── requirements.txt
    └── app/                # config, database, routes, repository, publisher, consumer, tra, acoes/
        └── acoes/          # receber_ordem.py, listar_confirmacoes.py, confirmar_ordem.py
```

---

## 🚀 Como Executar em Desenvolvimento Local (Docker Compose)

1. **Iniciar os serviços**:
   ```bash
   docker-compose up --build -d
   ```

2. **URLs de Acesso Local**:
   - **Frontend**: `http://localhost:8080`
   - **Dozzle Logs**: `http://localhost:8888`
   - **RabbitMQ Dashboard**: `http://localhost:15672` *(guest/guest)*

---

## ☁️ Como Executar em Produção na AWS EC2 usando K3s

### 1. Configuração do Security Group na AWS

No painel da AWS EC2, adicione as seguintes regras de entrada (**Inbound Rules**):

| Protocolo | Intervalo de Portas | Origem | Descrição |
| :--- | :--- | :--- | :--- |
| **SSH** | `22` | `0.0.0.0/0` | Acesso ao terminal |
| **Custom TCP** | `30080` | `0.0.0.0/0` | Frontend Web |
| **Custom TCP** | `30888` | `0.0.0.0/0` | Dozzle (Logs) |
| **Custom TCP** | `31672` | `0.0.0.0/0` | RabbitMQ Dashboard |
| **Custom TCP** | `30001 - 30003` | `0.0.0.0/0` | APIs de Backend |

---

### 2. Passo a Passo de Implantação na EC2

1. **Aceder à EC2 via SSH**:
   ```bash
   ssh -i "seu-keypair.pem" ubuntu@<IP-PUBLICO-EC2>
   ```

2. **Instalar Docker e K3s**:
   ```bash
   # Instalar Docker
   sudo apt update && sudo apt install -y docker.io
   sudo usermod -aG docker $USER

   # Instalar K3s
   curl -sfL https://get.k3s.io | sh -

   # Configurar o kubeconfig para o utilizador root
   mkdir -p ~/.kube
   cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
   chmod 600 ~/.kube/config
   ```

3. **Obter o código e compilar as imagens**:
   ```bash
   git clone <URL_DO_REPOSITORIO>
   cd PaymentOrderSystem

   # Build das imagens no Docker local
   docker build -t orders-service:latest ./orders_service
   docker build -t confirmation-service:latest ./confirmation_service
   docker build -t accounts-service:latest ./accounts_service
   docker build -t frontend:latest ./frontend

   # Importar imagens para o runtime containerd do K3s
   docker save orders-service:latest confirmation-service:latest accounts-service:latest frontend:latest | k3s ctr images import -
   ```

4. **Aplicar os manifestos do Kubernetes**:
   ```bash
   # Subir o RabbitMQ primeiro
   kubectl apply -f k8s/rabbitmq.yaml

   # Subir todos os serviços e deployments
   kubectl apply -f k8s/
   ```

5. **Verificar o estado do cluster**:
   ```bash
   kubectl get pods,svc
   ```
   Aguarde até que todos os pods estejam com o estado `Running` (1/1).

---

### 3. URLs de Acesso em Produção

- **Frontend Web**: `http://<IP-PUBLICO-EC2>:30080`
- **Dozzle (Logs em Tempo Real)**: `http://<IP-PUBLICO-EC2>:30888`
- **RabbitMQ Dashboard**: `http://<IP-PUBLICO-EC2>:31672` *(guest/guest)*

---

## 🧪 Roteiro de Teste do Fluxo Completo

1. Aceda ao **Frontend** (`:30080`).
2. Na aba **Tela PAGADOR**:
   - Confirme o saldo inicial do `PAGADOR_1` (R$ 1000.00).
   - Insira o recebedor `RECEBEDOR_1`, indique um valor (ex: `100.00`) e clique em **CreateOrdem**.
3. Acompanhe os logs no **Dozzle** (`:30888`) para ver o evento a ser publicado e consumido.
4. Na aba **Tela RECEBEDOR**:
   - Clique em **ListOrdens** para visualizar a ordem pendente.
   - Clique em **ConfirmeOrdem**.
5. Clique no botão **Atualizar Saldo** em qualquer uma das abas:
   - Saldo do `PAGADOR_1`: **900.00**
   - Saldo do `RECEBEDOR_1`: **200.00**