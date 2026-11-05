"""Camada de mensageria (saída): publica eventos no RabbitMQ.
Não conhece regra de negócio; quem chama decide quando publicar."""
import json

import pika

from app.config import RABBITMQ_HOST


def publicar(fila: str, evento: str, data: dict):
    """Envia o evento como mensagem persistente. Levanta exceção se o broker falhar."""
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    try:
        channel = connection.channel()
        channel.queue_declare(queue=fila, durable=True)
        channel.basic_publish(
            exchange="",
            routing_key=fila,
            body=json.dumps({"event": evento, "data": data}),
            properties=pika.BasicProperties(delivery_mode=2),
        )
    finally:
        connection.close()
