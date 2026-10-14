"""Manuel, bilgisayar ve iki oyunculu labirent uygulaması."""
import argparse
import pygame
import rendering as ui
from maze import generate_maze
from player import Player
from rl_agent import RLAgent
from network import Connection, PORT
from multiplayer import MultiplayerSession

KEYS = {pygame.K_a: 0, pygame.K_LEFT: 0, pygame.K_w: 1, pygame.K_UP: 1,
        pygame.K_d: 2, pygame.K_RIGHT: 2, pygame.K_s: 3, pygame.K_DOWN: 3}


class GameApplication:
    def __init__(self):
        ui.initialize()
        self.clock = pygame.time.Clock()
        self.running = True
        self.mode = 'menu'
        self.speed = 8
        self.show_trail = True
        self.paused = False
        self.trail = set()
        self.agent = self.player = None
        self.grid = self.start = self.goal = None
        self.connection = self.session = None
        self.join_ip = '127.0.0.1'
        self.last_step = 0
        self.buttons = {}

    def menu(self):
        if self.connection:
            self.connection.close()
        self.connection = self.session = None
        self.mode = 'menu'

    def start_game(self, computer=False, same=False):
        if not same or self.grid is None:
            self.grid, self.start, self.goal = generate_maze()
        self.player = Player(self.start, self.goal)
        self.agent = RLAgent(self.start) if computer else None
        self.mode = 'computer' if computer else 'manual'
        self.paused = False
        self.trail = {self.start}
        self.last_step = pygame.time.get_ticks()

    def start_network(self, host):
        self.menu()
        self.connection = Connection()
        self.session = MultiplayerSession(self.connection, 'host' if host else 'client')
        self.mode = 'network'
        if host:
            self.connection.host()
        else:
            self.connection.join(self.join_ip.strip())

    def action(self, name):
        if name == 'menu':
            self.menu()
        elif name == 'manual':
            self.start_game()
        elif name == 'computer':
            self.start_game(True)
        elif name in ('settings', 'network_menu'):
            self.mode = name
        elif name == 'quit':
            self.running = False
        elif name in ('host', 'join'):
            self.start_network(name == 'host')
        elif name == 'slower':
            self.speed = max(1, self.speed - 1)
        elif name == 'faster':
            self.speed = min(30, self.speed + 1)
        elif name == 'trail':
            self.show_trail = not self.show_trail
        elif name == 'pause':
            self.paused = not self.paused
        elif name in ('new', 'same'):
            self.start_game(self.mode == 'computer', same=name == 'same')
        elif name == 'rematch' and self.session and self.session.winner is not None:
            self.session.new_round()

    def event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for name, (rect, active) in list(self.buttons.items()):
                if active and rect.collidepoint(event.pos):
                    self.action(name)
                    break
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.menu()
            elif self.mode == 'network_menu':
                if event.key == pygame.K_BACKSPACE:
                    self.join_ip = self.join_ip[:-1]
                elif event.unicode and event.unicode in '0123456789.abcdefghijklmnopqrstuvwxyz-':
                    self.join_ip = (self.join_ip + event.unicode)[:60]
            elif self.mode in ('manual', 'computer'):
                if event.key == pygame.K_r:
                    self.action('new')
                elif event.key == pygame.K_t:
                    self.action('same')
                elif self.mode == 'manual' and event.key in KEYS:
                    self.player.move(self.grid, KEYS[event.key])
                elif self.mode == 'computer':
                    if event.key == pygame.K_SPACE:
                        self.action('pause')
                    elif event.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                        self.action('faster')
                    elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                        self.action('slower')
            elif self.mode == 'network':
                if event.key in KEYS:
                    self.session.move(KEYS[event.key])
                elif event.key == pygame.K_r:
                    self.action('rematch')
            elif self.mode == 'menu' and event.key == pygame.K_RETURN:
                self.start_game()

    def update(self):
        if self.mode == 'computer' and not self.paused and not self.agent.finished:
            now = pygame.time.get_ticks()
            if now - self.last_step >= 1000 / self.speed:
                self.agent.step(self.grid, self.goal)
                self.trail.add(self.agent.position)
                self.last_step = now
        elif self.mode == 'network':
            self.session.poll()

    def button(self, name, text, x, y, width=240, active=True):
        rect = pygame.Rect(x, y, width, 42)
        self.buttons[name] = rect, active
        ui.button(rect, text, pygame.mouse.get_pos(), active)

    def text(self, text, x, y, color=None, small=False):
        ui.left_text(text, x, y, ui.tiny if small else ui.small, color or ui.WHITE)

    def wrapped(self, text, x, y, width=250):
        line = ''
        for word in text.split():
            candidate = (line + ' ' + word).strip()
            if ui.small.size(candidate)[0] > width and line:
                self.text(line, x, y)
                y += 24
                line = word
            else:
                line = candidate
        if line:
            self.text(line, x, y)
        return y + 24

    def draw(self):
        ui.screen.fill(ui.NAVY)
        self.buttons = {}
        x = ui.MAZE_WIDTH + 16
        if self.mode in ('manual', 'computer'):
            actor = self.agent if self.mode == 'computer' else self.player
            ui.draw_maze(self.grid, actor.position, self.goal,
                         trail=self.trail if self.mode == 'computer' and self.show_trail else None)
            ui.label('BİLGİSAYAR' if self.mode == 'computer' else 'MANUEL', ui.font, ui.WHITE, (125, 30))
            ui.label(f'Hamle: {actor.moves}', ui.font, ui.YELLOW, (400, 30))
            self.text('Başarılı geçiş = 1 hamle', x, 24, ui.YELLOW)
            for i, (key, value) in enumerate([('Hamle', actor.moves), ('Deneme', actor.attempts), ('Çarpışma', actor.collisions)]):
                self.text(f'{key}: {value}', x, 65 + i * 30)
            if self.mode == 'computer':
                self.text('Keşif: DFS / geri izleme', x, 169, ui.YELLOW)
                self.text(f'Keşfedilen hücre: {len(actor.visited)}', x, 204)
                self.text(f'Hız: {self.speed} adım/sn', x, 234)
                self.wrapped(actor.status, x, 266)
                self.text('Q değerleri deneysel kayıttır;', x, 327, ui.MUTED, True)
                self.text('yol seçimini DFS belirler.', x, 347, ui.MUTED, True)
                self.button('pause', 'Devam' if self.paused else 'Duraklat', x, 385, active=not actor.finished)
                self.text('SPACE: Dur/devam  +/-: Hız', x, 439, ui.MUTED, True)
            else:
                self.wrapped('WASD veya yön tuşlarıyla fareyi peynire götür.', x, 177)
            self.button('same', 'Aynı harita (T)', x, 470)
            self.button('new', 'Yeni harita (R)', x, 520)
            self.button('menu', 'Ana menü (ESC)', x, 570)
            if actor.won:
                shade = pygame.Surface((ui.MAZE_WIDTH, ui.HEIGHT), pygame.SRCALPHA)
                shade.fill((0, 0, 0, 165))
                ui.screen.blit(shade, (0, 0))
                ui.label('Peynir bulundu!', ui.large, ui.YELLOW, (ui.MAZE_WIDTH // 2, 280))
                ui.label(f'{actor.moves} hamle · {actor.collisions} çarpışma', ui.font, ui.WHITE, (ui.MAZE_WIDTH // 2, 350))
        elif self.mode == 'network':
            session = self.session
            self.text('İKİ OYUNCULU YARIŞ', x, 25, ui.YELLOW)
            self.text('Sen: ' + ('Oyuncu 1' if session.role == 'host' else 'Oyuncu 2'), x, 65)
            self.text('P1: Gri   P2: Mavi', x, 95)
            if session.grid:
                ui.draw_maze(session.grid, session.players[0].position, session.goal, other=session.players[1].position)
                for i, actor in enumerate(session.players):
                    self.text(f'P{i+1} hamle: {actor.moves}', x, 145 + i * 65)
                    self.text(f'Deneme: {actor.attempts} / Çarpışma: {actor.collisions}', x, 170 + i * 65, small=True)
            self.wrapped(session.message, x, 300)
            if session.winner is not None:
                ui.label(f'OYUNCU {session.winner + 1} KAZANDI!', ui.font, ui.YELLOW, (ui.MAZE_WIDTH // 2, 30))
                self.button('rematch', 'Yeni yarış (R)', x, 440,
                            active=session.role == 'host' and self.connection.connected)
                if session.role == 'client':
                    self.text('Yeni yarışı oda sahibi başlatır.', x, 495, small=True)
            elif not session.ready:
                ui.label('Bağlantı / harita bekleniyor', ui.font, ui.WHITE, (ui.MAZE_WIDTH // 2, 30))
            else:
                ui.label(f'Yarış {session.round_id} · İlk ulaşan kazanır', ui.font, ui.YELLOW, (ui.MAZE_WIDTH // 2, 30))
            self.button('menu', 'Ana menü (ESC)', x, 570)
        else:
            title = {'menu': 'LABİRENT', 'settings': 'AYARLAR', 'network_menu': 'İKİ OYUNCULU'}[self.mode]
            ui.label(title, ui.large, ui.CREAM, (ui.MAZE_WIDTH // 2, 95))
            if self.mode == 'menu':
                ui.draw_mouse(340, 167)
                ui.draw_cheese(440, 167)
                for i, (name, title) in enumerate([('manual', 'Manuel mod'), ('computer', 'Bilgisayar modu'), ('network_menu', 'Çok oyunculu'), ('settings', 'Ayarlar'), ('quit', 'Çıkış')]):
                    self.button(name, title, 260, 220 + i * 65, 280)
                self.wrapped('Üç modda da hamle sayacı bulunur.', x, 70)
            elif self.mode == 'settings':
                ui.label(f'Bilgisayar hızı: {self.speed} adım/sn', ui.font, ui.WHITE, (400, 200))
                self.button('slower', '-', 260, 250, 100)
                self.button('faster', '+', 440, 250, 100)
                self.button('trail', 'Keşif izi: ' + ('Açık' if self.show_trail else 'Kapalı'), 260, 335, 280)
                self.text('Ayarlar bu oturum boyunca korunur.', 240, 415, ui.MUTED)
                self.button('menu', 'Ana menü', 280, 530)
            else:
                self.button('host', 'Oda kur', 130, 195)
                self.button('join', 'Odaya katıl', 430, 195)
                ui.label('Oda sahibinin IPv4 adresini yaz:', ui.font, ui.WHITE, (400, 290))
                pygame.draw.rect(ui.screen, (39, 64, 92), (150, 325, 500, 48), border_radius=8)
                ui.label(self.join_ip[-40:] or 'IP adresi...', ui.small, ui.YELLOW, (400, 348))
                self.text(f'Aynı Wi-Fi / LAN · TCP {PORT}', 240, 420)
                self.text('127.0.0.1 yalnızca aynı bilgisayardaki deneme içindir.', 150, 460, ui.MUTED)
                self.button('menu', 'Ana menü', 280, 530)
        pygame.display.flip()

    def run(self, max_frames=None):
        frames = 0
        try:
            while self.running:
                for event in pygame.event.get():
                    self.event(event)
                self.update()
                self.draw()
                frames += 1
                if max_frames is not None and frames >= max_frames:
                    break
                self.clock.tick(60)
        finally:
            self.menu()
            pygame.quit()


def main():
    parser = argparse.ArgumentParser(description='Fare ve Peynir labirent oyunu')
    parser.add_argument('--smoke-test', action='store_true', help='Üç kare çalıştırıp çık')
    args = parser.parse_args()
    GameApplication().run(max_frames=3 if args.smoke_test else None)


if __name__ == '__main__':
    main()
