<div align="center">

<img src="https://skillicons.dev/icons?i=nodejs,python,redis,docker,aws" />

<br/>

![GitHub last commit](https://img.shields.io/github/last-commit/Tristan-DW/datastream?style=for-the-badge&color=6e40c9)
![GitHub stars](https://img.shields.io/github/stars/Tristan-DW/datastream?style=for-the-badge&color=f0883e)
![Node.js](https://img.shields.io/badge/Node.js-43853D?style=for-the-badge&logo=node.js&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-232F3E?style=for-the-badge&logo=amazon-aws&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-238636?style=for-the-badge)

# datastream

> **Real-time analytics pipeline - WebSockets, Node.js, Redis pub/sub, Python processors, and AWS Lambda ingest.**

</div>

---

## Overview

**datastream** is a flexible real-time event pipeline. Events are ingested via REST or AWS Lambda, fanned out through Redis pub/sub, optionally processed by Python workers, and broadcast live to connected clients over WebSockets. Built for dashboards, monitoring systems, and live data feeds.

---

## Architecture

```
REST / AWS Lambda
       |
  Ingest API (Node.js)
       |
  Redis Pub/Sub -------> Python Processors (enrichment, aggregation)
       |
  WebSocket Server
       |
  Dashboard / Mobile clients
```

---

## Features

| Feature | Description |
|---|---|
| **Dual ingest** | REST endpoint or serverless via AWS Lambda |
| **Redis Pub/Sub** | Decoupled fan-out between ingest and broadcast |
| **Redis Streams** | Persistent time-series log with consumer groups |
| **Python Workers** | Event enrichment and aggregation via `asyncio` consumers |
| **WebSocket Server** | Low-latency push to subscribed clients |
| **Channel namespacing** | Subscribe to specific event types or wildcards |
| **Replay API** | Query historical events with offset/count |

---

## Quick Start

```bash
git clone https://github.com/Tristan-DW/datastream.git
cd datastream

cp .env.example .env
docker-compose up -d

# Node.js server
npm install && npm run dev

# Python workers (optional)
cd workers && pip install -r requirements.txt && python main.py
```

---

## Usage

**Publish an event:**
```bash
curl -X POST http://localhost:3000/events \
  -H "Content-Type: application/json" \
  -d '{"channel": "metrics", "type": "page_view", "data": {"path": "/dashboard"}}'
```

**Subscribe via WebSocket:**
```js
const ws = new WebSocket('ws://localhost:3000/ws');
ws.onopen = () => ws.send(JSON.stringify({ action: 'subscribe', channel: 'metrics' }));
ws.onmessage = (e) => console.log('Event:', JSON.parse(e.data));
```

**AWS Lambda ingest:**
```python
import boto3, json

def handler(event, context):
    payload = json.loads(event['body'])
    # Forward to Redis via ElastiCache
    publish_to_redis(payload['channel'], payload)
    return {'statusCode': 200, 'body': '{"ok":true}'}
```

---

## Project Structure

```
datastream/
├── src/                # Node.js server (ingest + WS)
├── workers/            # Python async event processors
│   ├── main.py
│   └── processors/
├── lambda/             # AWS Lambda ingest handler
├── docker-compose.yml
└── package.json
```

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes (`git commit -m 'Add my feature'`)
4. Push to the branch (`git push origin feature/my-feature`)
5. Open a Pull Request

---

<div align="center">

<sub>Architected by <a href="https://github.com/Tristan-DW">Tristan</a> - Head Architect</sub>

</div>
