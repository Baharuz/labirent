import os
import sys
import time
import queue
import socket
import unittest
from collections import deque
from pathlib import Path

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from maze import generate_maze
from player import Player
from rl_agent import RLAgent
from network import Connection, MAX_MESSAGE
from multiplayer import MultiplayerSession


def path_to_goal(grid, start, goal):
    todo = deque([(tuple(start), [])])
    seen = {tuple(start)}
    while todo:
        (x, y), actions = todo.popleft()
        if (x, y) == tuple(goal):
            return actions
        for action, (dx, dy) in enumerate(((-1, 0), (0, -1), (1, 0), (0, 1))):
            point = x + dx, y + dy
            if 0 <= point[1] < len(grid) and 0 <= point[0] < len(grid[0]) and point not in seen and grid[point[1]][point[0]] != '#':
                seen.add(point)
                todo.append((point, actions + [action]))
    raise AssertionError('Hedefe yol bulunamadı.')


def wait_until(predicate, pump=lambda: None, seconds=4):
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        pump()
        if predicate():
            return
        time.sleep(.005)
    raise AssertionError('Zaman aşımı')


class GameTests(unittest.TestCase):
    def test_manual_wall_and_win_counters(self):
        grid = ['#####', '#...#', '#####']
        player = Player((1, 1), (3, 1))
        self.assertFalse(player.move(grid, 0))
        self.assertEqual((player.moves, player.attempts, player.collisions), (0, 1, 1))
        player.move(grid, 2)
        player.move(grid, 2)
        self.assertTrue(player.won)
        player.move(grid, 0)
        self.assertEqual((player.moves, player.attempts, player.collisions), (2, 3, 1))

    def test_invalid_direction(self):
        p = Player((1, 1), (2, 1))
        for action in (-1, 4, True, '2'):
            with self.assertRaises(ValueError):
                p.move(['####', '#..#', '####'], action)

    def test_generated_mazes_solvable(self):
        for seed in range(100):
            g, s, goal = generate_maze(seed=seed)
            self.assertTrue(path_to_goal(g, s, goal))

    def test_computer_finds_goal_and_counts(self):
        for seed in range(100):
            g, s, goal = generate_maze(seed=seed)
            a = RLAgent(s)
            for _ in range(5000):
                a.step(g, goal)
                if a.finished:
                    break
            self.assertTrue(a.won, seed)
            self.assertEqual(a.attempts, a.moves + a.collisions)
            self.assertEqual(a.position, goal)

    def test_seed_and_dimension_validation(self):
        self.assertEqual(generate_maze(seed=17), generate_maze(seed=17))
        for size in (0, 1, 2, -1, 52, True, 4.5):
            with self.assertRaises(ValueError):
                generate_maze(size, 21)

    def test_start_is_goal(self):
        g, s, goal = generate_maze(3, 3)
        self.assertTrue(Player(s, goal).won)
        a = RLAgent(s)
        a.step(g, goal)
        self.assertTrue(a.won)
        self.assertEqual(a.moves, 0)


class NetworkTests(unittest.TestCase):
    def setUp(self):
        self.host = Connection()
        self.client = Connection()
        self.host.host(0)
        info = self.host.inbox.get(timeout=3)
        self.assertEqual(info['type'], 'listening')
        self.port = info['port']
        self.hs = MultiplayerSession(self.host, 'host')
        self.cs = MultiplayerSession(self.client, 'client')

    def tearDown(self):
        self.host.close()
        self.client.close()
        for connection in (self.host, self.client):
            for thread in connection._threads:
                thread.join(timeout=1)

    def pump(self):
        self.hs.poll()
        self.cs.poll()

    def connect(self):
        self.client.join('127.0.0.1', self.port)
        wait_until(lambda: self.hs.ready and self.cs.ready, self.pump)

    def test_handshake_and_same_board(self):
        self.hs.move(2)
        self.assertFalse(self.hs.ready)
        self.connect()
        self.assertEqual(self.hs.grid, self.cs.grid)
        self.assertEqual(self.hs.goal, self.cs.goal)
        self.assertEqual(self.hs.round_id, self.cs.round_id)

    def test_real_tcp_client_win_rematch_and_disconnect(self):
        self.connect()
        actions = path_to_goal(self.hs.grid, self.hs.start, self.hs.goal)
        for i, action in enumerate(actions):
            self.cs.move(action)
            wait_until(lambda: self.cs.players[1].moves == i + 1, self.pump)
        self.assertEqual(self.cs.winner, 1)
        self.assertEqual(self.hs.winner, 1)
        self.assertEqual(self.cs.players[1].moves, len(actions))
        self.hs.move(2)
        self.assertEqual(self.hs.players[0].moves, 0)
        old_round = self.hs.round_id
        self.hs.new_round()
        wait_until(lambda: self.cs.round_id == old_round + 1 and self.cs.ready, self.pump)
        self.assertEqual(self.cs.players[1].moves, 0)
        self.hs.handle({'type': 'move', 'round': old_round, 'direction': 2})
        self.assertEqual(self.hs.players[1].moves, 0)
        self.client.close()
        wait_until(lambda: not self.host.connected, self.pump)
        self.pump()
        self.assertFalse(self.hs.ready)

    def test_host_wall_counts_both_peers(self):
        self.connect()
        self.hs.move(0)
        wait_until(lambda: self.cs.players[0].collisions == 1, self.pump)
        self.assertEqual(self.cs.players[0].moves, 0)
        self.assertEqual(self.cs.players[0].attempts, 1)

    def test_invalid_message_disconnects_without_crash(self):
        self.connect()
        self.client.send({'type': 'move', 'round': self.hs.round_id, 'direction': True})
        wait_until(lambda: not self.host.connected, self.pump)
        self.assertIn('Geçersiz', self.hs.message)

    def test_invalid_state_rejected(self):
        self.connect()
        broken = self.hs._state()
        broken['players'] = [[0, 0], [1, 1]]
        self.host.send(broken)
        wait_until(lambda: not self.client.connected, self.pump)
        self.assertFalse(self.cs.ready)

    def test_oversized_frame_closes_connection(self):
        raw = socket.create_connection(('127.0.0.1', self.port), timeout=2)
        try:
            raw.sendall(b'x' * (MAX_MESSAGE + 10))
            wait_until(lambda: self.host._closed.is_set())
        finally:
            raw.close()

    def test_cancelled_connection_cannot_activate(self):
        self.client.close()
        a, b = socket.socketpair()
        try:
            self.client._activate(a)
            self.assertFalse(self.client.connected)
            self.assertEqual(a.fileno(), -1)
        finally:
            b.close()

    def test_close_pending_listener_releases_port(self):
        self.host.close()
        for thread in self.host._threads:
            thread.join(timeout=1)
        with socket.socket() as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('0.0.0.0', self.port))


class ScreenTests(unittest.TestCase):
    def test_screens_events_and_restart(self):
        import pygame
        from main import GameApplication
        app = GameApplication()
        try:
            for mode in ('menu', 'settings', 'network_menu'):
                app.mode = mode
                app.draw()
            app.start_game()
            initial = app.grid[:]
            app.event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT, unicode=''))
            self.assertEqual(app.player.collisions, 1)
            for action in path_to_goal(app.grid, app.start, app.goal):
                app.player.move(app.grid, action)
            app.draw()
            self.assertTrue(app.player.won)
            app.action('same')
            self.assertEqual(app.grid, initial)
            self.assertEqual(app.player.moves, 0)
            app.start_game(True)
            app.draw()
            app.action('pause')
            position = app.agent.position
            app.update()
            self.assertEqual(app.agent.position, position)
            app.action('menu')
            self.assertEqual(app.mode, 'menu')
        finally:
            app.menu()
            pygame.quit()


if __name__ == '__main__':
    unittest.main()
