from datetime import datetime, timedelta
from random import randint, random, choice

import pyxel

WINDOW_WIDTH = 240
WINDOW_HEIGHT = 240


def center(text, width):
    """
    文章を中央揃えで表示する際のx座標を返す
    :param text: 座標を得たい文章
    :param width: 画面の幅
    :return:
    """
    TEXT_W = 4
    return width // 2 - len(text) * TEXT_W // 2


class App:
    INIT_SCROLL_SPEED = 2
    MAX_SCROLL_SPEED = 5
    SCROLL_SPEED_RATE = 3

    GOAL = 10000

    def __init__(self):
        pyxel.init(WINDOW_WIDTH, WINDOW_HEIGHT)
        pyxel.load('./assets/my_resource.pyxres')
        self.rabbit = Rabbit()
        self.carrots = []
        self.rocks = []
        self.road = Road()
        self.progress_bar = ProgressBar()
        self.start_screen = StartScreen()
        self.clear_screen = ClearScreen()
        self.button = Button()
        self.ura_command = UraCommand()
        self.scroll_speed = self.INIT_SCROLL_SPEED
        self.scroll_speed_count = 0
        self.progress = 0
        self.state = 'start'
        self.mode = 'normal'
        self.start_time = datetime.now()
        self.time_display = None
        self.how_to_play = HowToPlayDisplay('start')
        self.effects = []
        pyxel.run(self.update, self.draw)

    def update(self):
        self.button.update()
        if self.state == 'start':
            if self.ura_command.update(self.button.get_input()):
                self.mode = 'hard'
            self.rabbit.move_center()
            if self.start_screen.update(self.button.get_input(), self.how_to_play):
                self.state = 'play'
                self.start_time = datetime.now()
                self.how_to_play.change_message('run')
                self.rabbit.move_left()
        elif self.state == 'play':
            if self.mode == 'normal':
                self.scroll_speed = min(self.INIT_SCROLL_SPEED + self.scroll_speed_count // self.SCROLL_SPEED_RATE, self.MAX_SCROLL_SPEED)
            elif self.mode == 'hard':
                self.scroll_speed = self.INIT_SCROLL_SPEED + self.scroll_speed_count // self.SCROLL_SPEED_RATE
            else:
                self.scroll_speed = min(self.INIT_SCROLL_SPEED + self.scroll_speed_count // self.SCROLL_SPEED_RATE,
                                        self.MAX_SCROLL_SPEED)
            self.progress += self.scroll_speed
            self.rabbit.update(self.button.get_input())
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
            if self.progress > self.GOAL:
                self.state = 'clear'
                self.time_display = TimeDisplay(datetime.now() - self.start_time)
                self.how_to_play.change_message('clear')
                self.rabbit.move_center()
        elif self.state == 'clear':
            self.effects.append(Effect.create_random())
            if pyxel.btn(pyxel.KEY_B) or self.button.get_input() == (Button.INPUT_DECIDE, Button.INPUT_RELEASE):
                self.state = 'start'
                self.how_to_play.change_message('start')
                self.init_game()
        for effect in self.effects:
            effect.update()
        self.effects = [effect for effect in self.effects if effect.alive]

    def init_game(self):
        self.rabbit = Rabbit()
        self.carrots = []
        self.rocks = []
        self.road = Road()
        self.progress_bar = ProgressBar()
        self.start_screen = StartScreen()
        self.clear_screen = ClearScreen()
        self.scroll_speed = self.INIT_SCROLL_SPEED
        self.scroll_speed_count = 0
        self.progress = 0
        self.state = 'start'
        self.start_time = datetime.now()
        self.time_display = None
        self.how_to_play = HowToPlayDisplay('start')
        self.ura_command = UraCommand()

    def draw(self):
        if self.mode == 'normal':
            image = 0
        elif self.mode == 'hard':
            image = 1
        else:
            image = 0
        pyxel.cls(0)
        if self.state == 'start':
            self.road.draw(image)
            self.start_screen.draw(image)
            self.rabbit.draw(image)
        elif self.state == 'play':
            self.road.draw(image)
            for carrot in self.carrots:
                carrot.draw(image)
            for rock in self.rocks:
                rock.draw(image)
            self.rabbit.draw(image)
            self.progress_bar.draw(self.progress / self.GOAL, image)
        elif self.state == 'clear':
            self.road.draw(image)
            self.clear_screen.draw(image)
            self.rabbit.draw(image)
            self.time_display.draw(image)
        self.how_to_play.draw()
        self.button.draw()
        for effect in self.effects:
            effect.draw()


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
    MOVE_ANIMATION_TIME = 3

    def __init__(self):
        self.x = self.INIT_START_X
        self.lane = self.INIT_LANE
        self.y = Road.lane_to_height(self.lane)
        self.state = 'run'
        self.state_count_time = 0
        self.move_count_time = 0

    def update(self, button_input):
        if self.move_count_time == 0:
            key_input = 0
            if pyxel.btn(pyxel.KEY_W) or button_input[0] == Button.INPUT_UP:
                pyxel.play(0, 1)
                key_input -= 1
            if pyxel.btn(pyxel.KEY_S) or button_input[0] == Button.INPUT_DOWN:
                pyxel.play(0, 2)
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
            pyxel.play(0, 3)
            pyxel.play(1, 4)
            self.state = 'hit'
            self.state_count_time = self.HIT_ANIMATION_TIME

    def move_center(self):
        self.x = WINDOW_WIDTH // 2 - self.RUN_W // 2
        self.y = WINDOW_HEIGHT // 2 - self.RUN_H // 2

    def move_left(self):
        self.x = self.INIT_START_X
        self.y = Road.lane_to_height(self.lane)

    def draw(self, image=0):
        if self.state == 'run':
            pyxel.blt(self.x, self.y, image, self.RUN_U, self.RUN_V, self.RUN_W, self.RUN_H, 2)
        elif self.state == 'hit' and pyxel.frame_count % 4 < 3:
            pyxel.blt(self.x, self.y, image, self.HIT_U, self.HIT_V, self.HIT_W, self.HIT_H, 2)


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
            pyxel.play(0, 0)
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

    def draw(self, image=0):
        pyxel.blt(self.x, self.y, image, self.U, self.V, self.W, self.H, 2)


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

    def draw(self, image=0):
        pyxel.blt(self.x, self.y, image, self.U, self.V, self.W, self.H, 2)


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

    def draw(self, image=0):
        for column, lane in enumerate(self.lanes):
            for i in range(WINDOW_WIDTH // (self.W * self.ROW) + 3):
                pyxel.blt(i * (self.W * self.ROW) - lane * self.W - self.scroll, column * self.H, image, self.U, self.V, (self.W * self.ROW), self.H, 2)

    @classmethod
    def lane_to_height(cls, lane):
        return cls.H // 3 + lane * cls.H


class ProgressBar:
    U = 0
    V = 160
    W = 96
    H = 16

    X = (WINDOW_HEIGHT - W) // 2
    Y = 2

    BAR_U = 5
    BAR_V = 11
    BAR_WIDTH = 85
    BAR_HEIGHT = 4
    BAR_COLOR = 8

    def draw(self, progress_percent, image=0):
        progress_percent = min(1, max(0, progress_percent))
        pyxel.blt(self.X, self.Y, image, self.U, self.V, self.W, self.H, 2)
        length = int(self.BAR_WIDTH * progress_percent)
        pyxel.rect(self.X + self.BAR_U, self.Y + self.BAR_V, length, self.BAR_HEIGHT, self.BAR_COLOR)


class ClearScreen:
    U = 0
    V = 176
    W = 128
    H = 48

    X = (WINDOW_HEIGHT - W) // 2
    Y = WINDOW_HEIGHT // 4 - H // 2

    def draw(self, image=0):
        pyxel.blt(self.X, self.Y, image, self.U, self.V, self.W, self.H, 2)


class StartScreen:
    U = 128
    V = 176
    W = 128
    H = 48

    X = (WINDOW_HEIGHT - W) // 2
    Y = WINDOW_HEIGHT // 4 - H // 2

    NEWYEAR_TIME = datetime(2023, 1, 1)
    # NEWYEAR_TIME = datetime.now() + timedelta(minutes=1)
    print(NEWYEAR_TIME)

    def __init__(self):
        self.selection = 0
        self.state = 'start'

    def update(self, button_input, how_to_play):
        if self.state == 'start':
            if pyxel.btn(pyxel.KEY_SPACE) or button_input == (Button.INPUT_DECIDE, Button.INPUT_RELEASE):
                if self.selection == 0:
                    return True
                else:
                    self.state = 'wait'
                    how_to_play.change_message('clear')
                    return False
            key_input = 0
            if pyxel.btnr(pyxel.KEY_W) or button_input == (Button.INPUT_UP, Button.INPUT_RELEASE):
                key_input -= 1
            if pyxel.btnr(pyxel.KEY_S) or button_input == (Button.INPUT_DOWN, Button.INPUT_RELEASE):
                key_input += 1
            self.selection += key_input
            self.selection = self.selection % 2
        elif self.state == 'wait':
            if pyxel.btn(pyxel.KEY_B) or button_input == (Button.INPUT_DECIDE, Button.INPUT_RELEASE):
                how_to_play.change_message('start')
                self.state = 'start'
            if self.NEWYEAR_TIME <= datetime.now():
                return True

    def draw(self, image=0):
        pyxel.blt(self.X, self.Y, image, self.U, self.V, self.W, self.H, 2)
        if self.state == 'start':
            msg = 'Play Normal Run Mode'
            pyxel.text(center(msg, WINDOW_WIDTH) + 1, WINDOW_HEIGHT // 4 * 3 + 1, msg, 0)
            pyxel.text(center(msg, WINDOW_WIDTH), WINDOW_HEIGHT // 4 * 3, msg, 7)
            if self.selection == 0:
                pyxel.text(center(msg, WINDOW_WIDTH) - 15, WINDOW_HEIGHT // 4 * 3, '>>>', 9)
                pyxel.text(center(msg, WINDOW_WIDTH) - 14, WINDOW_HEIGHT // 4 * 3, '>>>', 9)
            msg = 'Play Happy New Year Run Mode'
            pyxel.text(center(msg, WINDOW_WIDTH) + 1, WINDOW_HEIGHT // 4 * 3 + 11, msg, 0)
            pyxel.text(center(msg, WINDOW_WIDTH), WINDOW_HEIGHT // 4 * 3 + 10, msg, 7)
            if self.selection == 1:
                pyxel.text(center(msg, WINDOW_WIDTH) - 15, WINDOW_HEIGHT // 4 * 3 + 10, '>>>', 9)
                pyxel.text(center(msg, WINDOW_WIDTH) - 14, WINDOW_HEIGHT // 4 * 3 + 10, '>>>', 9)
        elif self.state == 'wait':
            time = TimeDisplay(self.NEWYEAR_TIME - datetime.now())
            time.draw()


class TimeDisplay:
    U = 16
    V = 224
    W = 16
    H = 32

    def __init__(self, time):
        self.time = str(time)
        if time.days == 0:
            self.time = self.time[:self.time.find('.')]
        else:
            self.time = str(time.days) + self.time[self.time.find(','):self.time.find('.')]

        self.x = WINDOW_WIDTH // 2 - len(self.time)*self.W // 2
        self.y = WINDOW_HEIGHT // 4 * 3 - self.H // 2

    def draw(self, image=0):
        pyxel.blt(self.x - self.W, self.y, image, self.U - self.W, self.V, self.W, self.H, 2)
        pyxel.blt(self.x + len(self.time) * self.W, self.y, image, self.U + 12 * self.W, self.V, self.W, self.H, 2)
        for i, c in enumerate(self.time):
            if c == '0':
                pyxel.blt(self.x + i * self.W, self.y, image, self.U, self.V, self.W, self.H, 2)
            elif c == '1':
                pyxel.blt(self.x + i * self.W, self.y, image, self.U + self.W, self.V, self.W, self.H, 2)
            elif c == '2':
                pyxel.blt(self.x + i * self.W, self.y, image, self.U + self.W * 2, self.V, self.W, self.H, 2)
            elif c == '3':
                pyxel.blt(self.x + i * self.W, self.y, image, self.U + self.W * 3, self.V, self.W, self.H, 2)
            elif c == '4':
                pyxel.blt(self.x + i * self.W, self.y, image, self.U + self.W * 4, self.V, self.W, self.H, 2)
            elif c == '5':
                pyxel.blt(self.x + i * self.W, self.y, image, self.U + self.W * 5, self.V, self.W, self.H, 2)
            elif c == '6':
                pyxel.blt(self.x + i * self.W, self.y, image, self.U + self.W * 6, self.V, self.W, self.H, 2)
            elif c == '7':
                pyxel.blt(self.x + i * self.W, self.y, image, self.U + self.W * 7, self.V, self.W, self.H, 2)
            elif c == '8':
                pyxel.blt(self.x + i * self.W, self.y, image, self.U + self.W * 8, self.V, self.W, self.H, 2)
            elif c == '9':
                pyxel.blt(self.x + i * self.W, self.y, image, self.U + self.W * 9, self.V, self.W, self.H, 2)
            elif c == ':':
                pyxel.blt(self.x + i * self.W, self.y, image, self.U + self.W * 10, self.V, self.W, self.H, 2)
            else:
                pyxel.blt(self.x + i * self.W, self.y, image, self.U + self.W * 11, self.V, self.W, self.H, 2)


class HowToPlayDisplay:
    MESSAGE = {
        'start': ['[W/S]:Move cursor', '[Space]:Select Menu'],
        'wait': ['[B]:Back to Menu'],
        'run': ['[W/S]:Move Rabbit'],
        'clear': ['[B]:Back to Menu']
    }
    X = WINDOW_WIDTH // 2
    Y = WINDOW_WIDTH // 8 * 7

    def __init__(self, message):
        self.message = message

    def change_message(self, message):
        self.message = message

    def draw(self):
        for i, msg in enumerate(self.MESSAGE[self.message]):
            pyxel.text(self.X + 1, self.Y + 1 + i * 7, msg, 0)
            pyxel.text(self.X, self.Y + i * 7, msg, 7)


class Effect:
    def __init__(self, shape, time, x, y, vx, vy, size, color):
        self.shape = shape
        self.time = time
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.size = size
        self.color = color
        self.alive = True

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.time -= 1
        if self.time < 0:
            self.alive = False

    def draw(self):
        if self.shape == 0:
            pyxel.rect(self.x, self.y, self.size, self.size, self.color)
        if self.shape == 1:
            pyxel.circ(self.x, self.y, self.size, self.color)
        if self.shape == 2:
            x1 = self.x + randint(-self.size, self.size)
            x2 = self.x + randint(-self.size, self.size)
            y1 = self.y + randint(-self.size, self.size)
            y2 = self.y + randint(-self.size, self.size)
            pyxel.tri(self.x, self.y, x1, y1, x2, y2, self.color)

    @classmethod
    def create_random(cls, shape=None, time=None, x=None, y=None, vx=None, vy=None, size=None, color=None):
        if shape is None:
            shape = randint(0, 2)
        if time is None:
            time = randint(10, 30)
        if x is None:
            x = randint(0, WINDOW_WIDTH)
        if y is None:
            y = randint(0, WINDOW_WIDTH)
        if vx is None:
            vx = randint(-5, 5)
        if vy is None:
            vy = randint(-5, 5)
        if size is None:
            size = randint(1, 10)
        if color is None:
            color = choice([1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15])
        return Effect(shape, time, x, y, vx, vy, size, color)


class Button:
    WIDTH = 50
    HEIGHT = 40

    UP_X = WINDOW_WIDTH // 4
    UP_Y = WINDOW_HEIGHT // 4 * 3

    DOWN_X = WINDOW_WIDTH // 4
    DOWN_Y = WINDOW_HEIGHT // 4 * 3 + HEIGHT + 10

    RADIUS = 25

    DECIDE_X = WINDOW_WIDTH // 4 * 3
    DECIDE_Y = UP_Y + 5

    INPUT_NONE = 0
    INPUT_UP = 1
    INPUT_DOWN = 2
    INPUT_DECIDE = 3

    INPUT_PUSH = 0
    INPUT_KEEP = 1
    INPUT_RELEASE = 2

    COLOR = 7

    def __init__(self):
        self.enable = False
        pyxel.mouse(True)
        self.input = self.INPUT_NONE
        self.before_input = self.INPUT_NONE

    def update(self):
        self.before_input = self.input
        self.input = self.INPUT_NONE
        if pyxel.btn(pyxel.MOUSE_BUTTON_LEFT):
            self.enable = True
            cx = pyxel.mouse_x
            cy = pyxel.mouse_y

            if abs(self.UP_X - cx) <= self.WIDTH // 2 and 0 <= self.UP_Y - cy <= self.HEIGHT:
                self.input = self.INPUT_UP
            if abs(self.DOWN_X - cx) <= self.WIDTH // 2 and 0 <= self.DOWN_Y - cy <= self.HEIGHT:
                self.input = self.INPUT_DOWN
            if (self.DECIDE_X - cx) ** 2 + (self.DECIDE_Y - cy) ** 2 < self.RADIUS ** 2:
                self.input = self.INPUT_DECIDE

    def get_input(self):
        if self.before_input == self.input:
            return self.input, self.INPUT_KEEP
        if self.before_input == self.INPUT_NONE:
            if self.input == self.INPUT_NONE:
                return self.input, self.INPUT_KEEP
            else:
                return self.input, self.INPUT_PUSH
        return self.before_input, self.INPUT_RELEASE

    def draw(self):
        if self.enable:
            x1 = self.UP_X
            y1 = self.UP_Y - self.HEIGHT
            x2 = self.UP_X - self.WIDTH // 2
            y2 = self.UP_Y
            x3 = self.UP_X + self.WIDTH // 2
            y3 = self.UP_Y
            pyxel.trib(x1, y1, x2, y2, x3, y3, self.COLOR)
            x1 = self.DOWN_X
            y1 = self.DOWN_Y
            x2 = self.DOWN_X - self.WIDTH // 2
            y2 = self.DOWN_Y - self.HEIGHT
            x3 = self.DOWN_X + self.WIDTH // 2
            y3 = self.DOWN_Y - self.HEIGHT
            pyxel.trib(x1, y1, x2, y2, x3, y3, self.COLOR)
            pyxel.circb(self.DECIDE_X, self.DECIDE_Y, self.RADIUS, self.COLOR)


class UraCommand:

    COMMAND = [1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 1]

    def __init__(self):
        self.key_history = []

    def update(self, button_input):
        key_input = 0
        if pyxel.btnr(pyxel.KEY_W) or button_input == (Button.INPUT_UP, Button.INPUT_RELEASE):
            key_input -= 1
        if pyxel.btnr(pyxel.KEY_S) or button_input == (Button.INPUT_DOWN, Button.INPUT_RELEASE):
            key_input += 1
        if key_input == -1:
            self.key_history.append(1)
        if key_input == 1:
            self.key_history.append(2)
        if len(self.key_history) > len(self.COMMAND):
            self.key_history.pop(0)
        if self.key_history == self.COMMAND:
            return True
        return False

App()
