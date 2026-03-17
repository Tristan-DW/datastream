import asyncio
import json
import redis.asyncio as aioredis


async def process_event(event: dict) -> dict:
    # Enrich and aggregate incoming events
    # Add server-side timestamp
    import time
    event["processed_at"] = time.time()

    # Example: aggregate page view counts
    if event.get("type") == "page_view":
        async with aioredis.from_url("redis://localhost:6379") as r:
            await r.hincrby("stats:page_views", event["data"].get("path", "/"), 1)

    return event


async def consume(channel: str = "metrics"):
    r = await aioredis.from_url("redis://localhost:6379")
    pubsub = r.pubsub()
    await pubsub.subscribe(f"channel:{channel}")

    print(f"Worker listening on channel:{channel}")
    async for message in pubsub.listen():
        if message["type"] != "message":
            continue
        try:
            event = json.loads(message["data"])
            processed = await process_event(event)
            print(f"Processed: {processed['type']} @ {processed['ts']}")
        except Exception as e:
            print(f"Error processing event: {e}")


if __name__ == "__main__":
    asyncio.run(consume())
