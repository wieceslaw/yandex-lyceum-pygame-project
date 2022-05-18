import pygame
import random


class Object():
    def __init__(self, x, y, w, h, color):
        self.x = x
        self.y = y
        self.color = color
        self.rect = pygame.Rect(x, y, w, h)

    def update(self):
        pygame.draw.rect(screen, self.color, self.rect)


class Tile(Object):
    def __init__(self, x, y, s, color):
        super().__init__(x, y, tile_size, tile_size, color)
        self.s = s


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('Лесенки')
    size = width, height = 1600, 900
    screen = pygame.display.set_mode(size)
    running = True
    fps = 60
    clock = pygame.time.Clock()
    obj = []
    tile_size = 20
    s = ''
    k = 0
    d = 0
    clear = False
    drawing = False
    color = (random.randint(0, 255),
             random.randint(0, 255),
             random.randint(0, 255))
    space = False
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sp = {}
                for el in obj:
                    if (el.x, el.y) in sp:
                        if el.s not in sp[(el.x, el.y)]:
                            sp[(el.x, el.y)] += '.' + el.s
                    else:
                        sp[(el.x, el.y)] = el.s
                if len(sp) != 0:
                    mx = max([el[0] for el in sp]) // tile_size
                    my = max([el[1] for el in sp]) // tile_size
                    pl = []
                    for j in range(my + 1):
                        st = ''
                        for i in range(mx + 1):
                            if (i * tile_size, j * tile_size) in sp:
                                st += sp[(i * tile_size, j * tile_size)] + ';'
                            else:
                                st += ';'
                        pl.append(st)
                    for el in pl:
                        print(el)
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                drawing = True
            if event.type == pygame.MOUSEBUTTONUP:
                drawing = False
            if event.type == pygame.MOUSEMOTION:
                if drawing:
                    x, y = event.pos
                    if clear:
                        for i, el in enumerate(obj):
                            if el.x == x // tile_size * tile_size and el.y == y // tile_size * tile_size:
                                del obj[i]
                    else:
                        obj.append(Tile(x // tile_size * tile_size, y // tile_size * tile_size, s, color))
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_CAPSLOCK:
                    if clear:
                        clear = False
                    else:
                        clear = True
                if event.key == pygame.K_SPACE:
                    s = ''
                    color = (random.randint(0, 255),
                             random.randint(0, 255),
                             random.randint(0, 255))
                    space = True
                else:
                    if space:
                        s += pygame.key.name(event.key)
                        print(s)
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    space = False

        screen.fill(pygame.Color('white'))
        for el in obj:
            el.update()
        pygame.display.flip()
        clock.tick(fps)
    pygame.quit()