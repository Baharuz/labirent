"""Oda sahibi hareketleri doğrular; iki oyuncu aynı turu paylaşır."""
import queue
from maze import generate_maze, ROWS, COLS
from player import Player, validate_board


class MultiplayerSession:
    def __init__(self, connection, role):
        self.connection = connection
        self.role = role
        self.grid = None
        self.start = self.goal = None
        self.players = []
        self.winner = None
        self.ready = False
        self.round_id = 0
        self.message = 'Oyuncu bekleniyor...' if role == 'host' else 'Bağlanıyor...'

    def _send(self, message):
        if not self.connection.send(message):
            self.ready = False
            self.message = 'Gönderim başarısız. Menüden yeniden bağlanın.'
            return False
        return True

    def new_round(self):
        if self.role != 'host' or not self.connection.connected:
            return False
        self.grid, self.start, self.goal = generate_maze()
        self.round_id += 1
        self.players = [Player(self.start, self.goal), Player(self.start, self.goal)]
        self.winner = None
        self.ready = False
        self.message = 'Diğer oyuncunun haritayı alması bekleniyor...'
        return self._send({'type': 'init', 'round': self.round_id, 'grid': self.grid,
                           'start': self.start, 'goal': self.goal})

    def _state(self):
        return {'type': 'state', 'round': self.round_id,
                'players': [list(p.position) for p in self.players],
                'moves': [p.moves for p in self.players],
                'attempts': [p.attempts for p in self.players],
                'collisions': [p.collisions for p in self.players], 'winner': self.winner}

    def move(self, action):
        if not self.ready or not self.connection.connected or self.winner is not None:
            return
        if self.role == 'client':
            self._send({'type': 'move', 'round': self.round_id, 'direction': action})
        else:
            self._move(0, action)

    def _move(self, index, action):
        if not self.ready or self.winner is not None:
            return
        self.players[index].move(self.grid, action)
        if self.players[index].won:
            self.winner = index
        self._send(self._state())

    def poll(self):
        for _ in range(64):
            try:
                message = self.connection.inbox.get_nowait()
            except queue.Empty:
                break
            try:
                self.handle(message)
            except (ValueError, KeyError, TypeError, IndexError):
                self.ready = False
                self.message = 'Geçersiz oyun verisi. Menüden yeniden bağlanın.'
                self.connection.close()
                break
        if not self.connection.connected:
            self.ready = False

    def handle(self, msg):
        kind = msg.get('type')
        if kind == 'connected':
            self.message = 'Harita hazırlanıyor...'
            if self.role == 'host':
                self.new_round()
            return
        if kind == 'listening':
            return
        if kind in ('error', 'disconnected'):
            self.ready = False
            self.message = ('Bağlantı hatası: ' + str(msg.get('message', ''))) if kind == 'error' else 'Bağlantı kesildi. Menüden yeniden bağlanın.'
            return
        if kind not in ('init', 'ready', 'state', 'move'):
            raise ValueError('Bilinmeyen mesaj.')
        if type(msg.get('round')) is not int or msg['round'] < 1:
            raise ValueError('Tur kimliği geçersiz.')
        if kind == 'init' and self.role == 'client':
            if msg['round'] <= self.round_id:
                return
            validate_board(msg['grid'], msg['start'], msg['goal'])
            if len(msg['grid']) != ROWS or len(msg['grid'][0]) != COLS:
                raise ValueError('Harita boyutu desteklenmiyor.')
            self.grid = msg['grid']
            self.start, self.goal = tuple(msg['start']), tuple(msg['goal'])
            self.players = [Player(self.start, self.goal), Player(self.start, self.goal)]
            self.round_id = msg['round']
            self.winner = None
            self.ready = False
            self.message = 'Başlama onayı bekleniyor...'
            self._send({'type': 'ready', 'round': self.round_id})
            return
        if msg['round'] != self.round_id:
            return
        if kind == 'ready' and self.role == 'host':
            self.ready = True
            self.message = 'Yarış başladı!'
            self._send(self._state())
        elif kind == 'move' and self.role == 'host':
            if type(msg.get('direction')) is not int or msg['direction'] not in range(4):
                raise ValueError('Yön geçersiz.')
            self._move(1, msg['direction'])
        elif kind == 'state' and self.role == 'client':
            if self.grid is None:
                raise ValueError('Harita henüz yok.')
            positions = msg['players']
            if not isinstance(positions, list) or len(positions) != 2:
                raise ValueError('İki oyuncu gerekli.')
            for position in positions:
                validate_board(self.grid, position, self.goal)
            for key in ('moves', 'attempts', 'collisions'):
                values = msg[key]
                if not isinstance(values, list) or len(values) != 2 or any(type(v) is not int or v < 0 for v in values):
                    raise ValueError('Sayaç geçersiz.')
            winner = msg['winner']
            if winner is not None and (type(winner) is not int or winner not in (0, 1) or tuple(positions[winner]) != self.goal):
                raise ValueError('Kazanan geçersiz.')
            for i, player in enumerate(self.players):
                if msg['attempts'][i] != msg['moves'][i] + msg['collisions'][i]:
                    raise ValueError('Sayaçlar tutarsız.')
                player.position = tuple(positions[i])
                player.moves, player.attempts, player.collisions = msg['moves'][i], msg['attempts'][i], msg['collisions'][i]
                player.won = winner == i
            self.winner = winner
            self.ready = True
            self.message = 'Yarış başladı!'
        else:
            raise ValueError('Role uygun olmayan mesaj.')
