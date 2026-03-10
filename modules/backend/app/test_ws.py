import asyncio
import os
import random
import string

import pytest
import websockets


BASE_URL = os.getenv("SISAT_BASE_URL", "http://localhost:8010")
ROOM = os.getenv("SISAT_WS_ROOM", "room1")
SEND_INTERVAL_SECONDS = float(os.getenv("SISAT_WS_SEND_INTERVAL", "1"))


def _to_ws_url(base_url: str) -> str:
    if base_url.startswith("https://"):
        return base_url.replace("https://", "wss://", 1)
    if base_url.startswith("http://"):
        return base_url.replace("http://", "ws://", 1)
    return base_url


@pytest.mark.manual
def test_websocket_send_receive_infinite():
    """
    Teste de integracao: conecta no servidor real e envia mensagem indefinidamente.
    Execute apenas quando desejar (ex.: pytest -m manual).
    """
    ws_url = f"{_to_ws_url(BASE_URL)}/ws/connect/send/{ROOM}"

    def _random_text(length: int = 16) -> str:
        alphabet = string.ascii_letters + string.digits
        return "".join(random.choices(alphabet, k=length))

    async def _sender(websocket):
        while True:
            payload = _random_text()
            await websocket.send(payload)
            print(f"sent: {payload} -> {ws_url}", flush=True)
            await asyncio.sleep(SEND_INTERVAL_SECONDS)

    async def _receiver(websocket):
        while True:
            message = await websocket.recv()
            print(f"recv: {message}", flush=True)

    async def _run():
        send_url = f"{_to_ws_url(BASE_URL)}/ws/connect/send/{ROOM}"
        receive_url = f"{_to_ws_url(BASE_URL)}/ws/connect/receive/{ROOM}"
        async with websockets.connect(send_url) as ws_sender:
            async with websockets.connect(receive_url) as ws_receiver:
                await asyncio.gather(
                    _sender(ws_sender),
                    _receiver(ws_receiver),
                )

    asyncio.run(_run())


def main():
    test_websocket_send_receive_infinite()


if __name__ == "__main__":
    main()
