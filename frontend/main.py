import json
import logging
import os
import sqlite3
import threading
import time

import pika
from fastapi import FastAPI

logging.basicConfig(level=logging.INFO, format="%(asctime)s | payment | %(message)s")
logging.getLogger("pika").setLevel(logging.WARNING)
log = logging.getLogger("payment")

DB_PATH = "/data/payment.db"
RABBIT_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
EXCHANGE = "shop.events"
QUEUE = "payment.q"
LIMIT = 1000  # acima disso o pagamento é recusado

app = FastAPI(title="payment")


def run(sql, params=()):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = [dict(r) for r in conn.execute(sql, params).fetchall()]
    conn.commit()
    conn.close()
    return rows


def on_message(channel, method, properties, body):
    data = json.loads(body)
    log.info("RECEBEU evento %s: %s", method.routing_key, data)

    status = "APROVADO" if data["amount"] <= LIMIT else "RECUSADO"
    run(
        "INSERT INTO payments (order_id, amount, status) VALUES (?, ?, ?)",
        (data["order_id"], data["amount"], status),
    )
    log.info("pagamento do pedido %s: %s", data["order_id"], status)

    channel.basic_ack(method.delivery_tag)


def consume():
    while True:
        try:
            conn = pika.BlockingConnection(pika.URLParameters(RABBIT_URL))
            channel = conn.channel()
            channel.exchange_declare(EXCHANGE, "topic", durable=True)
            channel.queue_declare(QUEUE, durable=True)
            channel.queue_bind(QUEUE, EXCHANGE, "order.created")
            channel.basic_consume(QUEUE, on_message)
            log.info("conectado ao RabbitMQ, escutando a fila %s", QUEUE)
            channel.start_consuming()
        except Exception as e:
            log.warning("sem conexão com o RabbitMQ (%s), tentando de novo em 3s", e)
            time.sleep(3)


@app.on_event("startup")
def startup():
    run("CREATE TABLE IF NOT EXISTS payments (id INTEGER PRIMARY KEY AUTOINCREMENT, order_id TEXT, amount REAL, status TEXT)")
    threading.Thread(target=consume, daemon=True).start()
    log.info("serviço iniciado")


@app.get("/payments")
def list_payments():
    return run("SELECT * FROM payments")