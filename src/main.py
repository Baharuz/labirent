import sys
import pygame
from maze import generate_maze, ROWS, COLS

pygame.init()
CELL = 38
TOP = 64
WIDTH, HEIGHT = COLS * CELL, ROWS * CELL + TOP
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Labirent | Fare ve Peynir')
clock = pygame.time.Clock()
font = pygame.font.SysFont('arial', 22, bold=True)
small = pygame.font.SysFont('arial', 18)
large = pygame.font.SysFont('arial', 56, bold=True)
NAVY = (16, 27, 43)
CREAM = (255, 230, 179)
YELLOW = (255, 192, 65)


def label(text, fnt, color, center):
    img = fnt.render(text, True, color)
    screen.blit(img, img.get_rect(center=center))


def button(rect, text, mouse_pos, active=True):
    hovered = rect.collidepoint(mouse_pos) and active
    color = (255, 193, 69) if hovered else ((39, 64, 92) if active else (45, 53, 66))
    pygame.draw.rect(screen, (5, 12, 22), rect.move(0, 4), border_radius=10)
    pygame.draw.rect(screen, color, rect, border_radius=10)
    pygame.draw.rect(screen, (115, 135, 158), rect, 2, border_radius=10)
    label(text, font, NAVY if hovered else (245, 247, 250), rect.center)


def brick(x, y):
    r = pygame.Rect(x, y, CELL, CELL)
    pygame.draw.rect(screen, (86, 35, 27), r)
    pygame.draw.rect(screen, (176, 64, 39), r.inflate(-2, -2))
    pygame.draw.line(screen, (227, 111, 65), (x + 3, y + 3), (x + CELL - 4, y + 3), 2)
    pygame.draw.line(screen, (96, 36, 26), (x + 3, y + CELL // 2), (x + CELL - 3, y + CELL // 2), 3)
    pygame.draw.line(screen, (96, 36, 26), (x + CELL // 2, y + 3), (x + CELL // 2, y + CELL // 2), 2)
    pygame.draw.line(screen, (96, 36, 26), (x + CELL // 4, y + CELL // 2), (x + CELL // 4, y + CELL - 3), 2)


def draw_mouse(cx, cy):
    pygame.draw.line(screen, (209, 146, 157), (cx - 8, cy + 7), (cx - 18, cy + 10), 3)
    pygame.draw.circle(screen, (100, 105, 120), (cx - 9, cy - 9), 9)
    pygame.draw.circle(screen, (100, 105, 120), (cx + 8, cy - 10), 9)
    pygame.draw.circle(screen, (241, 155, 166), (cx - 9, cy - 9), 6)
    pygame.draw.circle(screen, (241, 155, 166), (cx + 8, cy - 10), 6)
    pygame.draw.ellipse(screen, (175, 180, 192), (cx - 13, cy - 11, 27, 29))
    pygame.draw.circle(screen, NAVY, (cx - 5, cy - 2), 2)
    pygame.draw.circle(screen, NAVY, (cx + 6, cy - 2), 2)
    pygame.draw.circle(screen, (238, 128, 142), (cx + 1, cy + 5), 3)


def draw_cheese(cx, cy):
    points = [(cx - 15, cy + 12), (cx + 15, cy + 12), (cx + 12, cy - 12)]
    pygame.draw.polygon(screen, (248, 170, 38), points)
    pygame.draw.polygon(screen, (255, 218, 87), [(cx - 15, cy + 5), (cx + 12, cy - 12), (cx + 15, cy + 5)])
    for dx, dy, radius in [(-2, 2, 4), (8, 6, 3), (7, -5, 2)]:
        pygame.draw.circle(screen, (213, 131, 28), (cx + dx, cy + dy), radius)


def new_game():
    grid, start, goal = generate_maze()
    return grid, list(start), goal, 0, False


grid, player, goal, moves, won = new_game()
mode = 'menu'
buttons = [
    (pygame.Rect(WIDTH // 2 - 170, 225 + i * 67, 340, 52), text)
    for i, text in enumerate(['Manuel Mod', 'RL Modu (Yakinda)', 'Cok Oyunculu (Yakinda)', 'Ayarlar (Yakinda)', 'Cikis'])
]
win_new = pygame.Rect(WIDTH // 2 - 218, HEIGHT // 2 + 85, 205, 53)
win_menu = pygame.Rect(WIDTH // 2 + 13, HEIGHT // 2 + 85, 205, 53)

while True:
    mouse_pos = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if mode == 'game':
                if event.key == pygame.K_ESCAPE:
                    mode = 'menu'
                elif event.key == pygame.K_r:
                    grid, player, goal, moves, won = new_game()
                elif not won:
                    keys = {
                        pygame.K_w: (0, -1), pygame.K_UP: (0, -1),
                        pygame.K_s: (0, 1), pygame.K_DOWN: (0, 1),
                        pygame.K_a: (-1, 0), pygame.K_LEFT: (-1, 0),
                        pygame.K_d: (1, 0), pygame.K_RIGHT: (1, 0),
                    }
                    if event.key in keys:
                        dx, dy = keys[event.key]
                        nx, ny = player[0] + dx, player[1] + dy
                        if 0 <= nx < COLS and 0 <= ny < ROWS and grid[ny][nx] != '#':
                            player = [nx, ny]
                            moves += 1
                            won = tuple(player) == goal
            elif mode == 'menu' and event.key == pygame.K_RETURN:
                grid, player, goal, moves, won = new_game()
                mode = 'game'
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if mode == 'menu':
                if buttons[0][0].collidepoint(event.pos):
                    grid, player, goal, moves, won = new_game()
                    mode = 'game'
                elif buttons[-1][0].collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()
            elif mode == 'game' and won:
                if win_new.collidepoint(event.pos):
                    grid, player, goal, moves, won = new_game()
                elif win_menu.collidepoint(event.pos):
                    mode = 'menu'

    screen.fill(NAVY)
    if mode == 'menu':
        for y in range(0, HEIGHT, CELL):
            for x in range(0, WIDTH, CELL):
                pygame.draw.rect(screen, (23, 37, 55), (x + 2, y + 2, CELL - 4, CELL - 4), border_radius=3)
        label('LABIRENT', large, CREAM, (WIDTH // 2, 100))
        draw_mouse(WIDTH // 2 - 165, 155)
        draw_cheese(WIDTH // 2 + 155, 155)
        for i, (rect, text) in enumerate(buttons):
            button(rect, text, mouse_pos, active=i in (0, 4))
        label('WASD / Ok Tuslari: Hareket   |   R: Yeni Harita   |   ESC: Menu', small,
              (210, 225, 242), (WIDTH // 2, HEIGHT - 35))
    else:
        pygame.draw.rect(screen, (13, 23, 38), (0, 0, WIDTH, TOP))
        label('MANUEL MOD', font, (245, 245, 245), (110, TOP // 2))
        label(f'Hamle: {moves}', font, YELLOW, (WIDTH // 2, TOP // 2))
        label('R: Yeni Harita  |  ESC: Menu', small, (245, 245, 245), (WIDTH - 165, TOP // 2))
        for y, row in enumerate(grid):
            for x, cell in enumerate(row):
                px, py = x * CELL, TOP + y * CELL
                if cell == '#':
                    brick(px, py)
                else:
                    pygame.draw.rect(screen, (157, 158, 155), (px, py, CELL, CELL))
                    pygame.draw.rect(screen, (136, 137, 135), (px, py, CELL, CELL), 1)
        draw_cheese(goal[0] * CELL + CELL // 2, TOP + goal[1] * CELL + CELL // 2)
        draw_mouse(player[0] * CELL + CELL // 2, TOP + player[1] * CELL + CELL // 2)
        if won:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((5, 10, 20, 190))
            screen.blit(overlay, (0, 0))
            panel = pygame.Rect(WIDTH // 2 - 260, HEIGHT // 2 - 125, 520, 300)
            pygame.draw.rect(screen, (18, 29, 47), panel, border_radius=18)
            pygame.draw.rect(screen, (78, 102, 129), panel, 2, border_radius=18)
            label('Kazandin!', large, YELLOW, (WIDTH // 2, HEIGHT // 2 - 65))
            label(f'Peynire {moves} hamlede ulastin!', font, (245, 245, 245),
                  (WIDTH // 2, HEIGHT // 2 + 5))
            draw_mouse(WIDTH // 2 - 32, HEIGHT // 2 + 46)
            draw_cheese(WIDTH // 2 + 32, HEIGHT // 2 + 46)
            button(win_new, 'Yeni Oyun (R)', mouse_pos)
            button(win_menu, 'Ana Menu (ESC)', mouse_pos)
    pygame.display.flip()
    clock.tick(60)
