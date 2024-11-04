import json
import asyncio
import random
import string
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
from concurrent.futures import ThreadPoolExecutor
from channels.layers import BaseChannelLayer
from threading import Lock


class KafkaChannelLayer(BaseChannelLayer):
    def __init__(self, hosts=None, group_id=None, topic_prefix="django-channels", num_partitions=3, **kwargs):
        super().__init__(expiry=kwargs.pop("expiry", 60))

        # Kafka settings
        self.hosts = hosts or ["localhost:9092"]
        self.group_id = group_id or "django-channels-group"
        self.topic_prefix = topic_prefix
        self.num_partitions = num_partitions

        # Initialize connection pools
        self._producers = []
        self._producer_lock = Lock()
        self._initialize_producers()

        # Asynchronous message queue to store received messages
        self.message_queue = asyncio.Queue()

        # Internal dictionary to manage group-channel mappings
        self.groups = {}

    def _initialize_producers(self):
        for _ in range(self.num_partitions):
            producer = KafkaProducer(
                bootstrap_servers=self.hosts,
                value_serializer=lambda v: json.dumps(v).encode("utf-8")
            )
            self._producers.append(producer)

    def _get_producer(self):
        with self._producer_lock:
            # Round-robin selection of producer for load distribution
            producer = self._producers.pop(0)
            self._producers.append(producer)
            return producer

    async def send(self, channel, message):
        topic = f"{self.topic_prefix}.{channel}"
        producer = self._get_producer()

        try:
            # Send message to Kafka topic (channel)
            producer.send(topic, value=message)
            producer.flush()
        except KafkaError as e:
            print(f"Error sending message to Kafka: {e}")

    async def group_add(self, group, channel):
        """Add a channel to a group for broadcasting."""
        if group not in self.groups:
            self.groups[group] = set()
        self.groups[group].add(channel)

    async def group_discard(self, group, channel):
        """Remove a channel from a group."""
        if group in self.groups and channel in self.groups[group]:
            self.groups[group].discard(channel)
            if not self.groups[group]:  # Clean up empty group
                del self.groups[group]

    async def group_send(self, group, message):
        """Send a message to all channels in a group."""
        if group in self.groups:
            for channel in self.groups[group]:
                await self.send(channel, message)

    async def receive(self, channel):
        """Asynchronously receive messages and put them into a queue."""
        topic = f"{self.topic_prefix}.{channel}"

        # Create a separate consumer for the topic
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=self.hosts,
            group_id=self.group_id,
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            auto_offset_reset="earliest"
        )

        # Consume messages in a background task
        async def consume_messages():
            for message in consumer:
                # Put the message in the async queue
                await self.message_queue.put(message.value)

        # Start the background consumer task if it's not already running
        asyncio.create_task(consume_messages())

        # Retrieve the next message from the async queue
        return await self.message_queue.get()

    async def new_channel(self, prefix="specific."):
        """Generate a new, unique channel name."""
        random_suffix = ''.join(random.choices(
            string.ascii_letters + string.digits, k=8))
        return f"{prefix}{random_suffix}"

    def valid_channel_name(self, name):
        """Validate that the channel name conforms to the expected pattern."""
        return name.startswith("specific.") or name.startswith("group.")

    async def close(self):
        # Close all producers
        for producer in self._producers:
            producer.close()
