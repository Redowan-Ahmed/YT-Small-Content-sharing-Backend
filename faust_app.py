import faust
import os
import django
import asyncio

# Set up Django environment for Faust
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config_youtube.settings')
# django.setup()

app = faust.App(
    'likes_dislikes_batch_app',
    broker='kafka://localhost:9092',
    store='memory://',
)
# Record schema
class LikeDislikeEvent(faust.Record, serializer='json'):
    user_id: int
    video_id: int
    action: str  # 'like' or 'dislike'

# Kafka topic
topic = app.topic('likes_dislikes_events', value_type=LikeDislikeEvent)

# Batch buffer and settings
batch = []
batch_lock = False
BATCH_SIZE = 1000
FLUSH_INTERVAL = 1.0

@app.agent(topic)
async def process_likes_dislikes(stream):
    async for event in stream:
        global batch
        batch.append(event)

        # If batch size reached, process immediately
        # if len(batch) >= BATCH_SIZE:
        #     await flush_batch()

@app.timer(interval=FLUSH_INTERVAL)
async def flush_batch_timer():
    """Flush batch every 30 ms."""
    await flush_batch()

async def flush_batch():
    """Process and save the current batch to the database."""
    global batch, batch_lock
    if batch and not batch_lock:
        l = 1
        batch_lock = True  # Lock to avoid parallel flushes
        current_batch = batch[:]  # Create a copy of the batch
        batch = []  # Clear the global batch
        batch_lock = False
        print(current_batch, l++)

# if __name__ == '__main__':
#     app.main()
