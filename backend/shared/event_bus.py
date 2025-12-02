"""
Event Bus Implementation with RabbitMQ
"""
import json
import logging
from typing import Dict, Callable
import pika
from cqrs_base import DomainEvent, EventBus

logger = logging.getLogger(__name__)


class RabbitMQEventBus(EventBus):
    """RabbitMQ implementation of EventBus"""

    def __init__(self, rabbitmq_url: str):
        self.rabbitmq_url = rabbitmq_url
        self.connection = None
        self.channel = None
        self.subscribers: Dict[str, Callable] = {}
        self._connect()

    def _connect(self):
        """Connect to RabbitMQ"""
        try:
            parameters = pika.URLParameters(self.rabbitmq_url)
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()

            # Declare exchange for events
            self.channel.exchange_declare(
                exchange='domain_events',
                exchange_type='topic',
                durable=True
            )

            logger.info(f"Connected to RabbitMQ at {self.rabbitmq_url}")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise

    async def publish(self, event: DomainEvent, routing_key: str = None):
        """Publish domain event to RabbitMQ"""
        try:
            if not self.channel or self.channel.is_closed:
                self._connect()

            routing_key = routing_key or event.event_type

            message = json.dumps(event.to_dict(), default=str)

            self.channel.basic_publish(
                exchange='domain_events',
                routing_key=routing_key,
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Persistent
                    content_type='application/json'
                )
            )

            logger.info(f"Published event: {event.event_type} with routing key: {routing_key}")

        except Exception as e:
            logger.error(f"Failed to publish event {event.event_type}: {e}")
            raise

    async def subscribe(self, event_type: str, handler: Callable):
        """Subscribe to events"""
        try:
            if not self.channel or self.channel.is_closed:
                self._connect()

            queue_name = f"queue_{event_type}"

            self.channel.queue_declare(queue=queue_name, durable=True)
            self.channel.queue_bind(
                exchange='domain_events',
                queue=queue_name,
                routing_key=event_type
            )

            self.subscribers[event_type] = handler

            def callback(ch, method, properties, body):
                try:
                    event_data = json.loads(body)
                    handler(event_data)
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                except Exception as e:
                    logger.error(f"Error processing event {event_type}: {e}")
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

            self.channel.basic_consume(
                queue=queue_name,
                on_message_callback=callback
            )

            logger.info(f"Subscribed to event: {event_type}")

        except Exception as e:
            logger.error(f"Failed to subscribe to {event_type}: {e}")
            raise

    def start_consuming(self):
        """Start consuming messages"""
        try:
            logger.info("Starting to consume messages...")
            self.channel.start_consuming()
        except Exception as e:
            logger.error(f"Error while consuming: {e}")
            raise

    def close(self):
        """Close connection"""
        try:
            if self.connection and not self.connection.is_closed:
                self.connection.close()
                logger.info("RabbitMQ connection closed")
        except Exception as e:
            logger.error(f"Error closing connection: {e}")