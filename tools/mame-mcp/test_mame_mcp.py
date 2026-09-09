import json
import socket
import threading
import unittest

from mame_mcp import GdbRemote, MameMcp


def packet(payload: str) -> bytes:
    raw = payload.encode("ascii")
    return b"$" + raw + b"#%02x" % (sum(raw) & 255)


class FakeGdb(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.ready = threading.Event()
        self.port = 0
        self.commands = []
        self.server = socket.socket()
        self.server.bind(("127.0.0.1", 0))
        self.server.listen(1)
        self.port = self.server.getsockname()[1]

    def run(self):
        self.ready.set()
        conn, _ = self.server.accept()
        conn.sendall(packet("T05"))
        conn.recv(1)
        while True:
            data = conn.recv(4096)
            if not data:
                return
            start = data.find(b"$")
            if start < 0:
                continue
            end = data.find(b"#", start)
            payload = data[start + 1:end].decode("ascii")
            self.commands.append(payload)
            conn.sendall(b"+")
            if payload == "qSupported": reply = "PacketSize=fff"
            elif payload.startswith("qXfer:features:read"): reply = "l<target></target>"
            elif payload == "Hc0": reply = "OK"
            elif payload == "m100,4": reply = "01020304"
            else: reply = "OK"
            conn.sendall(packet(reply))


class GdbMcpTests(unittest.TestCase):
    def test_remote_request_and_checksum(self):
        try:
            fake = FakeGdb()
        except PermissionError as exc:
            self.skipTest(f"socket creation is unavailable in this environment: {exc}")
        fake.start(); fake.ready.wait()
        gdb = GdbRemote("127.0.0.1", fake.port)
        gdb.connect()
        self.assertEqual(gdb.request("m100,4"), "01020304")
        gdb.close()
        self.assertEqual(fake.commands, ["m100,4"])

    def test_address_parsing_and_limits(self):
        server = MameMcp()
        with self.assertRaisesRegex(Exception, "length"):
            server._address_length({"address": "0x10", "length": -1})
        self.assertEqual(server._address_length({"address": "0x10", "length": "4"}), (16, 4))


if __name__ == "__main__":
    unittest.main()
