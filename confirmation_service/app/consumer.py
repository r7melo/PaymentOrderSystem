"""Camada de mensageria (entrada): consome a fila payment_orders e repassa à ação."""
import json
import logging
import time

import pika

from app.acoes.receber_ordem import receber_ordem
from app.config import PAYMENT_ORDERS_QUEUE, RABBITMQ_HOST


def tratar_evento(msg: dict):
    """Lógica de uma mensagem, separada do RabbitMQ para poder ser testada sozinha."""
    if msg.get("event") != "ORDEM_CRIADA":
        return
    receber_ordem(msg.get("data"))


def _callback(ch, method, properties, body):
    tratar_evento(json.loads(body))
    ch.basic_ack(delivery_tag=method.delivery_tag)


def start_confirmation_consumer():
    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
            channel = connection.channel()
            channel.queue_declare(queue=PAYMENT_ORDERS_QUEUE, durable=True)
            channel.basic_consume(queue=PAYMENT_ORDERS_QUEUE, on_message_callback=_callback)
            logging.info("Consumidor de Confirmações iniciado no RabbitMQ...")
            channel.start_consuming()
        except Exception as e:
            # Falha no banco ou no broker sobe sem ack: a conexão cai, o loop reconecta
            # e o RabbitMQ reentrega a mensagem.
            logging.warning(f"Aguardando RabbitMQ/banco estarem disponíveis... ({e})")
            time.sleep(5)
