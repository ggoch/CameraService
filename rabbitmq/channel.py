import aio_pika
import json
import logging
from setting.config import get_settings

settings = get_settings()

# 全局RabbitMQ连接和频道
connection = None
channel = None

logger = logging.getLogger(__name__)

async def get_rabbitmq_channel():
    global connection, channel
    if connection is None or channel is None or connection.is_closed or channel.is_closed:
        connection = await aio_pika.connect_robust(
            f"amqp://{settings.rabbitmq_user}:{settings.rabbitmq_password}@{settings.rabbitmq_host}:{settings.rabbitmq_port}/")
        channel = await connection.channel()
    return channel

async def publish_rabbitmq_event(event_data: dict, router_key: str):
    try:
        channel = await get_rabbitmq_channel()
        await channel.declare_queue(router_key, durable=True)
        await channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps(event_data).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            ),
            routing_key=router_key
        )
        print(f"Event published: {event_data} to queue {router_key}")
    except Exception as e:
        print(f"Failed to publish RabbitMQ event: {e}")
        logger.error(f"Failed to publish RabbitMQ event: {e}")