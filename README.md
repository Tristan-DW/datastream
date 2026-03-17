<div align="center">

<img src="https://skillicons.dev/icons?i=nodejs,redis,docker,linux" />

<br/>

![GitHub last commit](https://img.shields.io/github/last-commit/Tristan-DW/datastream?style=for-the-badge&color=6e40c9)
![GitHub stars](https://img.shields.io/github/stars/Tristan-DW/datastream?style=for-the-badge&color=f0883e)
![Node.js](https://img.shields.io/badge/Node.js-43853D?style=for-the-badge&logo=node.js&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![WebSockets](https://img.shields.io/badge/WebSockets-black?style=for-the-badge&logo=socket.io&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-238636?style=for-the-badge)

# datastream

> **Real-time analytics pipeline - WebSockets, Node.js, Redis pub/sub, and live dashboards.**

</div>

---

## Overview

**datastream** is a real-time event pipeline that ingests events via a REST API, fans them out through Redis pub/sub, and broadcasts live updates to connected clients over WebSockets. Built for high-throughput scenarios like dashboards, monitoring systems, and live feeds.

---

## Architecture

```
Client --[REST POST]--> Ingest API --> Redis Pub/Sub --> WS Server --[push]--> Dashboard
                                           |
                                      Time-series store (Redis Streams)
```

---

## Features

| Feature | Description |
|---|---|
| **Event Ingestion** | REST endpoint accepting structured event payloads |
| **Redis Pub/Sub** | Decoupled fan-out - ingest and broadcast are independent processes |
| **Redis Streams** | Persistent time-series event log with consumer groups |
| **WebSocket Server** | Low-latency push to subscribed clients via `ws` |
| **Namespaced Channels** | Subscribe to specific event types or wildcards |
| **Replay** | Query historical events from the stream with offset/count |
| **Health Endpoint** | Live connection count, queue depth, Redis ping |

---

## Quick Start

```bash
git clone https://github.com/Tristan-DW/datastream.git
cd datastream

cp .env.example .env
docker-compose up -d

npm install
npm run dev
```

---

## Usage

**Publish an event:**
```bash
curl -X POST http://localhost:3000/events \
  -H "Content-Type: application/json" \
  -d '{"channel": "metrics", "type": "page_view", "data": {"path": "/dashboard", "user": "u_123"}}'
```

**Subscribe via WebSocket:**
```js
const ws = new WebSocket('ws://localhost:3001');

ws.onopen = () => {
  ws.send(JSON.stringify({ action: 'subscribe', channel: 'metrics' }));
};

ws.onmessage = (msg) => {
  const event = JSON.parse(msg.data);
  console.log('Live event:', event);
};
```

---

## Project Structure

```
datastream/
├── src/
│   ├── ingest/         # REST API event intake
│   ├── broker/         # Redis pub/sub bridge
│   ├── ws/             # WebSocket server
│   ├── streams/        # Redis Streams read/write
│   ├── config/         # Redis + env config
│   └── server.js
├── docker-compose.yml
├── .env.example
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
