import asyncio
import json
import sys
import time
from typing import Any

import websockets

def now_ms() -> int:
    return int(time.time() * 1000)

def jdump(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False)

async def read_stdin_line() -> str:
    # чтобы не блокировать event loop
    return (await asyncio.to_thread(sys.stdin.readline)).rstrip("\n")

def fmt_ts(ts: int) -> str:
    t = time.localtime(ts / 1000)
    return time.strftime("%H:%M:%S", t)

def print_help():
    print(
        "\nКоманды:\n"
        "  /users         список онлайн\n"
        "  @nick msg      личное сообщение\n"
        "  /quit          выход\n"
        "  /help          помощь\n"
        "  (любая строка) сообщение в общий чат\n"
    )

async def receiver(ws: websockets.WebSocketClientProtocol):
    async for raw in ws:
        try:
            msg = json.loads(raw)
        except Exception:
            print(f"< [bad json] {raw}")
            continue

        t = msg.get("type")
        ts = msg.get("ts", now_ms())
        prefix = f"< [{fmt_ts(ts)}] "

        if t == "WELCOME":
            print(prefix + f"connected as {msg.get('user')}")
        elif t == "HISTORY":
            items = msg.get("items") or []
            if items:
                print(prefix + f"history ({len(items)}):")
                for it in items:
                    if it.get("type") == "MSG":
                        print(f"    [лобби][{it.get('from')}]: {it.get('text')}")
        elif t == "USERS":
            items = msg.get("items") or []
            print(prefix + "online: " + ", ".join(items))
        elif t == "EVENT":
            print(prefix + f"* {msg.get('name')}: {msg.get('user')}")
        elif t == "MSG":
            print(prefix + f"[лобби][{msg.get('from')}]: {msg.get('text')}")
        elif t == "DM":
            print(prefix + f"[dm][{msg.get('from')} -> you]: {msg.get('text')}")
        elif t == "DM_SENT":
            print(prefix + f"[dm -> {msg.get('to')}]: {msg.get('text')}")
        elif t == "PONG":
            pass
        elif t == "ERROR":
            print(prefix + f"[error {msg.get('code')}]: {msg.get('message')}")
        else:
            print(prefix + f"[{t}] {msg}")

async def sender(ws: websockets.WebSocketClientProtocol):
    print_help()
    while True:
        line = (await read_stdin_line()).strip()
        if not line:
            continue

        if line == "/quit":
            await ws.close()
            return
        if line == "/help":
            print_help()
            continue
        if line == "/users":
            await ws.send(jdump({"type": "USERS"}))
            continue
        if line.startswith("@"):
            # @nick msg
            try:
                nick, text = line[1:].split(" ", 1)
                nick = nick.strip()
                text = text.strip()
            except ValueError:
                print("usage: @nick message")
                continue
            await ws.send(jdump({"type": "DM", "to": nick, "text": text}))
            continue

        await ws.send(jdump({"type": "MSG", "text": line}))

async def main(url: str, user: str):
    async with websockets.connect(url, ping_interval=20, ping_timeout=20, max_size=2**20) as ws:
        await ws.send(jdump({"type": "HELLO", "user": user}))
        await asyncio.gather(receiver(ws), sender(ws))

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--url", default="ws://localhost:8080/ws")
    p.add_argument("--user", required=True)
    args = p.parse_args()
    asyncio.run(main(args.url, args.user))