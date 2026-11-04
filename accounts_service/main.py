import json
import logging
import os
import threading
import time
import pika
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = FastAPI(title="Serviço de Gestão de Contas")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")

# Saldos iniciais em memória
accounts_db = {
    "PAGADOR_1": 1000.00,
    "RECEBEDOR_1": 100.00
}

def start_accounts_consumer():
    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
            channel = connection.channel()
            channel.queue_declare(queue="confirmed_orders", durable=True)

            def callback(ch, method, properties, body):
                msg = json.loads(body)
                if msg.get("event") == "ORDEM_CONFIRMADA":
                    data = msg.get("data")
                    pagador = data.get("pagador")
                    recebedor = data.get("recebedor")
                    valor = float(data.get("valor", 0))

                    # Atualiza saldos
                    if pagador in accounts_db:
                        accounts_db[pagador] -= valor
                    else:
                        accounts_db[pagador] = -valor

                    if recebedor in accounts_db:
                        accounts_db[recebedor] += valor
                    else:
                        accounts_db[recebedor] = valor

                    logging.info(f"[BANCO] Saldos Atualizados | {pagador}: {accounts_db[pagador]} | {recebedor}: {accounts_db[recebedor]}")

                ch.basic_ack(delivery_tag=method.delivery_tag)

            channel.basic_consume(queue="confirmed_orders", on_message_callback=callback)
            logging.info("Consumidor do Banco iniciado no RabbitMQ...")
            channel.start_consuming()
        except Exception as e:
            logging.warning(f"Aguardando RabbitMQ estar disponível... ({e})")
            time.sleep(5)

@app.on_event("startup")
def startup_event():
    threading.Thread(target=start_accounts_consumer, daemon=True).start()

@app.get("/contas/{usuario}")
def get_saldo(usuario: str):
    saldo = accounts_db.get(usuario, 0.0)
    return {"usuario": usuario, "saldo": saldo}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)