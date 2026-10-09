import random

ROWS = 15
COLS = 21


def generate_maze(rows=ROWS, cols=COLS):
    """Rastgele, tum gecitleri bagli, dongusuz labirent olusturur."""
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
        nx, ny, dx, dy = random.choice(options)
        grid[y + dy // 2][x + dx // 2] = '.'
        grid[ny][nx] = '.'
        stack.append((nx, ny))
    return [''.join(row) for row in grid], (1, 1), (cols - 2, rows - 2)
