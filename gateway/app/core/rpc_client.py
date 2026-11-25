import json
import uuid
import asyncio
import aio_pika
from fastapi import HTTPException
from app.core.config import settings


class RabbitRpcClient:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.callback_queue = None
        self.futures: dict[str, asyncio.Future] = {}

    async def connect(self):
        self.connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
        self.channel = await self.connection.channel()
        self.callback_queue = await self.channel.declare_queue(exclusive=True)
        await self.callback_queue.consume(self._on_response, no_ack=True)

    async def close(self):
        if self.connection:
            await self.connection.close()

    async def _on_response(self, message: aio_pika.IncomingMessage):
        future = self.futures.pop(message.correlation_id, None)
        if future and not future.done():
            future.set_result(json.loads(message.body.decode("utf-8")))

    async def call(self, queue_name: str, action: str, payload: dict) -> dict:
        correlation_id = str(uuid.uuid4())
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        self.futures[correlation_id] = future

        body = json.dumps({"action": action, "payload": payload}).encode("utf-8")
        await self.channel.default_exchange.publish(
            aio_pika.Message(
                body=body,
                correlation_id=correlation_id,
                reply_to=self.callback_queue.name,
            ),
            routing_key=queue_name,
        )

        try:
            return await asyncio.wait_for(future, timeout=settings.RPC_TIMEOUT)
        except asyncio.TimeoutError:
            self.futures.pop(correlation_id, None)
            raise HTTPException(
                status_code=504,
                detail=f"Nenhum worker respondeu na fila '{queue_name}' dentro de {settings.RPC_TIMEOUT}s.",
            )


rpc_client = RabbitRpcClient()