"""Pygame çizim yardımcıları; import sırasında pencere açılmaz."""
import pygame
from maze import ROWS, COLS

CELL = 38
TOP = 64
PANEL = 290
MAZE_WIDTH = COLS * CELL
WIDTH = MAZE_WIDTH + PANEL
HEIGHT = ROWS * CELL + TOP
NAVY = (16, 27, 43)
CREAM = (255, 230, 179)
YELLOW = (255, 192, 65)
WHITE = (240, 244, 250)
MUTED = (169, 184, 204)


def initialize():
    global screen, font, small, tiny, large
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Labirent | Fare ve Peynir")
    font = pygame.font.SysFont('arial', 22, bold=True)
    small = pygame.font.SysFont('arial', 17)
    tiny = pygame.font.SysFont('arial', 15)
    large = pygame.font.SysFont('arial', 52, bold=True)

def label(text, fnt, color, center):
    image = fnt.render(str(text), True, color)
    screen.blit(image, image.get_rect(center=center))


def left_text(text, x, y, fnt=None, color=WHITE):
    screen.blit((fnt or small).render(str(text), True, color), (x, y))


def button(rect, text, mouse_pos, active=True):
    hovered = rect.collidepoint(mouse_pos) and active
    color = YELLOW if hovered else ((39, 64, 92) if active else (45, 53, 66))
    pygame.draw.rect(screen, (5, 12, 22), rect.move(0, 4), border_radius=10)
    pygame.draw.rect(screen, color, rect, border_radius=10)
    pygame.draw.rect(screen, (115, 135, 158), rect, 2, border_radius=10)
    label(text, font, NAVY if hovered else WHITE, rect.center)


def brick(x, y):
    r = pygame.Rect(x, y, CELL, CELL)
    pygame.draw.rect(screen, (86, 35, 27), r)
    pygame.draw.rect(screen, (176, 64, 39), r.inflate(-2, -2))
    pygame.draw.line(screen, (227, 111, 65), (x + 3, y + 3), (x + CELL - 4, y + 3), 2)
    pygame.draw.line(screen, (96, 36, 26), (x + 3, y + CELL // 2), (x + CELL - 3, y + CELL // 2), 3)
    pygame.draw.line(screen, (96, 36, 26), (x + CELL // 2, y + 3), (x + CELL // 2, y + CELL // 2), 2)
    pygame.draw.line(screen, (96, 36, 26), (x + CELL // 4, y + CELL // 2), (x + CELL // 4, y + CELL - 3), 2)


def draw_mouse(cx, cy, color=None):
    pygame.draw.line(screen, (209, 146, 157), (cx - 8, cy + 7), (cx - 18, cy + 10), 3)
    for dx, dy in ((-9, -9), (8, -10)):
        pygame.draw.circle(screen, (100, 105, 120), (cx + dx, cy + dy), 9)
        pygame.draw.circle(screen, (241, 155, 166), (cx + dx, cy + dy), 6)
    pygame.draw.ellipse(screen, color or (175, 180, 192), (cx - 13, cy - 11, 27, 29))
    pygame.draw.circle(screen, NAVY, (cx - 5, cy - 2), 2)
    pygame.draw.circle(screen, NAVY, (cx + 6, cy - 2), 2)
    pygame.draw.circle(screen, (238, 128, 142), (cx + 1, cy + 5), 3)


def draw_cheese(cx, cy):
    points = [(cx - 15, cy + 12), (cx + 15, cy + 12), (cx + 12, cy - 12)]
    pygame.draw.polygon(screen, (248, 170, 38), points)
    pygame.draw.polygon(screen, (255, 218, 87), [(cx - 15, cy + 5), (cx + 12, cy - 12), (cx + 15, cy + 5)])
    for dx, dy, radius in ((-2, 2, 4), (8, 6, 3), (7, -5, 2)):
        pygame.draw.circle(screen, (213, 131, 28), (cx + dx, cy + dy), radius)


def draw_maze(grid, player, goal, agent=None, other=None, trail=None):
    """Oyuncu tüm labirenti görür; RL ajanının bilgisi değişmez."""
    for y, row in enumerate(grid):
        for x, cell in enumerate(row):
            px, py = x * CELL, TOP + y * CELL
            if cell == '#':
                brick(px, py)
                continue
            pygame.draw.rect(screen, (157, 158, 155), (px, py, CELL, CELL))
            pygame.draw.rect(screen, (106, 115, 118), (px, py, CELL, CELL), 1)

    if trail:
        for tx, ty in trail:
            pygame.draw.circle(screen, (234, 186, 75),
                               (tx * CELL + CELL // 2, TOP + ty * CELL + CELL // 2), 4)
    # Peynir oyuncuya bastan gorunur; RL ajanina konumu aciklanmaz.
    draw_cheese(goal[0] * CELL + CELL // 2, TOP + goal[1] * CELL + CELL // 2)
    if other is not None:
        draw_mouse(other[0] * CELL + CELL // 2, TOP + other[1] * CELL + CELL // 2, (111, 187, 239))
    draw_mouse(player[0] * CELL + CELL // 2, TOP + player[1] * CELL + CELL // 2)


