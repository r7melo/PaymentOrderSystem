import asyncio
import json
import logging
import aio_pika
from sqlalchemy import text
from app.core.config import settings
from app.db.database import AsyncSessionLocal, engine
from app.services.auth_handlers import dispatch_action

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("auth_service")


async def wait_for_db() -> None:
    for attempt in range(1, 11):
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            logger.info("Conexão com auth-db estabelecida com sucesso.")
            return
        except Exception as exc:
            logger.warning(f"Aguardando auth-db (tentativa {attempt}/10): {exc}")
            await asyncio.sleep(2)
    raise RuntimeError("Não foi possível conectar ao auth-db.")


async def on_message(message: aio_pika.IncomingMessage, exchange: aio_pika.Exchange) -> None:
    async with message.process():
        try:
            body = json.loads(message.body.decode("utf-8"))
            action = body.get("action", "")
            payload = body.get("payload", {})
            logger.info(f"Processando ação RPC: {action!r} (correlation_id={message.correlation_id})")

            async with AsyncSessionLocal() as session:
                response = await dispatch_action(session, action, payload)
        except Exception as exc:
            logger.exception("Erro interno ao processar mensagem RPC")
            response = {"status": 500, "error": f"Erro interno no auth_service: {exc}"}

        if message.reply_to:
            await exchange.publish(
                aio_pika.Message(
                    body=json.dumps(response).encode("utf-8"),
                    correlation_id=message.correlation_id,
                    content_type="application/json",
                ),
                routing_key=message.reply_to,
            )


async def main() -> None:
    await wait_for_db()
    connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=10)
        queue = await channel.declare_queue(settings.AUTH_QUEUE, durable=True)
        logger.info(f"auth_service escutando fila {settings.AUTH_QUEUE!r}...")

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                asyncio.create_task(on_message(message, channel.default_exchange))


if __name__ == "__main__":
    asyncio.run(main())