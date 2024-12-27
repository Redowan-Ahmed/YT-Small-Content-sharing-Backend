from kafka import KafkaProducer
import json
import random

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
)

def send_bulk_events():
    for _ in range(10000):  # Simulate 10,000 events
        user_id = random.randint(1, 1000)
        video_id = random.randint(1, 500)
        action = random.choice(['like', 'dislike'])
        event = {"user_id": user_id, "video_id": video_id, "action": action}
        producer.send('likes_dislikes_events', value=event)

# Run the producer
send_bulk_events()
