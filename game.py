import pygame
import os
import sys
import random
import math
from settings import *


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    fon = pygame.transform.scale(load_image('screens/start_screen.png'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    path = 'player/menu/m_'
    delay1 = 20
    delay2 = 200
    k = 0
    por = 0
    couneter = 0
    if MUSIC:
        music = pygame.mixer.Sound('data/music/track_1.mp3')
        music.play(loops=100)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                load_level(LEVELS['0'])
                if MUSIC:
                    music.stop()
                return
        if couneter % delay1 == 0:
            k += 1
            k %= 4
            image = load_image(f'{path}{k}_{por}.png', -1)
        if couneter % delay2 == 0:
            por = random.randint(0, 4)
        couneter += 1
        screen.blit(fon, (0, 0))
        screen.blit(image, (WIDTH // 2 + 8, HEIGHT // 2 + 37))
        pygame.display.flip()
        clock.tick(FPS)


def end_screen():
    if MUSIC:
        music.stop()
    fon = pygame.transform.scale(load_image('screens/end_screen.png'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                start_screen()
                return
        pygame.display.flip()
        clock.tick(FPS)


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def load_level(filename):
    filename = 'data/maps/' + filename + '.csv'
    global obj, player, camera, BG_COLOR, music
    obj = []
    with open(filename, 'r') as mapFile:
        level_map = [line.strip().split(';') for line in mapFile]
    for i, st in enumerate(level_map):
        if i == 0:
            lvl_sets = st
            BG_COLOR = lvl_sets[0]
            if MUSIC:
                track = f'data/music/{lvl_sets[1]}.mp3'
                try:
                    music.stop()
                except:
                    pass
                try:
                    music = pygame.mixer.Sound(track)
                    music.play(loops=100)
                except:
                    pass
            continue
        for j, el in enumerate(st):
            if len(el) != 0:
                for s in el.split('.'):
                    if len(s) != 0:
                        ob = do(s, i, j)
                        if ob is not None:
                            if ob.__class__ == Player:
                                player = ob
                                camera = Camera()
                            else:
                                obj.append(ob)


def do(s, i, j):
    # s[1] - tx
    # s[2] - platform_shift - sight - pos1
    # s[3] - pos2 - k
    # s[4] - level1
    # s[5] - level2
    cords = (j * TILE_SIZE, i * TILE_SIZE)
    if s[0] == 'w':  # Wall s1
        return Wall(cords, image_name='walls/' + wall_tx[s[1:]])
    if s[0] == 't':  # Tile s1
        return Tile(cords, image_name='tiles/' + tiles_tx[s[1]])
    if s[0] == 'p':  # Portal s4
        return Portal(cords, s[2], s[3], s[4], s[5], image_name='portals/' + portals_tx[s[1]])
    if s[0] == 'l':  # Ladder s1
        return Ladder(cords, image_name='ladders/' + ladders_tx[s[1]])
    if s[0] == 'v':  # Vertical_Platforms s2
        return Platform(cords, s[2], s[3], image_names=platforms_tx[s[1]], orient=0)
    if s[0] == 'h':  # Horizontal_platform s2
        return Platform(cords, s[2], s[3], image_names=platforms_tx[s[1]], orient=1)
    if s[0] == 'i':  # Pike s1
        return Pike(cords, image_name='pikes/' + pikes_tx[s[1]])
    if s[0] == 'o':  # Player s1:
        return Player(cords, sight=s[1:], image_name='player/idle_0')
    if s[0] == 'r':  # Trap s2
        return Trap(cords, s[1], image_name='traps/' + traps_tx[s[1]])
    return None


class Object:
    def __init__(self, cords, w, h, color, block=False, image_name=None, color_key=(255, 255, 255)):
        self.color = color
        self.block = block
        self.rect = pygame.Rect(*cords, w, h)
        self.vx = 0
        self.vy = 0
        if image_name is not None:
            self.image = load_image(image_name + '.png', color_key)
        else:
            self.image = None

    def update(self):
        pass

    def collision(self, rect, rects):
        collided = []
        for el in rects:
            if rect.colliderect(el):
                collided.append(el)
        return collided

    def draw(self):
        if self.image is not None and SPRITE:
            screen.blit(self.image, (self.rect.x, self.rect.y))
        else:
            pygame.draw.rect(screen, self.color, self.rect)


class Player(Object):
    def __init__(self, cords, sight, image_name):
        super().__init__(cords, 30, 100, (0, 0, 255), image_name=image_name)
        self.plat_v = 0
        self.ay = 1
        self.air_time = 0
        self.ladder = 0
        self.dir = 0
        self.sight = int(sight)
        self.couneter = 0
        self.load_images('idle_', 4)
        self.k = 0
        self.jump_lengh = 20
        self.up_down = 0
        self.hp = 20
        self.mx_hp = self.hp
        self.delay = 20
        self.kill_delay = 50
        self.kill_delay_count = 0

    def load_images(self, action, n):
        self.images = []
        path = f'player/{action}'
        for el in range(n):
            self.images.append(load_image(path + str(el) + '.png', -1))

    def new_pos(self, x, y):
        self.rect.x = x
        self.rect.y = y

    def move(self, dx, dy, rects):
        self.rect.x += dx
        dirs = {'up': False, 'down': False, 'right': False, 'left': False}
        colls = filter(lambda x: x.block, self.collision(self.rect, rects))
        if dx < 0:
            self.dir = -1
        if dx > 0:
            self.dir = 1
        if dx == 0:
            self.dir = 0
        for el in colls:
            if dx > 0:
                self.rect.right = el.rect.left
                dirs['right'] = True
            elif dx < 0:
                self.rect.left = el.rect.right
                dirs['left'] = True
        self.rect.y += dy
        colls = filter(lambda x: x.block, self.collision(self.rect, rects))
        if dy != 0:
            self.up_down = 1
        else:
            self.up_down = 0
        for el in colls:
            if dy > 0:
                self.rect.bottom = el.rect.top
                dirs['down'] = True
                if el.__class__ == Platform:
                    self.plat_v = el.v * el.dx
                else:
                    self.plat_v = 0
            elif dy < 0:
                self.rect.top = el.rect.bottom
                dirs['up'] = True
        return dirs

    def next_image(self):
        self.k += 1
        self.k %= len(self.images)
        self.image = self.images[self.k]

    def update(self):
        if self.kill_delay_count > 0:
            self.kill_delay_count -= 1
        self.couneter += 1
        if self.couneter % self.delay == 0:
            self.couneter = 0
            self.next_image()
        if self.dir == 1 and self.plat_v == 0:
            if self.air_time > 0:
                self.load_images('jump_r_', 1)
            else:
                self.load_images('step_r_', 3 )
        elif self.dir == -1 and self.plat_v == 0:
            if self.air_time > 0:
                self.load_images('jump_l_', 1)
            else:
                self.load_images('step_l_', 3)
        else:
            if self.air_time > 1:
                self.load_images('jump_c_', 1)
            else:
                self.load_images('idle_', 4)
        cols = self.collision(self.rect, obj)
        self.ladder = 0
        for el in cols:
            if el.__class__ == Portal:
                if self.dir != 0:
                    el.teleport(self.dir)
                else:
                    el.teleport(1)
            if el.__class__ == Ladder:
                self.plat_v = 0
                self.ladder = 1
            if el.__class__ == Pike:
                self.kill()
            if el.__class__ == Projectile:
                self.kill()
                el.kill()
        if self.air_time > 300:
            self.kill()
        if self.ladder:
            self.air_time = 0
            self.vy = 0
            if self.up_down:
                self.load_images('ladder_m_', 3)
            else:
                self.load_images('ladder_', 1)
        dirs = self.move(self.vx + self.plat_v, self.vy, obj)
        self.vy += self.ay - self.ladder
        if self.vy > 20:
            self.vy = 20
        if dirs['down'] or dirs['up']:
            self.vy = 1
            self.air_time = 0
        else:
            self.air_time += 1
        if dirs['right'] or dirs['left']:
            self.vx = 0

    def jump(self):
        if self.air_time <= 10:
            self.load_images('jump_', 1)
            self.vy -= self.jump_lengh

    def vision(self, rects):
        ans = set()
        if self.sight is not None:
            vision_rect = pygame.Rect(self.rect.x + self.rect.w // 2 - self.sight,
                                      self.rect.y + self.rect.h // 2 - self.sight,
                                      self.sight * 2,
                                      self.sight * 2)
            return self.collision(vision_rect, rects)
            return ans
        else:
            return rects

    def kill(self):
        if self.kill_delay_count == 0:
            self.kill_delay_count = self.kill_delay
            self.hp -= 1
            if self.hp == 0:
                end_screen()


class Platform(Object):
    def __init__(self, cords, mx_shift, k, orient=1, image_names=None, w=TILE_SIZE, h=TILE_SIZE, color=(100, 100, 100)):
        super().__init__(cords, w, h, color, True, 'platforms/' + image_names[0])
        self.image_names = image_names
        self.orient = orient
        self.k = int(k) * TILE_SIZE
        self.dir = 1
        self.v = 1
        self.dx = 0
        self.dy = 0
        self.mx_shift = int(mx_shift) * TILE_SIZE
        self.blocks = ['Player']

    def update(self):
        if self.k >= self.mx_shift:
            self.k = 0
            if self.dir:
                self.dir = 0
            else:
                self.dir = 1
        if self.dir:
            self.k += 1
            if self.orient:
                self.dx = -1
            else:
                self.dy = -1
        else:
            self.k += 1
            if self.orient:
                self.dx = 1
            else:
                self.dy = 1
        self.move(self.dx * self.v, self.dy * self.v)

    def draw(self):
        if self.image is not None and SPRITE:
            if self.dir:
                self.image = load_image('platforms/' + self.image_names[0] + '.png')
            else:
                self.image = load_image('platforms/' + self.image_names[1] + '.png')
            screen.blit(self.image, (self.rect.x, self.rect.y))
        else:
            pygame.draw.rect(screen, self.color, self.rect)

    def move(self, dx, dy):
        self.rect.x += dx
        dirs = {'up': False, 'down': False, 'right': False, 'left': False}
        colls = self.collision(self.rect, [player])
        for el in colls:
            if dx > 0:
                el.rect.left = self.rect.right
                dirs['right'] = True
            elif dx < 0:
                el.rect.right = self.rect.left
                dirs['left'] = True
        self.rect.y += dy
        colls = self.collision(self.rect, [player])
        for el in colls:
            if dy > 0:
                el.rect.top = self.rect.bottom
                dirs['down'] = True
            elif dy < 0:
                el.rect.bottom = self.rect.top
                dirs['up'] = True


class Ladder(Object):
    def __init__(self, cords, image_name=None, w=TILE_SIZE, h=TILE_SIZE, color=(255, 0, 0)):
        super().__init__(cords, w, h, color, False, image_name)


class Portal(Object):
    def __init__(self, cords, pos1, pos2, level1, level2, image_name=None, w=TILE_SIZE, h=TILE_SIZE * 2, color=(255, 0, 100)):
        x, y = cords
        super().__init__((x, y - h // 2), w, h, color, False, image_name)
        self.pos1 = pos1
        self.pos2 = pos2
        self.level1 = level1
        self.level2 = level2

    def teleport(self, dir):
        if self.level1 != self.level2:
            load_level(LEVELS[self.level2])
        for el in obj:
            if el.__class__ == Portal:
                if el.pos1 == self.pos2 and el.pos2 == self.pos1\
                        and self.level2 == el.level1 and self.level1 == el.level2:
                    player.new_pos(el.rect.x + 50, el.rect.y - 50)


class Tile(Object):
    def __init__(self, cords, image_name=None, w=TILE_SIZE, h=TILE_SIZE, color=(0, 130, 111)):
        super().__init__(cords, w, h, color, True, image_name)


class Wall(Object):
    def __init__(self, cords, image_name=None, w=TILE_SIZE, h=TILE_SIZE, color=(111, 233, 111)):
        super().__init__(cords, w, h, color, False, image_name) #


class Pike(Object):
    def __init__(self, cords, image_name=None, w=TILE_SIZE, h=TILE_SIZE, color=(254, 0, 200)):
        super().__init__(cords, w, h, color, False, image_name)


class Projectile(Object):
    def __init__(self, cords, dir, image_name=None, w=TILE_SIZE, h=TILE_SIZE, color=(255, 100, 100)):
        super().__init__(cords, w, h, color, False, image_name)
        self.vx = 5 * dir
        self.k = 0
        self.max_count = 200

    def update(self):
        if len(self.collision(self.rect, obj)) > 1:
            for el in self.collision(self.rect, obj):
                if el != self and el.block:
                    self.kill()
        self.k += 1
        if self.k > self.max_count:
            self.kill()
        self.rect.x += self.vx

    def kill(self):
        for i, el in enumerate(obj):
            if el == self:
                del obj[i]


class Trap(Object):
    def __init__(self, cords, dir, image_name=None, w=TILE_SIZE, h=TILE_SIZE, color=(255, 100, 100)):
        super().__init__(cords, w, h, color, True, image_name)
        self.dir = dir
        if self.dir == '0':
            self.tx = -1
        else:
            self.tx = 1
        self.counter = 0

    def update(self):
        self.counter += 1
        self.counter %= 200
        if self.counter % 100 == 0:
            obj.append(Projectile((self.rect.x + self.rect.w * self.tx, self.rect.y + self.rect.h // 2),
                                  self.tx, w=20, h = 15, image_name='traps/' + arrow_tx[self.dir]))


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)


if __name__ == '__main__':
    left = False
    right = False
    up = False
    down = False
    running = True
    all_sprites = pygame.sprite.Group()
    pygame.init()
    pygame.display.set_caption("Castle's shadow")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    start_screen()
    heart_image1 = load_image('player/heart1.png', -1)
    heart_image2 = load_image('player/heart2.png', -1)
    heart_image3 = load_image('player/back_heart.png')
    counter = 0
    d = 0
    ots = 15
    while running:
        counter += 1
        counter %= 100
        screen.fill(pygame.Color(BG_COLOR))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    pass
                elif event.button == 3:
                    pass
                    # player.new_pos(*event.pos)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d:
                    right = True
                if event.key == pygame.K_a:
                    left = True
                if event.key == pygame.K_w:
                    up = True
                if event.key == pygame.K_s:
                    down = True
                if event.key == pygame.K_SPACE:
                    player.jump()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_d:
                    right = False
                if event.key == pygame.K_a:
                    left = False
                if event.key == pygame.K_w:
                    up = False
                if event.key == pygame.K_s:
                    down = False
        if right:
            player.move(5, 0, obj)
        if left:
            player.move(-5, 0, obj)
        if up:
            if player.ladder:
                player.move(0, -5, obj)
        if down:
            player.move(0, 5, obj)

        els = player.vision(obj)

        player.update()
        camera.update(player)
        camera.apply(player)

        for el in obj:
            camera.apply(el)
            el.update()
        for el in els:
            if el.__class__ == Wall:
                el.draw()
        for el in els:
            if el.__class__ != Wall:
                el.draw()
        player.draw()
        if counter % 25 == 0:
            d += 1
            d %= 2
        for i in range(player.mx_hp):
            screen.blit(heart_image3, (i * TILE_SIZE + ots, ots))
        if player.hp < player.mx_hp // 2:
            for i in range(player.hp):
                if (i + d) % 2 == 0:
                    screen.blit(heart_image1, (i * TILE_SIZE + ots, ots))
                else:
                    screen.blit(heart_image2, (i * TILE_SIZE + ots, ots))
        else:
            for i in range(player.hp):
                screen.blit(heart_image1, (i * TILE_SIZE + ots, ots))
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()