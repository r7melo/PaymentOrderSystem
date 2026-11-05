"""Camada de mensageria: consome a fila do RabbitMQ e repassa ao serviço."""
import json
import logging
import time

import pika

from app import service
from app.config import CONFIRMED_ORDERS_QUEUE, RABBITMQ_HOST


def tratar_evento(msg: dict):
    """Lógica de uma mensagem, separada do RabbitMQ para poder ser testada sozinha."""
    if msg.get("event") != "ORDEM_CONFIRMADA":
        return

    data = msg.get("data")
    pagador = data.get("pagador")
    recebedor = data.get("recebedor")
    valor = float(data.get("valor", 0))

    try:
        service.aplicar_ordem(pagador, recebedor, valor)
        logging.info(f"[BANCO] Ordem aplicada | {pagador} -> {recebedor} | R$ {valor:.2f}")
    except service.ContaNaoEncontradaError as e:
        # Conta inexistente: reenviar a mensagem não adianta, então descarta e loga.
        logging.error(f"[BANCO] Ordem {data.get('id')} descartada: {e}")
    # Qualquer outra exceção (ex.: banco fora do ar) sobe sem ack:
    # a conexão cai, o loop reconecta e o RabbitMQ reentrega a mensagem.


def _callback(ch, method, properties, body):
    tratar_evento(json.loads(body))
    ch.basic_ack(delivery_tag=method.delivery_tag)


def start_accounts_consumer():
    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
            channel = connection.channel()
            channel.queue_declare(queue=CONFIRMED_ORDERS_QUEUE, durable=True)
            channel.basic_consume(queue=CONFIRMED_ORDERS_QUEUE, on_message_callback=_callback)
            logging.info("Consumidor do Banco iniciado no RabbitMQ...")
            channel.start_consuming()
        except Exception as e:
            logging.warning(f"Aguardando RabbitMQ estar disponível... ({e})")
            time.sleep(5)