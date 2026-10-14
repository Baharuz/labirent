import random

ROWS = 15
COLS = 21


def generate_maze(rows=ROWS, cols=COLS, seed=None):
    """Rastgele, tum gecitleri bagli, dongusuz labirent olusturur."""
    if any(type(n) is not int or n < 3 or n > 51 for n in (rows, cols)):
        raise ValueError("Boyutlar 3-51 arası tam sayı olmalı.")
    rng = random.Random(seed)
    rows = rows if rows % 2 else rows + 1
    cols = cols if cols % 2 else cols + 1
    grid = [['#'] * cols for _ in range(rows)]
    stack = [(1, 1)]
    grid[1][1] = '.'
    while stack:
        x, y = stack[-1]
        options = []
        for dx, dy in ((0, -2), (0, 2), (-2, 0), (2, 0)):
            nx, ny = x + dx, y + dy
            if 1 <= nx < cols - 1 and 1 <= ny < rows - 1 and grid[ny][nx] == '#':
                options.append((nx, ny, dx, dy))
        if not options:
            stack.pop()
            continue
        nx, ny, dx, dy = rng.choice(options)
        grid[y + dy // 2][x + dx // 2] = '.'
        grid[ny][nx] = '.'
        stack.append((nx, ny))
    return [''.join(row) for row in grid], (1, 1), (cols - 2, rows - 2)
