import pygame
from random import choice, randint
from os import path
from sys import exit


def terminate():
    pygame.quit()
    exit()


def load_image(name, colorkey=None):
    fullname = path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error:
        print(f'\033[31mThere is no such image ({name})\003[0m')
        terminate()
    if colorkey:
        image.set_colorkey(image.get((0, 0)))
    else:
        image.convert_alpha()
    return image


def new_direction(direction):
    res = direction * choice(CHANCE_TO_SWAP_DIRECTION)
    return res


class Dog(pygame.sprite.Sprite):
    def __init__(self, main_time, shooted_duck, group):
        super().__init__(group)
        img_name = 'dog_' + str(min(shooted_duck, 2))
        self.image = IMAGES.get(img_name)
        self.rect = self.image.get_rect()
        self.rect.x = randint(200, WIDTH - 200)
        self.rect.y = HEIGHT - 1
        self.pos_y = HEIGHT - 1
        self.speed = -400
        self.killed = False
        self.t_stay = None

    def shooted(self, *args):
        self.killed = True
        self.image = IMAGES.get('shooted_dog')

    def update(self, *args):
        main_time, time = args
        if self.pos_y > HEIGHT:
            if self.killed:
                global dog_group
                RebornedDog(self.rect.x, dog_group)
            self.kill()
        if self.t_stay and main_time - self.t_stay < 900:
            return
        elif self.pos_y < HEIGHT - self.rect.height * 1.5:
            self.speed *= -1
            self.t_stay = main_time
            self.pos_y = HEIGHT - self.rect.height * 1.5
            return
        self.pos_y += self.speed * time / 1000
        self.rect.y = int(self.pos_y)


class RebornedDog(pygame.sprite.Sprite):
    def __init__(self, x, group):
        self.killed = True
        super().__init__(group)
        self.speed = -450
        self.image = IMAGES.get('reborned_dog')
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y, self.pos_y = x, HEIGHT, HEIGHT

    def update(self, *args):
        time = args[1]
        self.pos_y += self.speed * time / 1000
        self.rect.y = int(self.pos_y)
        if self.rect.y + self.rect.width < 0:
            global END
            pygame.mouse.set_visible(True)
            END = True
            its_end('bad_end')
            self.kill()


class Target(pygame.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)
        self.image = IMAGES.get('target')
        self.rect = self.image.get_rect()
        self.w = self.rect.width // 2
        self.h = self.rect.height // 2

    def update(self):
        x, y = pygame.mouse.get_pos()
        self.rect.x = x - self.w
        self.rect.y = y - self.h


class Duck(pygame.sprite.Sprite):
    def __init__(self, lvl, main_time, group):
        super().__init__(group)
        self.image, self.im_num = IMAGES.get(0), 0
        self.last_change = main_time
        self.rect = self.image.get_rect()
        self.direction = [choice([-1, 1]), -1]
        self.lvl = lvl
        self.speed = randint(700, 900) * lvl
        self.pos_x = randint(self.rect.width + 50, WIDTH - self.rect.width - 50)
        self.pos_y = HEIGHT - self.rect.height
        self.killed = False
        self.t_killed = None

    def shooted(self, *args):
        main_time = args[0]
        self.killed = True
        self.t_killed = main_time
        self.image = IMAGES.get('shooted_duck')

    def update(self, *args):
        main_time, time = args
        if self.killed:
            if main_time - self.t_killed > 200:
                if self.pos_y < HEIGHT:
                    self.pos_y += 2 * time
                    self.rect.y = int(self.pos_y)
                else:
                    global count_dead_ducks, shooted_ducks
                    count_dead_ducks += 1
                    shooted_ducks += 1
                    self.kill()
            return
        if (main_time - self.last_change) * self.lvl > 160:
            self.last_change = main_time
            self.im_num = ((self.im_num + 1) % 3)
            self.image = IMAGES.get(self.im_num)
            if self.direction[0] > 0:
                self.image = pygame.transform.flip(self.image, True, False)
        if 0 > self.rect.x:
            self.rect.x = self.pos_x = 1
            self.direction[0] *= -1
        elif self.rect.x + self.rect.width > WIDTH:
            self.rect.x = self.pos_x = WIDTH - self.rect.width - 1
            self.direction[0] *= -1
        if 0 > self.rect.y:
            self.rect.y = self.pos_y = 1
            self.direction[1] *= -1
        elif self.rect.y + self.rect.height > HEIGHT:
            self.rect.y = self.pos_y = HEIGHT - self.rect.height - 1
            self.direction[1] *= -1

        x, y = self.direction
        self.pos_x += x * self.speed * time / 1000
        self.pos_y += y * self.speed * time / 1000
        self.rect.x = int(self.pos_x)
        self.rect.y = int(self.pos_y)
        self.direction = [new_direction(x), y]


class ShootedCells(pygame.sprite.Sprite):
    def __init__(self, main_time, pos, group):
        super().__init__(group)
        self.image = IMAGES.get('shoot')
        self.rect = self.image.get_rect()
        self.rect.x = pos[0] - self.rect.width // 2
        self.rect.y = pos[1] - self.rect.height // 2
        self.born_time = main_time

    def update(self, *args):
        main_time = args[0]
        if main_time - self.born_time > 70:
            self.kill()


def its_end(end_type):
    SCREEN.blit(IMAGES.get(end_type), (0, 0))


def first_screen():
    class button(pygame.sprite.Sprite):
        def __init__(self, surfnum, strnum, x, y, group):
            super().__init__(group)
            self.num = float('1.' + strnum)
            surf = pygame.Surface((160, 50))
            surf.fill((222, 184, 0))
            surf.blit(surfnum, (35, 15))
            self.image = surf
            self.rect = self.image.get_rect()
            self.rect.x, self.rect.y = x, y
    global SCREEN
    font = pygame.font.Font(None, 30)
    butts_group = pygame.sprite.Group()
    x, y = 40, 320
    for j in range(3):
        for i in range(j * 3 + 1, j * 3 + 4):
            button(font.render(str(i) + ' уровень', 1, (0, 0, 0)), str(i), x, y, butts_group)
            y += 70
        x += 200
        y = 320
    INTRO_TEXT = ['DUCK HUNT', '',
                  '0. Уровень определяет скорость движения уток.',
                  '1. Вам нужно сбить как можно больше уток.',
                  '2. Чтобы выстрелить из ружья нажимайте левую кнопку мыши.',
                  '3. Для продолжения выберите уровень или нажмите на любую клавишу.']
    background = IMAGES['first_screen']
    SCREEN.blit(background, (0, 0))
    surf = pygame.Surface((WIDTH, HEIGHT))
    surf.fill((0, 0, 0))
    surf.set_alpha(160)
    SCREEN.blit(surf, (0, 0))
    text_y_coord = 120
    for line in INTRO_TEXT:
        line = font.render(line, True, (222, 184, 0))
        rect = line.get_rect()
        rect.x, rect.y = 40, text_y_coord
        text_y_coord += rect.height + 10
        SCREEN.blit(line, rect)
    butts_group.draw(SCREEN)
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                lvl = pygame.sprite.spritecollideany(target, butts_group)
                return float(lvl.num) if lvl else 1.1
        target.update()


def main_screen(lvl):
    global SCREEN, END, count_dead_ducks, shooted_ducks, dog_group
    shoots_group = pygame.sprite.Group()
    duck_group = pygame.sprite.Group()
    pygame.mouse.set_visible(False)
    CLOCK = pygame.time.Clock()
    FONT = pygame.font.Font(None, 60)
    FPS = 60
    DOG_TIME = 1
    pygame.time.set_timer(DOG_TIME, 7500)
    while True:
        main_time = pygame.time.get_ticks()
        if len(duck_group.sprites()) < 3 and not END:
            Duck(lvl, main_time, duck_group)
            if count_dead_ducks == 15:
                pygame.mouse.set_visible(True)
                END = True
                its_end('good_end')
                SCREEN.blit(FONT.render(str(count_dead_ducks), True, (0, 0, 0)), (10, 10))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if END:
                continue
            if event.type == DOG_TIME and not dog_group.sprites():
                Dog(main_time, shooted_ducks, dog_group)
                shooted_ducks = 0
            if event.type == pygame.MOUSEBUTTONDOWN:
                ShootedCells(main_time, event.pos, shoots_group)
                for duck in duck_group.sprites():
                    if pygame.sprite.collide_mask(target, duck):
                        duck.shooted(main_time)
                        break
                dog = dog_group.sprites()
                if dog and not dog[0].killed and pygame.sprite.collide_mask(dog[0], target):
                    dog[0].shooted(main_time)
        if not END:
            target.update()
            SCREEN.blit(IMAGES.get('background'), (0, 0))
            time = CLOCK.tick()
            dog_group.update(main_time, time)
            duck_group.update(main_time, time)
            shoots_group.update(main_time, time)
            duck_group.draw(SCREEN)
            dog_group.draw(SCREEN)
            SCREEN.blit(IMAGES.get('frontground'), (0, 0))
            SCREEN.blit(FONT.render(str(count_dead_ducks), True, (0, 0, 0)), (10, 10))
            shoots_group.draw(SCREEN)
            target_group.draw(SCREEN)
        CLOCK.tick(FPS)
        pygame.display.flip()


def main():
    pygame.init()
    lvl = first_screen()
    main_screen(lvl)


if __name__ == "__main__":
    WIDTH, HEIGHT = 1280, 720
    SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
    END = False
    CHANCE_TO_SWAP_DIRECTION = [1] * 95 + [-1] * 5
    IMAGES = {"frontground": pygame.transform.scale(load_image('frontground.png'), (WIDTH, HEIGHT)),
              "background": pygame.transform.scale(load_image('background.png'), (WIDTH, HEIGHT)),
              "shoot": pygame.transform.scale(load_image('shoot.png'), (40, 40)),
              0: load_image('duck_1.png'),
              1: load_image('duck_2.png'),
              2: load_image('duck_3.png'),
              "shooted_duck": load_image('dead_duck.png'),
              "dog_0": load_image('dog.png'),
              "dog_1": load_image('dog_with_duck.png'),
              "dog_2": load_image('dog_with_ducks.png'),
              "shooted_dog": load_image('shooted_dog.png'),
              "reborned_dog": load_image('dead_dog.png'),
              "first_screen": pygame.transform.scale(load_image('first_screen.png'), (WIDTH, HEIGHT)),
              "target": pygame.transform.scale(load_image('target.png'), (40, 40)),
              "bad_end": load_image('bad_end.png'),
              "good_end": load_image('good_end.png')}
    shooted_ducks = count_dead_ducks = 0
    dog_group = pygame.sprite.Group()
    target_group = pygame.sprite.GroupSingle()
    target = Target(target_group)
    main()
