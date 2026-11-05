"""Configuração do serviço: tudo que vem de variável de ambiente fica aqui."""
import os

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
PAYMENT_ORDERS_QUEUE = "payment_orders"

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "dbname": os.getenv("DB_NAME", "orders"),
    "user": os.getenv("DB_USER", "orders"),
    "password": os.getenv("DB_PASSWORD", "orders"),
}
