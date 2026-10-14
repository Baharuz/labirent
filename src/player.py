"""Tüm oyun modları için test edilebilir hareket ve hamle kuralları."""
DIRECTIONS = ((-1, 0), (0, -1), (1, 0), (0, 1))


def validate_board(grid, start, goal):
    if not isinstance(grid, (list, tuple)) or not 3 <= len(grid) <= 51:
        raise ValueError('Harita yüksekliği geçersiz.')
    width = len(grid[0]) if isinstance(grid[0], str) else 0
    if not 3 <= width <= 51 or any(not isinstance(r, str) or len(r) != width or set(r) - {'#', '.'} for r in grid):
        raise ValueError('Harita dikdörtgen olmalı ve yalnızca #/. içermeli.')
    for point in (start, goal):
        if not isinstance(point, (list, tuple)) or len(point) != 2 or any(type(n) is not int for n in point):
            raise ValueError('Konum geçersiz.')
        x, y = point
        if not (0 <= x < width and 0 <= y < len(grid)) or grid[y][x] == '#':
            raise ValueError('Konum geçitte olmalı.')


class Player:
    def __init__(self, start, goal):
        self.position = tuple(start)
        self.goal = tuple(goal)
        self.moves = self.attempts = self.collisions = 0
        self.won = self.position == self.goal

    def move(self, grid, action):
        if type(action) is not int or action not in range(4):
            raise ValueError('Yön 0-3 arasında tam sayı olmalı.')
        if self.won:
            return False
        self.attempts += 1
        dx, dy = DIRECTIONS[action]
        x, y = self.position[0] + dx, self.position[1] + dy
        if not (0 <= y < len(grid) and 0 <= x < len(grid[0])) or grid[y][x] == '#':
            self.collisions += 1
            return False
        self.position = (x, y)
        self.moves += 1
        self.won = self.position == self.goal
        return True
