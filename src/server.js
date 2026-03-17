const express = require('express');
const { createServer } = require('http');
const { WebSocketServer } = require('ws');
const { redis, redisSub } = require('./config/redis');

const app = express();
app.use(express.json());

const clients = new Map(); // clientId -> { ws, subscriptions }

// Ingest endpoint
app.post('/events', async (req, res) => {
  const { channel, type, data } = req.body;
  if (!channel || !type) return res.status(400).json({ error: 'channel and type required' });

  const event = { channel, type, data, ts: Date.now() };

  // Persist to Redis Stream
  await redis.xadd(`stream:${channel}`, '*', 'event', JSON.stringify(event));

  // Publish to pub/sub
  await redis.publish(`channel:${channel}`, JSON.stringify(event));

  res.json({ ok: true, event });
});

// Replay endpoint
app.get('/events/:channel', async (req, res) => {
  const { channel } = req.params;
  const { count = 50, after = '-' } = req.query;
  const entries = await redis.xrange(`stream:${channel}`, after, '+', 'COUNT', count);
  const events = entries.map(([id, fields]) => ({ id, ...JSON.parse(fields[1]) }));
  res.json(events);
});

app.get('/health', async (_req, res) => {
  const ping = await redis.ping();
  res.json({ status: 'ok', redis: ping, connections: clients.size });
});

const server = createServer(app);
const wss = new WebSocketServer({ server, path: '/ws' });

wss.on('connection', (ws) => {
  const id = Math.random().toString(36).slice(2);
  clients.set(id, { ws, subscriptions: new Set() });

  ws.on('message', (raw) => {
    try {
      const { action, channel } = JSON.parse(raw);
      const client = clients.get(id);
      if (action === 'subscribe' && channel) client.subscriptions.add(channel);
      if (action === 'unsubscribe' && channel) client.subscriptions.delete(channel);
    } catch {}
  });

  ws.on('close', () => clients.delete(id));
});

// Bridge pub/sub to WebSocket clients
redisSub.psubscribe('channel:*');
redisSub.on('pmessage', (_pattern, channelKey, message) => {
  const channel = channelKey.replace('channel:', '');
  for (const { ws, subscriptions } of clients.values()) {
    if (subscriptions.has(channel) && ws.readyState === ws.OPEN) {
      ws.send(message);
    }
  }
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => console.log(`datastream running on port ${PORT}`));
