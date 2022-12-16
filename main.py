import pyxel
from random import randint, random

WINDOW_WIDTH = 256
WINDOW_HEIGHT = 256


class App:
    def __init__(self):
        pyxel.init(WINDOW_WIDTH, WINDOW_HEIGHT)
        pyxel.load('./assets/my_resource.pyxres')
        self.rabbit = Rabbit()
        self.carrots = []
        self.rocks = []
        self.scroll_speed = 2
        pyxel.run(self.update, self.draw)

    def update(self):
        self.rabbit.update()
        for carrot in self.carrots:
            carrot.update(self.rabbit, self.scroll_speed)
        for rock in self.rocks:
            rock.update(self.rabbit, self.scroll_speed)
        if random() < 0.3:
            self.carrots.append(Carrot())
        if random() < 0.1:
            self.rocks.append(Rock())
        self.carrots = [carrot for carrot in self.carrots if carrot.alive]
        self.rocks = [rock for rock in self.rocks if rock.alive]

    def draw(self):
        pyxel.cls(0)
        for carrot in self.carrots:
            carrot.draw()
        for rock in self.rocks:
            rock.draw()
        self.rabbit.draw()


class Rabbit:
    INIT_START_X = 20
    INIT_START_Y = WINDOW_HEIGHT // 2

    RUN_U = 0
    RUN_V = 16
    RUN_W = 48
    RUN_H = 32

    HIT_U = 0
    HIT_V = 48
    HIT_W = 48
    HIT_H = 32

    HIT_ANIMATION_TIME = 20

    def __init__(self):
        self.x = self.INIT_START_X
        self.y = self.INIT_START_Y
        self.state = 'run'
        self.count_time = 0

    def update(self):
        key_input = 0
        if pyxel.btn(pyxel.KEY_W):
            key_input -= 1
        if pyxel.btn(pyxel.KEY_S):
            key_input += 1
        self.y += self.RUN_H * key_input
        if self.state == 'hit':
            self.count_time -= 1
            if self.count_time == 0:
                self.state = 'run'

    def hit(self):
        if self.state == 'run':
            self.state = 'hit'
            self.count_time = self.HIT_ANIMATION_TIME

    def draw(self):
        if self.state == 'run':
            pyxel.blt(self.x, self.y, 0, self.RUN_U, self.RUN_V, self.RUN_W, self.RUN_H, 0)
        elif self.state == 'hit' and pyxel.frame_count % 4 < 3:
            pyxel.blt(self.x, self.y, 0, self.HIT_U, self.HIT_V, self.HIT_W, self.HIT_H, 0)


class Carrot:
    U = 9
    V = 80
    W = 16
    H = 32

    def __init__(self):
        self.x = WINDOW_WIDTH
        self.y = randint(0, WINDOW_HEIGHT) // self.H * self.H
        self.alive = True

    def update(self, rabbit, scroll_speed):
        if self.x < -self.W:
            self.alive = False
        self.x -= scroll_speed
        if self.collision(rabbit):
            self.alive = False

    def collision(self, rabbit):
        dx = self.x - rabbit.x
        if not (dx < 0 and abs(dx) < self.W or 0 <= dx < rabbit.RUN_W):
            return False
        dy = self.y - rabbit.y
        if not (dy < 0 and abs(dy) < self.H or 0 <= dy < rabbit.RUN_H):
            return False
        return True

    def draw(self):
        pyxel.blt(self.x, self.y, 0, self.U, self.V, self.W, self.H, 0)


class Rock:
    U = 32
    V = 80
    W = 32
    H = 32

    def __init__(self):
        self.x = WINDOW_WIDTH
        self.y = randint(0, WINDOW_HEIGHT) // self.H * self.H
        self.alive = True

    def update(self, rabbit, scroll_speed):
        if self.x < -self.W:
            self.alive = False
        self.x -= scroll_speed
        if self.collision(rabbit):
            rabbit.hit()

    def collision(self, rabbit):
        dx = self.x - rabbit.x
        if not (dx < 0 and abs(dx) < self.W or 0 <= dx < rabbit.RUN_W):
            return False
        dy = self.y - rabbit.y
        if not (dy < 0 and abs(dy) < self.H or 0 <= dy < rabbit.RUN_H):
            return False
        return True

    def draw(self):
        pyxel.blt(self.x, self.y, 0, self.U, self.V, self.W, self.H, 0)

App()
