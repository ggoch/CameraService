
import pika
import json
import logging
from setting.config import get_settings

settings = get_settings()

# 全局RabbitMQ连接和频道
connection = None
channel = None

logger = logging.getLogger(__name__)

parameters = pika.ConnectionParameters(
    host=settings.rabbitmq_host,
    port=settings.rabbitmq_port,
    virtual_host='/',
    credentials=pika.PlainCredentials("ggoch", "ggoch")
)

def get_rabbitmq_channel():
    connection = None
    channel = None
    # global connection, channel
    if connection is None or channel is None or connection.is_closed or channel.is_closed:
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
    return channel

def publish_rabbitmq_event(event_data: dict,router_key:str):
        try:
            channel = get_rabbitmq_channel()
            channel.basic_publish(
                exchange='',
                routing_key=router_key,
                body=json.dumps(event_data),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                ))
        except Exception as e:
            print(f"Failed to publish RabbitMQ event: {e}")
            logger.error(f"Failed to publish RabbitMQ event: {e}")