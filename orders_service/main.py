import json
import logging
import os
import uuid
import pika
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = FastAPI(title="Serviço de Ordens de Pagamento")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")

# Classe TRA reservada para regras de negócio do usuário
class TRA:
    @staticmethod
    def validar_ordem(pagador: str, recebedor: str, valor: float) -> bool:
        # Espaço reservado para implementação de regras de negócio
        # Retorne True para aceitar ou False/Exception para rejeitar
        logging.info(f"[TRA] Validando ordem de {pagador} para {recebedor} no valor de {valor}")
        return True

class OrderRequest(BaseModel):
    pagador: str
    recebedor: str
    valor: float

orders_db = {}

def get_rabbitmq_channel():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue="payment_orders", durable=True)
    return connection, channel

@app.post("/ordens")
def create_ordem(order: OrderRequest):
    # Executa validação de regras de negócio
    if not TRA.validar_ordem(order.pagador, order.recebedor, order.valor):
        raise HTTPException(status_code=400, detail="Ordem rejeitada pela classe TRA.")

    order_id = str(uuid.uuid4())[:8]
    order_data = {
        "id": order_id,
        "pagador": order.pagador,
        "recebedor": order.recebedor,
        "valor": order.valor,
        "status": "CRIADA"
    }
    orders_db[order_id] = order_data

    # Envia evento na rede RabbitMQ
    try:
        conn, ch = get_rabbitmq_channel()
        payload = json.dumps({"event": "ORDEM_CRIADA", "data": order_data})
        ch.basic_publish(
            exchange="",
            routing_key="payment_orders",
            body=payload,
            properties=pika.BasicProperties(delivery_mode=2)
        )
        conn.close()
        logging.info(f"Ordem criada e enviada ao RabbitMQ: {order_data}")
    except Exception as e:
        logging.error(f"Erro ao enviar para RabbitMQ: {e}")
        raise HTTPException(status_code=500, detail="Erro de mensageria")

    return order_data

@app.get("/ordens")
def list_ordens():
    return list(orders_db.values())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)