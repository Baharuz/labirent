import sys
import queue
import socket
from network import Connection, PORT
import pygame
from maze import generate_maze, ROWS, COLS
from rl_agent import RLAgent, DIRECTION_NAMES

pygame.init()
CELL = 38
TOP = 64
PANEL = 290
MAZE_WIDTH = COLS * CELL
WIDTH = MAZE_WIDTH + PANEL
HEIGHT = ROWS * CELL + TOP
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Labirent | Fare ve Peynir')
clock = pygame.time.Clock()
font = pygame.font.SysFont('arial', 22, bold=True)
small = pygame.font.SysFont('arial', 17)
tiny = pygame.font.SysFont('arial', 15)
large = pygame.font.SysFont('arial', 52, bold=True)
NAVY = (16, 27, 43)
CREAM = (255, 230, 179)
YELLOW = (255, 192, 65)
WHITE = (240, 244, 250)
MUTED = (169, 184, 204)


def label(text, fnt, color, center):
    image = fnt.render(str(text), True, color)
    screen.blit(image, image.get_rect(center=center))


def left_text(text, x, y, fnt=small, color=WHITE):
    screen.blit(fnt.render(str(text), True, color), (x, y))


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


def new_game():
    grid, start, goal = generate_maze()
    return grid, list(start), goal, 0, False


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


def draw_panel(agent, speed, paused):
    x = MAZE_WIDTH + 17
    pygame.draw.rect(screen, (21, 34, 52), (MAZE_WIDTH, 0, PANEL, HEIGHT))
    pygame.draw.line(screen, (79, 103, 131), (MAZE_WIDTH, 0), (MAZE_WIDTH, HEIGHT), 2)
    left_text('CANLI OGRENME', x, 24, font, YELLOW)
    left_text('Q-Learning + DFS', x, 57, tiny, MUTED)
    stats = agent.get_stats()
    rows = [
        ('Hamle', stats['moves']),
        ('Duvara carpma', stats['collisions']),
        ('Hareket denemesi', stats['attempts']),
        ('Kesfedilen hucre', stats['explored']),
        ('Toplam odul', stats['reward']),
        ('Son odul', stats['last_reward']),
        ('Q guncellemesi', stats['q_updates']),
        ('Konum', str(stats['position'])),
        ('Son hareket', stats['action']),
    ]
    y = 97
    for name, value in rows:
        left_text(name, x, y, tiny, MUTED)
        value_img = small.render(str(value), True, WHITE)
        screen.blit(value_img, (WIDTH - 14 - value_img.get_width(), y - 2))
        y += 32
    pygame.draw.line(screen, (67, 88, 111), (x, y + 1), (WIDTH - 14, y + 1))
    y += 16
    left_text('Q DEGERLERI', x, y, small, YELLOW)
    y += 32
    for direction, value in zip(DIRECTION_NAMES, stats['q_values']):
        left_text(direction, x + 6, y, tiny, MUTED)
        value_img = small.render(f'{value:+.2f}', True, WHITE)
        screen.blit(value_img, (WIDTH - 17 - value_img.get_width(), y - 2))
        y += 27
    y += 6
    pygame.draw.line(screen, (67, 88, 111), (x, y), (WIDTH - 14, y))
    y += 13
    left_text('Durum:', x, y, tiny, YELLOW)
    y += 23
    left_text(stats['status'], x, y, tiny, WHITE)
    y += 32
    left_text(f'Hiz: {speed} adim/sn', x, y, tiny, MUTED)
    y += 23
    left_text('DURAKLATILDI' if paused else ('TAMAMLANDI' if agent.finished else 'OGRENIYOR'),
              x, y, tiny, YELLOW)
    left_text('SPACE: Dur / Devam', x, HEIGHT - 83, tiny, MUTED)
    left_text('+ / -: Hiz   R: Yeni', x, HEIGHT - 59, tiny, MUTED)
    left_text('ESC: Ana menu', x, HEIGHT - 35, tiny, MUTED)


def draw_win(moves, mouse_pos, rl=False):
    overlay = pygame.Surface((MAZE_WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((5, 10, 20, 190))
    screen.blit(overlay, (0, 0))
    cx = MAZE_WIDTH // 2
    panel = pygame.Rect(cx - 260, HEIGHT // 2 - 125, 520, 300)
    pygame.draw.rect(screen, (18, 29, 47), panel, border_radius=18)
    pygame.draw.rect(screen, (78, 102, 129), panel, 2, border_radius=18)
    label('Peynir Bulundu!' if rl else 'Kazandin!', large, YELLOW, (cx, HEIGHT // 2 - 65))
    label(f'{moves} hamlede hedefe ulasildi!', font, WHITE, (cx, HEIGHT // 2 + 5))
    draw_mouse(cx - 32, HEIGHT // 2 + 46)
    draw_cheese(cx + 32, HEIGHT // 2 + 46)
    button(win_new, 'Yeni Oyun (R)', mouse_pos)
    button(win_menu, 'Ana Menu (ESC)', mouse_pos)


grid, player, goal, moves, won = new_game()
mode = 'menu'
agent = None
rl_paused = False
rl_speed = 8
last_rl_step = 0
show_trail = True
trail = []
connection = None
network_message = ''
join_ip = '127.0.0.1'
mp_players = [[1, 1], [1, 1]]
mp_moves = [0, 0]
mp_winner = None
mp_role = None

buttons = [
    (pygame.Rect(MAZE_WIDTH // 2 - 170, 225 + i * 67, 340, 52), text)
    for i, text in enumerate(('Manuel Mod', 'RL Modu', 'Cok Oyunculu', 'Ayarlar', 'Cikis'))
]
win_new = pygame.Rect(MAZE_WIDTH // 2 - 218, HEIGHT // 2 + 85, 205, 53)
win_menu = pygame.Rect(MAZE_WIDTH // 2 + 13, HEIGHT // 2 + 85, 205, 53)


def start_game(rl=False):
    global grid, player, goal, moves, won, agent, mode, rl_paused, last_rl_step
    grid, player, goal, moves, won = new_game()
    agent = RLAgent(tuple(player)) if rl else None
    mode = 'rl' if rl else 'game'
    rl_paused = False
    last_rl_step = pygame.time.get_ticks()
    trail.clear()



def close_network():
    global connection
    if connection is not None:
        connection.close()
    connection = None


def begin_multiplayer(host):
    global mode, connection, network_message, mp_role, mp_winner
    global grid, player, goal, moves, won, mp_players, mp_moves
    close_network()
    connection = Connection()
    mp_role = 'host' if host else 'client'
    mp_winner = None
    mp_players = [[1, 1], [1, 1]]
    mp_moves = [0, 0]
    if host:
        grid, player, goal, moves, won = new_game()
        connection.host()
        network_message = f'Oyuncu bekleniyor (TCP {PORT})...'
    else:
        connection.join(join_ip.strip())
        network_message = f'Baglaniyor: {join_ip}:{PORT}'
    mode = 'multiplayer'


def send_state():
    if connection is not None and connection.connected:
        connection.send({
            'type': 'state', 'players': mp_players,
            'moves': mp_moves, 'winner': mp_winner,
        })


def multiplayer_move(index, dx, dy):
    global mp_winner
    if mp_winner is not None or not grid:
        return
    x, y = mp_players[index]
    nx, ny = x + dx, y + dy
    if 0 <= ny < len(grid) and 0 <= nx < len(grid[0]) and grid[ny][nx] != '#':
        mp_players[index] = [nx, ny]
        mp_moves[index] += 1
        if (nx, ny) == tuple(goal):
            mp_winner = index
        send_state()


def handle_network():
    global network_message, grid, goal, mp_players, mp_moves, mp_winner
    if connection is None:
        return
    for _ in range(40):
        try:
            msg = connection.inbox.get_nowait()
        except queue.Empty:
            break
        kind = msg.get('type')
        if kind == 'connected':
            network_message = 'Baglandi! Peynir icin yarisa baslayin.'
            if mp_role == 'host':
                connection.send({'type': 'init', 'grid': grid, 'goal': goal})
                send_state()
        elif kind == 'init' and mp_role == 'client':
            grid = msg['grid']
            goal = tuple(msg['goal'])
        elif kind == 'move' and mp_role == 'host':
            direction = msg.get('direction')
            if isinstance(direction, int) and 0 <= direction < 4:
                multiplayer_move(1, *[(-1, 0), (0, -1), (1, 0), (0, 1)][direction])
        elif kind == 'state' and mp_role == 'client':
            mp_players = msg['players']
            mp_moves = msg['moves']
            mp_winner = msg['winner']
        elif kind == 'error':
            network_message = 'Baglanti hatasi: ' + str(msg.get('message', ''))[:65]
        elif kind == 'disconnected':
            network_message = 'Diger oyuncunun baglantisi kesildi.'


menu_rect = pygame.Rect(18, HEIGHT - 57, 150, 40)
settings_speed_minus = pygame.Rect(MAZE_WIDTH // 2 - 70, 228, 55, 48)
settings_speed_plus = pygame.Rect(MAZE_WIDTH // 2 + 90, 228, 55, 48)
settings_trail = pygame.Rect(MAZE_WIDTH // 2 - 120, 324, 240, 52)
host_button = pygame.Rect(MAZE_WIDTH // 2 - 240, 200, 225, 60)
join_button = pygame.Rect(MAZE_WIDTH // 2 + 15, 200, 225, 60)
ip_rect = pygame.Rect(MAZE_WIDTH // 2 - 155, 300, 310, 54)


def draw_submenu_title(title):
    label(title, large, CREAM, (MAZE_WIDTH // 2, 110))
    button(menu_rect, 'Ana Menu', pygame.mouse.get_pos())



while True:
    mouse_pos = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            close_network()
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if mode in ('multiplayer', 'mp_menu', 'settings') and event.key == pygame.K_ESCAPE:
                close_network()
                mode = 'menu'
            elif mode == 'mp_menu':
                if event.key == pygame.K_BACKSPACE:
                    join_ip = join_ip[:-1]
                elif event.unicode and event.unicode in '0123456789.abcdefghijklmnopqrstuvwxyz-':
                    join_ip = (join_ip + event.unicode)[:60]
            elif mode == 'multiplayer':
                keys = {
                    pygame.K_w: 1, pygame.K_UP: 1,
                    pygame.K_a: 0, pygame.K_LEFT: 0,
                    pygame.K_d: 2, pygame.K_RIGHT: 2,
                    pygame.K_s: 3, pygame.K_DOWN: 3,
                }
                if event.key in keys and connection is not None and connection.connected:
                    direction = keys[event.key]
                    if mp_role == 'host':
                        multiplayer_move(0, *[(-1, 0), (0, -1), (1, 0), (0, 1)][direction])
                    else:
                        connection.send({'type': 'move', 'direction': direction})
            elif mode in ('game', 'rl'):
                if event.key == pygame.K_ESCAPE:
                    mode = 'menu'
                elif event.key == pygame.K_r:
                    start_game(rl=(mode == 'rl'))
                elif mode == 'rl':
                    if event.key == pygame.K_SPACE:
                        rl_paused = not rl_paused
                    elif event.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                        rl_speed = min(30, rl_speed + 1)
                    elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                        rl_speed = max(1, rl_speed - 1)
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
                start_game()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if mode == 'menu':
                if buttons[0][0].collidepoint(event.pos):
                    start_game()
                elif buttons[1][0].collidepoint(event.pos):
                    start_game(rl=True)
                elif buttons[-1][0].collidepoint(event.pos):
                    close_network()
                    pygame.quit()
                    sys.exit()
                elif buttons[2][0].collidepoint(event.pos):
                    mode = 'mp_menu'
                elif buttons[3][0].collidepoint(event.pos):
                    mode = 'settings'
            elif mode == 'mp_menu':
                if menu_rect.collidepoint(event.pos):
                    mode = 'menu'
                elif host_button.collidepoint(event.pos):
                    begin_multiplayer(True)
                elif join_button.collidepoint(event.pos):
                    begin_multiplayer(False)
            elif mode == 'settings':
                if menu_rect.collidepoint(event.pos):
                    mode = 'menu'
                elif settings_speed_minus.collidepoint(event.pos):
                    rl_speed = max(1, rl_speed - 1)
                elif settings_speed_plus.collidepoint(event.pos):
                    rl_speed = min(30, rl_speed + 1)
                elif settings_trail.collidepoint(event.pos):
                    show_trail = not show_trail
            elif mode == 'multiplayer':
                if menu_rect.collidepoint(event.pos):
                    close_network()
                    mode = 'menu'
            elif mode in ('game', 'rl') and won:
                if win_new.collidepoint(event.pos):
                    start_game(rl=(mode == 'rl'))
                elif win_menu.collidepoint(event.pos):
                    mode = 'menu'

    if mode == 'rl' and agent is not None and not rl_paused and not agent.finished:
        now = pygame.time.get_ticks()
        if now - last_rl_step >= 1000 // rl_speed:
            agent.step(grid, goal)
            if agent.position not in trail:
                trail.append(agent.position)
            player = list(agent.position)
            moves = agent.moves
            won = agent.won
            last_rl_step = now

    if mode == 'multiplayer':
        handle_network()

    screen.fill(NAVY)
    if mode == 'menu':
        for y in range(0, HEIGHT, CELL):
            for x in range(0, MAZE_WIDTH, CELL):
                pygame.draw.rect(screen, (23, 37, 55),
                                 (x + 2, y + 2, CELL - 4, CELL - 4), border_radius=3)
        label('LABIRENT', large, CREAM, (MAZE_WIDTH // 2, 100))
        draw_mouse(MAZE_WIDTH // 2 - 165, 155)
        draw_cheese(MAZE_WIDTH // 2 + 155, 155)
        for i, (rect, text) in enumerate(buttons):
            button(rect, text, mouse_pos, active=True)
        label('WASD / Ok Tuslari: Hareket  |  R: Yeni Harita  |  ESC: Menu',
              small, MUTED, (MAZE_WIDTH // 2, HEIGHT - 35))
        left_text('RL: Canli istatistik paneli', MAZE_WIDTH + 17, 30, small, YELLOW)
        left_text('RL Modu secerek basla.', MAZE_WIDTH + 17, 68, tiny, MUTED)
    elif mode == 'settings':
        draw_submenu_title('AYARLAR')
        label('RL Hizi (adim/saniye)', font, WHITE, (MAZE_WIDTH // 2, 185))
        button(settings_speed_minus, '-', mouse_pos)
        label(str(rl_speed), font, YELLOW, (MAZE_WIDTH // 2 + 38, 251))
        button(settings_speed_plus, '+', mouse_pos)
        button(settings_trail, 'Iz Goster: ' + ('Acik' if show_trail else 'Kapali'), mouse_pos)
        label('Ayarlar oyundan cikana kadar korunur.', small, MUTED, (MAZE_WIDTH // 2, 435))
    elif mode == 'mp_menu':
        draw_submenu_title('COK OYUNCULU')
        button(host_button, 'Oda Kur', mouse_pos)
        button(join_button, 'Odaya Katil', mouse_pos)
        label('Sunucu IP Adresi (yazabilirsin):', small, MUTED, (MAZE_WIDTH // 2, 288))
        pygame.draw.rect(screen, (39, 64, 92), ip_rect, border_radius=8)
        label(join_ip or 'IP yaz...', small, WHITE, ip_rect.center)
        label(f'Ayni Wi-Fi / LAN | TCP port: {PORT}', small, MUTED, (MAZE_WIDTH // 2, 415))
        label('Oda kuran bilgisayarin yerel IPv4 adresini gir.', small, MUTED, (MAZE_WIDTH // 2, 447))
    elif mode == 'multiplayer':
        draw_submenu_title('IKI KISILIK YARIS')
        label('Sen: ' + ('Oyuncu 1' if mp_role == 'host' else 'Oyuncu 2'), font, YELLOW, (MAZE_WIDTH // 2, 160))
        if connection and connection.connected and grid:
            draw_maze(grid, mp_players[0], goal, other=mp_players[1])
            label('P1: ' + str(mp_moves[0]) + '    P2: ' + str(mp_moves[1]), font, YELLOW, (MAZE_WIDTH // 2, TOP // 2))
            if mp_winner is not None:
                label(f'OYUNCU {mp_winner + 1} KAZANDI!', large, YELLOW, (MAZE_WIDTH // 2, HEIGHT // 2))
        else:
            label(network_message, small, WHITE, (MAZE_WIDTH // 2, 295))
        left_text('Oyuncu 1: Gri fare', MAZE_WIDTH + 17, 45, small, WHITE)
        left_text('Oyuncu 2: Mavi fare', MAZE_WIDTH + 17, 83, small, WHITE)
        left_text(network_message[:33], MAZE_WIDTH + 17, 145, tiny, MUTED)
        left_text('WASD / Ok: Hareket', MAZE_WIDTH + 17, 205, tiny, MUTED)
        left_text('ESC: Ana menu', MAZE_WIDTH + 17, 239, tiny, MUTED)
        button(menu_rect, 'Ana Menu', mouse_pos)
    else:
        pygame.draw.rect(screen, (13, 23, 38), (0, 0, MAZE_WIDTH, TOP))
        label('RL MODU' if mode == 'rl' else 'MANUEL MOD', font, WHITE, (105, TOP // 2))
        label(f'Hamle: {moves}', font, YELLOW, (MAZE_WIDTH // 2, TOP // 2))
        label('R: Yeni  |  ESC: Menu', small, WHITE, (MAZE_WIDTH - 120, TOP // 2))
        draw_maze(grid, player, goal, agent if mode == 'rl' else None,
                  trail=trail if mode == 'rl' and show_trail else None)
        if mode == 'rl':
            draw_panel(agent, rl_speed, rl_paused)
        if won:
            draw_win(moves, mouse_pos, rl=(mode == 'rl'))
    pygame.display.flip()
    clock.tick(60)
