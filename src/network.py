"""Sınırlı mesaj kuyrukları ve arka plan I/O ile yerel TCP bağlantısı."""
import json
import queue
import socket
import threading

PORT = 50505
MAX_MESSAGE = 65536


class Connection:
    def __init__(self):
        self.inbox = queue.Queue(maxsize=256)
        self.outbox = queue.Queue(maxsize=128)
        self.socket = self.listener = None
        self.connected = False
        self.role = None
        self._closed = threading.Event()
        self._lock = threading.Lock()
        self._threads = []

    def _spawn(self, target, *args):
        thread = threading.Thread(target=target, args=args, daemon=True)
        self._threads.append(thread)
        thread.start()

    def _emit(self, message):
        try:
            self.inbox.put_nowait(message)
        except queue.Full:
            self.close()

    def host(self, port=PORT):
        self.role = 'host'
        self._spawn(self._accept, port)

    def _accept(self, port):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            with self._lock:
                if self._closed.is_set():
                    server.close()
                    return
                self.listener = server
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind(('0.0.0.0', port))
            server.listen(1)
            server.settimeout(.2)
            self._emit({'type': 'listening', 'port': server.getsockname()[1]})
            while not self._closed.is_set():
                try:
                    client, _ = server.accept()
                    self._activate(client)
                    break
                except socket.timeout:
                    continue
        except OSError as exc:
            if not self._closed.is_set():
                self._emit({'type': 'error', 'message': str(exc)})
        finally:
            server.close()

    def join(self, address, port=PORT):
        self.role = 'client'
        self._spawn(self._connect, address, port)

    def _connect(self, address, port):
        try:
            sock = socket.create_connection((address, port), timeout=5)
            self._activate(sock)
        except OSError as exc:
            if not self._closed.is_set():
                self._emit({'type': 'error', 'message': str(exc)})

    def _activate(self, sock):
        with self._lock:
            if self._closed.is_set():
                sock.close()
                return
            self.socket = sock
            sock.settimeout(.2)
            self.connected = True
        self._emit({'type': 'connected'})
        self._spawn(self._write)
        self._read(sock)

    def _read(self, sock):
        pending = b''
        try:
            while not self._closed.is_set():
                try:
                    data = sock.recv(4096)
                except socket.timeout:
                    continue
                if not data:
                    break
                pending += data
                while b'\n' in pending:
                    line, pending = pending.split(b'\n', 1)
                    if len(line) > MAX_MESSAGE:
                        raise ValueError('Mesaj boyutu sınırı aşıldı.')
                    message = json.loads(line.decode('utf-8'))
                    if not isinstance(message, dict):
                        raise ValueError('Mesaj JSON nesnesi olmalı.')
                    self._emit(message)
                if len(pending) > MAX_MESSAGE:
                    raise ValueError('Mesaj boyutu sınırı aşıldı.')
        except (ValueError, UnicodeError) as exc:
            self._emit({'type': 'error', 'message': 'Geçersiz ağ mesajı: ' + str(exc)})
        except OSError:
            pass
        finally:
            if not self._closed.is_set():
                self._emit({'type': 'disconnected'})
            self.close()

    def _write(self):
        while not self._closed.is_set():
            try:
                payload = self.outbox.get(timeout=.2)
            except queue.Empty:
                continue
            try:
                self.socket.sendall(payload)
            except OSError:
                self._emit({'type': 'disconnected'})
                self.close()

    def send(self, message):
        if not self.connected or self._closed.is_set():
            return False
        try:
            payload = (json.dumps(message, ensure_ascii=False) + '\n').encode('utf-8')
            if len(payload) > MAX_MESSAGE:
                raise ValueError('Mesaj çok büyük.')
            self.outbox.put_nowait(payload)
            return True
        except (ValueError, TypeError, queue.Full):
            self._emit({'type': 'error', 'message': 'Mesaj gönderilemedi; bağlantı kapatıldı.'})
            self.close()
            return False

    def close(self):
        with self._lock:
            self._closed.set()
            self.connected = False
            for sock in (self.socket, self.listener):
                if sock is not None:
                    try:
                        sock.shutdown(socket.SHUT_RDWR)
                    except OSError:
                        pass
                    sock.close()
