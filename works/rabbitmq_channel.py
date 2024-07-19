
import pika
from queue import Queue
import json
import logging
import threading
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
    credentials=pika.PlainCredentials(settings.rabbitmq_user, settings.rabbitmq_password)
)

connection_pool = Queue(maxsize=10)

rabbitmq_lock = threading.Lock()

def get_rabbitmq_channel():
    connection = None
    channel = None
    try:
        with rabbitmq_lock:
            if connection_pool.empty():
                connection = pika.BlockingConnection(parameters)
                connection_pool.put(connection)
            else:
                connection = connection_pool.get()
                if connection.is_closed:
                    connection = pika.BlockingConnection(parameters)
                    connection_pool.put(connection)
            channel = connection.channel()
    except Exception as e:
        print(f"Error getting RabbitMQ channel: {e}")
        if connection and not connection.is_closed:
            connection.close()
        raise
    return connection, channel

def release_rabbitmq_channel(connection):
    try:
        with rabbitmq_lock:
            if connection and not connection.is_closed:
                connection_pool.put(connection)
    except Exception as e:
        print(f"Error releasing RabbitMQ connection: {e}")
        if connection and not connection.is_closed:
            connection.close()

# def get_rabbitmq_channel():
#     connection = None
#     channel = None
#     # global connection, channel
#     if connection is None or channel is None or connection.is_closed or channel.is_closed:
#         connection = pika.BlockingConnection(parameters)
#         channel = connection.channel()
#     return channel

def publish_rabbitmq_event(event_data: dict,router_key:str):
        try:
            connection,channel = get_rabbitmq_channel()
            channel.basic_publish(
                exchange='',
                routing_key=router_key,
                body=json.dumps(event_data),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                ))
            release_rabbitmq_channel(connection)
        except Exception as e:
            print(f"Failed to publish RabbitMQ event: {e}")
            logger.error(f"Failed to publish RabbitMQ event: {e}")