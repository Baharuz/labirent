"""Yerel agda iki kisilik TCP oyunu icin mesajlasma katmani."""
import json
import queue
import socket
import threading

PORT = 50505


class Connection:
    def __init__(self):
        self.inbox = queue.Queue()
        self.socket = None
        self.listener = None
        self.role = None
        self.connected = False
        self._closed = False
        self._lock = threading.Lock()

    def host(self, port=PORT):
        self.role = 'host'
        threading.Thread(target=self._accept, args=(port,), daemon=True).start()

    def _accept(self, port):
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.listener = server
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind(('0.0.0.0', port))
            server.listen(1)
            client, _ = server.accept()
            if self._closed:
                client.close()
                return
            self._activate(client)
        except OSError as exc:
            if not self._closed:
                self.inbox.put({'type': 'error', 'message': str(exc)})

    def join(self, address, port=PORT):
        self.role = 'client'
        threading.Thread(target=self._connect, args=(address, port), daemon=True).start()

    def _connect(self, address, port):
        try:
            client = socket.create_connection((address, port), timeout=8)
            self._activate(client)
        except OSError as exc:
            if not self._closed:
                self.inbox.put({'type': 'error', 'message': str(exc)})

    def _activate(self, sock):
        self.socket = sock
        sock.settimeout(None)
        self.connected = True
        self.inbox.put({'type': 'connected'})
        try:
            with sock.makefile('r', encoding='utf-8') as stream:
                for line in stream:
                    if self._closed:
                        break
                    try:
                        message = json.loads(line)
                        if isinstance(message, dict):
                            self.inbox.put(message)
                    except json.JSONDecodeError:
                        continue
        except OSError:
            pass
        finally:
            self.connected = False
            if not self._closed:
                self.inbox.put({'type': 'disconnected'})

    def send(self, message):
        if not self.connected or self.socket is None:
            return False
        payload = (json.dumps(message, ensure_ascii=False) + '\n').encode('utf-8')
        try:
            with self._lock:
                self.socket.sendall(payload)
            return True
        except OSError:
            self.connected = False
            self.inbox.put({'type': 'disconnected'})
            return False

    def close(self):
        self._closed = True
        self.connected = False
        for sock in (self.socket, self.listener):
            if sock is not None:
                try:
                    sock.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass
                try:
                    sock.close()
                except OSError:
                    pass
