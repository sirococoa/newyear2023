import pyxel
from random import randint, random

WINDOW_WIDTH = 240
WINDOW_HEIGHT = 240


class App:
    INIT_SCROLL_SPEED = 2
    MAX_SCROLL_SPEED = 5
    SCROLL_SPEED_RATE = 3

    def __init__(self):
        pyxel.init(WINDOW_WIDTH, WINDOW_HEIGHT)
        pyxel.load('./assets/my_resource.pyxres')
        self.rabbit = Rabbit()
        self.carrots = []
        self.rocks = []
        self.road = Road()
        self.scroll_speed = self.INIT_SCROLL_SPEED
        self.scroll_speed_count = 0
        pyxel.run(self.update, self.draw)

    def update(self):
        self.scroll_speed = min(self.INIT_SCROLL_SPEED + self.scroll_speed_count // self.SCROLL_SPEED_RATE, self.MAX_SCROLL_SPEED)
        self.rabbit.update()
        self.road.update(self.scroll_speed)
        for carrot in self.carrots:
            if carrot.update(self.rabbit, self.scroll_speed):
                self.scroll_speed_count += 1
        for rock in self.rocks:
            if rock.update(self.rabbit, self.scroll_speed):
                self.scroll_speed_count = 0
        if random() < 0.03 * self.scroll_speed:
            self.carrots.append(Carrot())
        if random() < 0.01 * self.scroll_speed:
            self.rocks.append(Rock())
        self.carrots = [carrot for carrot in self.carrots if carrot.alive]
        self.rocks = [rock for rock in self.rocks if rock.alive]

    def draw(self):
        pyxel.cls(0)
        self.road.draw()
        for carrot in self.carrots:
            carrot.draw()
        for rock in self.rocks:
            rock.draw()
        self.rabbit.draw()


class Rabbit:
    INIT_START_X = 20
    INIT_LANE = 3

    RUN_U = 0
    RUN_V = 16
    RUN_W = 48
    RUN_H = 32

    HIT_U = 0
    HIT_V = 48
    HIT_W = 48
    HIT_H = 32

    HIT_ANIMATION_TIME = 20
    MOVE_ANIMATION_TIME = 2

    def __init__(self):
        self.x = self.INIT_START_X
        self.lane = self.INIT_LANE
        self.y = Road.lane_to_height(self.lane)
        self.state = 'run'
        self.state_count_time = 0
        self.move_count_time = 0

    def update(self):
        if self.move_count_time == 0:
            key_input = 0
            if pyxel.btn(pyxel.KEY_W):
                key_input -= 1
            if pyxel.btn(pyxel.KEY_S):
                key_input += 1
            self.lane += key_input
            self.lane = min(Road.MAX_LANE, max(0, self.lane))
            self.y = Road.lane_to_height(self.lane)
            if key_input != 0:
                self.move_count_time = self.MOVE_ANIMATION_TIME
        else:
            self.move_count_time -= 1

        if self.state == 'hit':
            self.state_count_time -= 1
            if self.state_count_time == 0:
                self.state = 'run'

    def hit(self):
        if self.state == 'run':
            self.state = 'hit'
            self.state_count_time = self.HIT_ANIMATION_TIME

    def draw(self):
        if self.state == 'run':
            pyxel.blt(self.x, self.y, 0, self.RUN_U, self.RUN_V, self.RUN_W, self.RUN_H, 2)
        elif self.state == 'hit' and pyxel.frame_count % 4 < 3:
            pyxel.blt(self.x, self.y, 0, self.HIT_U, self.HIT_V, self.HIT_W, self.HIT_H, 2)


class Carrot:
    U = 9
    V = 80
    W = 16
    H = 32

    def __init__(self):
        self.x = WINDOW_WIDTH
        self.lane = randint(0, Road.MAX_LANE)
        self.y = Road.lane_to_height(self.lane)
        self.alive = True

    def update(self, rabbit, scroll_speed):
        if self.x < -self.W:
            self.alive = False
        self.x -= scroll_speed
        if self.collision(rabbit):
            self.alive = False
            return True
        return False

    def collision(self, rabbit):
        dx = self.x - rabbit.x
        if not (dx < 0 and abs(dx) < self.W or 0 <= dx < rabbit.RUN_W):
            return False
        dy = self.y - rabbit.y
        if not (dy < 0 and abs(dy) < self.H or 0 <= dy < rabbit.RUN_H):
            return False
        return True

    def draw(self):
        pyxel.blt(self.x, self.y, 0, self.U, self.V, self.W, self.H, 2)


class Rock:
    U = 32
    V = 80
    W = 32
    H = 32

    def __init__(self):
        self.x = WINDOW_WIDTH
        self.lane = randint(0, Road.MAX_LANE)
        self.y = Road.lane_to_height(self.lane)
        self.alive = True

    def update(self, rabbit, scroll_speed):
        if self.x < -self.W:
            self.alive = False
        self.x -= scroll_speed
        if self.collision(rabbit):
            rabbit.hit()
            return True
        return False

    def collision(self, rabbit):
        dx = self.x - rabbit.x
        if not (dx < 0 and abs(dx) < self.W or 0 <= dx < rabbit.RUN_W):
            return False
        dy = self.y - rabbit.y
        if not (dy < 0 and abs(dy) < self.H or 0 <= dy < rabbit.RUN_H):
            return False
        return True

    def draw(self):
        pyxel.blt(self.x, self.y, 0, self.U, self.V, self.W, self.H, 2)


class Road:
    U = 0
    V = 112
    W = 16
    H = 48
    ROW = 6
    MAX_LANE = WINDOW_WIDTH // H - 1

    def __init__(self):
        self.column = WINDOW_HEIGHT // self.H
        self.lanes = [randint(0, self.ROW) for _ in range(self.column)]
        self.scroll = 0

    def update(self, scroll_speed):
        # self.scroll += scroll_speed
        if self.scroll > self.W * self.ROW:
            self.scroll -= self.W * self.ROW

    def draw(self):
        for column, lane in enumerate(self.lanes):
            for i in range(WINDOW_WIDTH // (self.W * self.ROW) + 3):
                pyxel.blt(i * (self.W * self.ROW) - lane * self.W - self.scroll, column * self.H, 0, self.U, self.V, (self.W * self.ROW), self.H, 2)

    @classmethod
    def lane_to_height(cls, lane):
        return cls.H // 3 + lane * cls.H

App()
