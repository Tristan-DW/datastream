import json
import os
import redis

r = redis.from_url(os.environ["REDIS_URL"])


def handler(event, context):
    try:
        body = json.loads(event.get("body", "{}"))
        channel = body.get("channel")
        if not channel:
            return {"statusCode": 400, "body": json.dumps({"error": "channel required"})}

        payload = json.dumps({**body, "ts": context.aws_request_id})
        r.publish(f"channel:{channel}", payload)
        r.xadd(f"stream:{channel}", {"event": payload})

        return {"statusCode": 200, "body": json.dumps({"ok": True})}
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
