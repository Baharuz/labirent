"""Haritayi bilmeden adim adim kesfeden DFS + Q-Learning ajani."""
from collections import defaultdict

DIRECTIONS = ((-1, 0), (0, -1), (1, 0), (0, 1))
DIRECTION_NAMES = ("Sol", "Yukari", "Sag", "Asagi")


class RLAgent:
    def __init__(self, start, alpha=0.3, gamma=0.9):
        self.position = tuple(start)
        self.visited = {self.position}
        self.known_map = {self.position: "path"}
        self.tried_actions = defaultdict(set)
        self.path_stack = [self.position]
        self.q_table = defaultdict(lambda: [0.0, 0.0, 0.0, 0.0])
        self.alpha = alpha
        self.gamma = gamma
        self.moves = 0
        self.collisions = 0
        self.attempts = 0
        self.total_reward = 0.0
        self.last_reward = 0.0
        self.last_action = "-"
        self.status = "Kesif basliyor"
        self.won = False
        self.finished = False
        self.q_updates = 0

    def update_q(self, state, action, reward, next_state, terminal=False):
        previous = self.q_table[state][action]
        # Bilinen duvarlar gelecek hareket olarak degerlendirilmez.
        valid = [i for i, (dx, dy) in enumerate(DIRECTIONS)
                 if self.known_map.get((next_state[0] + dx, next_state[1] + dy)) != "wall"]
        future = max((self.q_table[next_state][i] for i in valid), default=0.0)
        if terminal:
            future = 0.0
        self.q_table[state][action] = previous + self.alpha * (
            reward + self.gamma * future - previous
        )
        self.q_updates += 1
        self.last_reward = reward
        self.total_reward += reward

    def step(self, grid, goal):
        """Yalnizca BIR hareket denemesi yapar; haritayi onceden okumaz."""
        if self.finished:
            return
        state = self.position
        x, y = state
        available = []
        for action, (dx, dy) in enumerate(DIRECTIONS):
            target = (x + dx, y + dy)
            if action in self.tried_actions[state]:
                continue
            if self.known_map.get(target) == "wall":
                self.tried_actions[state].add(action)
                continue
            if target in self.visited:
                # Ziyaret edilmis gecitler geri izleme ile kullanilir.
                self.tried_actions[state].add(action)
                continue
            available.append(action)

        if available:
            action = max(available, key=lambda a: self.q_table[state][a])
            self.tried_actions[state].add(action)
            self.last_action = DIRECTION_NAMES[action]
            dx, dy = DIRECTIONS[action]
            target = (x + dx, y + dy)
            nx, ny = target
            self.attempts += 1

            # Ortam yalnizca secilen hareketin sonucunu bildirir.
            if not (0 <= ny < len(grid) and 0 <= nx < len(grid[0])) or grid[ny][nx] == '#':
                self.collisions += 1
                self.known_map[target] = "wall"
                self.status = "Duvar kesfedildi"
                self.update_q(state, action, -5.0, state)
                return

            self.position = target
            self.moves += 1
            self.visited.add(target)
            self.known_map[target] = "path"
            self.path_stack.append(target)
            self.status = "Yeni hucre kesfedildi"
            reward = 5.0 - 0.1
            if target == tuple(goal):
                reward += 100.0
                self.won = True
                self.finished = True
                self.status = "Peynir bulundu!"
            self.update_q(state, action, reward, target, terminal=self.won)
            return

        # Bu hucrede kesfedilmemis yon kalmadi; bir adim geri don.
        if len(self.path_stack) == 1:
            self.finished = True
            self.status = "Tum yollar arastirildi"
            return
        child = self.path_stack.pop()
        parent = self.path_stack[-1]
        assert child == state
        assert abs(child[0] - parent[0]) + abs(child[1] - parent[1]) == 1
        self.position = parent
        self.moves += 1
        self.attempts += 1
        self.last_action = "Geri donus"
        self.status = "Cikmazdan geri donuyor"
        self.last_reward = -0.1
        self.total_reward -= 0.1
        # Geri izleme, DFS'in zorunlu hareketidir; Q eylem secimi degildir.

    def get_stats(self):
        return {
            "moves": self.moves,
            "collisions": self.collisions,
            "attempts": self.attempts,
            "explored": len(self.visited),
            "reward": round(self.total_reward, 2),
            "last_reward": round(self.last_reward, 2),
            "position": self.position,
            "action": self.last_action,
            "status": self.status,
            "q_values": tuple(round(v, 2) for v in self.q_table[self.position]),
            "q_updates": self.q_updates,
        }
