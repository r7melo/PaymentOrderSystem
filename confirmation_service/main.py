import json
import logging
import os
import threading
import time
import pika
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = FastAPI(title="Serviço de Confirmação de Ordens")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")

# Classe TRA reservada para regras de negócio do usuário na confirmação
class TRA:
    @staticmethod
    def validar_confirmacao(order_data: dict) -> bool:
        # Espaço reservado para verificação se o usuário pode confirmar ou não
        logging.info(f"[TRA] Validando se o usuário pode confirmar a ordem {order_data.get('id')}")
        return True

orders_to_confirm = {}

def start_consumer():
    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
            channel = connection.channel()
            channel.queue_declare(queue="payment_orders", durable=True)

            def callback(ch, method, properties, body):
                msg = json.loads(body)
                if msg.get("event") == "ORDEM_CRIADA":
                    data = msg.get("data")
                    orders_to_confirm[data["id"]] = data
                    logging.info(f"Ordem {data['id']} recebida para aguardar confirmação.")
                ch.basic_ack(delivery_tag=method.delivery_tag)

            channel.basic_consume(queue="payment_orders", on_message_callback=callback)
            logging.info("Consumidor de Confirmações iniciado no RabbitMQ...")
            channel.start_consuming()
        except Exception as e:
            logging.warning(f"Aguardando RabbitMQ estar disponível... ({e})")
            time.sleep(5)

@app.on_event("startup")
def startup_event():
    threading.Thread(target=start_consumer, daemon=True).start()

@app.get("/confirmacoes")
def get_ordens_pendentes():
    return list(orders_to_confirm.values())

@app.post("/confirmacoes/{order_id}/confirmar")
def confirmar_ordem(order_id: str):
    if order_id not in orders_to_confirm:
        raise HTTPException(status_code=404, detail="Ordem não encontrada")

    order = orders_to_confirm[order_id]

    if not TRA.validar_confirmacao(order):
        raise HTTPException(status_code=400, detail="Confirmação rejeitada pela regra TRA.")

    order["status"] = "CONFIRMADA"

    # Publica na rede para atualização final dos valores
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
        channel = connection.channel()
        channel.queue_declare(queue="confirmed_orders", durable=True)
        payload = json.dumps({"event": "ORDEM_CONFIRMADA", "data": order})
        channel.basic_publish(
            exchange="",
            routing_key="confirmed_orders",
            body=payload,
            properties=pika.BasicProperties(delivery_mode=2)
        )
        connection.close()
        logging.info(f"Ordem {order_id} confirmada e enviada para atualização de saldo no RabbitMQ.")
    except Exception as e:
        logging.error(f"Erro ao publicar confirmação: {e}")
        raise HTTPException(status_code=500, detail="Erro de mensageria")

    return {"status": "SUCESSO", "order": order}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)