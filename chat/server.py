import asyncio
import json
import re
import time
from collections import deque
from dataclasses import dataclass
from typing import Dict, Deque, Any
import argparse
import websockets
from websockets.server import WebSocketServerProtocol

USERNAME_RE = re.compile(r"^[a-zA-Z0-9_]{2,20}$")


def now_ms() -> int:
    return int(time.time() * 1000)


def jdump(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False)


async def jsend(ws: WebSocketServerProtocol, obj: Any) -> None:
    await ws.send(jdump(obj))


@dataclass
class Client:
    user: str
    ws: WebSocketServerProtocol


class ChatServer:
    def __init__(self, history_size: int = 50):
        self._lock = asyncio.Lock()
        self._users: Dict[str, Client] = {}
        self._history: Deque[dict] = deque(maxlen=history_size)

    async def _broadcast(self, obj: dict) -> None:
        msg = jdump(obj)
        async with self._lock:
            clients = list(self._users.values())

        # отправляем без удержания lock
        dead = []
        for c in clients:
            try:
                await c.ws.send(msg)
            except Exception:
                dead.append(c.user)

        if dead:
            async with self._lock:
                for u in dead:
                    self._users.pop(u, None)

    async def _send_users_list(self, ws: WebSocketServerProtocol) -> None:
        async with self._lock:
            items = sorted(self._users.keys())
        await jsend(ws, {"type": "USERS", "items": items, "ts": now_ms()})

    async def _broadcast_users_list(self) -> None:
        async with self._lock:
            items = sorted(self._users.keys())
        await self._broadcast({"type": "USERS", "items": items, "ts": now_ms()})

    async def handler(self, ws: WebSocketServerProtocol):
        # 1) HELLO handshake
        try:
            raw = await asyncio.wait_for(ws.recv(), timeout=10)
        except Exception:
            await ws.close()
            return

        try:
            msg = json.loads(raw)
        except Exception:
            await jsend(ws, {"type": "ERROR", "code": "BAD_JSON", "message": "Invalid JSON"})
            await ws.close()
            return

        if msg.get("type") != "HELLO" or not isinstance(msg.get("user"), str):
            await jsend(ws, {"type": "ERROR", "code": "NO_HELLO", "message": "First message must be HELLO"})
            await ws.close()
            return

        user = msg["user"].strip()
        if not USERNAME_RE.match(user):
            await jsend(ws, {
                "type": "ERROR",
                "code": "BAD_USERNAME",
                "message": "Username must be 2-20 chars: letters/digits/_",
            })
            await ws.close()
            return

        async with self._lock:
            if user in self._users:
                await jsend(ws, {"type": "ERROR", "code": "USER_TAKEN", "message": "Username is already online"})
                await ws.close()
                return
            self._users[user] = Client(user=user, ws=ws)
            history_snapshot = list(self._history)

        await jsend(ws, {"type": "WELCOME", "user": user, "ts": now_ms()})
        await jsend(ws, {"type": "HISTORY", "items": history_snapshot, "ts": now_ms()})

        await self._broadcast({"type": "EVENT", "name": "USER_JOIN", "user": user, "ts": now_ms()})
        await self._broadcast_users_list()

        # 2) main loop
        try:
            async for raw in ws:
                try:
                    msg = json.loads(raw)
                except Exception:
                    await jsend(ws, {"type": "ERROR", "code": "BAD_JSON", "message": "Invalid JSON"})
                    continue

                mtype = msg.get("type")

                if mtype == "MSG":
                    text = (msg.get("text") or "").strip()
                    if not text:
                        continue
                    out = {"type": "MSG", "from": user, "text": text, "ts": now_ms()}
                    async with self._lock:
                        self._history.append(out)
                    await self._broadcast(out)

                elif mtype == "DM":
                    to = (msg.get("to") or "").strip()
                    text = (msg.get("text") or "").strip()
                    if not to or not text:
                        await jsend(ws, {"type": "ERROR", "code": "BAD_DM", "message": "DM requires to+text"})
                        continue

                    async with self._lock:
                        recipient = self._users.get(to)

                    if not recipient:
                        await jsend(ws, {"type": "ERROR", "code": "USER_NOT_FOUND", "message": f"{to} is offline"})
                        continue

                    out = {"type": "DM", "from": user, "to": to, "text": text, "ts": now_ms()}
                    # получателю
                    await jsend(recipient.ws, out)
                    # отправителю (чтобы видеть у себя подтверждение)
                    await jsend(ws, {"type": "DM_SENT", "to": to, "text": text, "ts": out["ts"]})

                elif mtype == "USERS":
                    await self._send_users_list(ws)

                elif mtype == "PING":
                    await jsend(ws, {"type": "PONG", "ts": now_ms()})

                else:
                    await jsend(ws, {"type": "ERROR", "code": "UNKNOWN_TYPE", "message": f"Unknown type: {mtype}"})

        finally:
            # cleanup on disconnect
            async with self._lock:
                self._users.pop(user, None)

            await self._broadcast({"type": "EVENT", "name": "USER_LEAVE", "user": user, "ts": now_ms()})
            await self._broadcast_users_list()


async def main(host: str = "0.0.0.0", port: int = 8080):
    server = ChatServer(history_size=50)
    print(f"WS server listening on ws://{host}:{port}/ws")

    async def _handler(ws: WebSocketServerProtocol):
        await server.handler(ws)

    async with websockets.serve(
        _handler,
        host,
        port,
        ping_interval=20,
        ping_timeout=20,
        max_size=2**20,
    ):
        await asyncio.Future()


if __name__ == "__main__":
    

    p = argparse.ArgumentParser()
    p.add_argument("--host", default="0.0.0.0")
    p.add_argument("--port", type=int, default=8080)
    args = p.parse_args()

    asyncio.run(main(args.host, args.port))