"""
RabbitMQ Event Bus Implementation
Handles event publishing and subscription with RabbitMQ
"""
import json
import asyncio
import pika
from typing import Dict, List, Callable
from cqrs_base import EventBus, DomainEvent
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RabbitMQEventBus(EventBus):
    """RabbitMQ implementation of Event Bus"""

    def __init__(self, rabbitmq_url: str = None, exchange_name: str = "talentlink.events"):
        self.rabbitmq_url = rabbitmq_url or os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672")
        self.exchange_name = exchange_name
        self.connection = None
        self.channel = None
        self._subscribers: Dict[str, List[Callable]] = {}
        self._connect()

    def _connect(self):
        """Establish connection to RabbitMQ"""
        try:
            # Parse connection URL
            if self.rabbitmq_url.startswith("https://"):
                # Handle web UI URL - convert to AMQP
                host = self.rabbitmq_url.replace("https://", "").split("/")[0]
                self.rabbitmq_url = f"amqp://guest:guest@{host}:5672"

            params = pika.URLParameters(self.rabbitmq_url)
            self.connection = pika.BlockingConnection(params)
            self.channel = self.connection.channel()

            # Declare exchange
            self.channel.exchange_declare(
                exchange=self.exchange_name,
                exchange_type='topic',
                durable=True
            )
            logger.info(f"Connected to RabbitMQ at {self.rabbitmq_url}")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            # Don't fail - service should work without events for now
            self.channel = None

    async def publish(self, event: DomainEvent, routing_key: str = None):
        """Publish event to RabbitMQ"""
        if not self.channel:
            logger.warning(f"RabbitMQ not connected, event not published: {event.event_type}")
            return

        try:
            routing_key = routing_key or event.event_type
            message = json.dumps(event.to_dict(), default=str)

            self.channel.basic_publish(
                exchange=self.exchange_name,
                routing_key=routing_key,
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # persistent
                    content_type='application/json'
                )
            )
            logger.info(f"Published event: {event.event_type} with routing key: {routing_key}")
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")

    async def subscribe(self, event_type: str, handler: callable):
        """Subscribe to events (for consumer services)"""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
        logger.info(f"Subscribed to event type: {event_type}")

    def start_consuming(self, queue_name: str, routing_keys: List[str]):
        """Start consuming events from queue (blocking)"""
        if not self.channel:
            logger.warning("RabbitMQ not connected, cannot start consuming")
            return

        try:
            # Declare queue
            self.channel.queue_declare(queue=queue_name, durable=True)

            # Bind queue to exchange with routing keys
            for routing_key in routing_keys:
                self.channel.queue_bind(
                    exchange=self.exchange_name,
                    queue=queue_name,
                    routing_key=routing_key
                )
                logger.info(f"Queue {queue_name} bound to routing key: {routing_key}")

            # Set up consumer
            def callback(ch, method, properties, body):
                try:
                    event_data = json.loads(body)
                    event_type = event_data.get('event_type')

                    # Call registered handlers
                    if event_type in self._subscribers:
                        for handler in self._subscribers[event_type]:
                            handler(event_data)

                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    logger.info(f"Processed event: {event_type}")
                except Exception as e:
                    logger.error(f"Error processing event: {e}")
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

            self.channel.basic_consume(
                queue=queue_name,
                on_message_callback=callback,
                auto_ack=False
            )

            logger.info(f"Started consuming from queue: {queue_name}")
            self.channel.start_consuming()
        except Exception as e:
            logger.error(f"Error in start_consuming: {e}")

    def close(self):
        """Close RabbitMQ connection"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            logger.info("RabbitMQ connection closed")
