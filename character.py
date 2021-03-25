import pygame


class Character:  # Статичный персонаж
    def __init__(self, x, y, img_src='', width='16', height='16'):  # x, y - координаты, img_src - спрайт
        self.visible = True
        self.pause = False
        self.x = x
        self.y = y
        self.object = pygame.image.load(img_src)
        self.object_rect = self.object.get_rect()
        self.width = width
        self.height = height
        self.angle = 0
        self.set_position(self.x, self.y)
        self.rect = pygame.Rect(x, y, width, height)

    def set_x(self, x):  # Задать координату X
        self.x = x
        self.object_rect.x = self.x

    def set_y(self, y):  # Задать координату Y
        self.y = y
        self.object_rect.y = self.y

    def set_position(self, x, y):  # Задать координаты X и Y
        self.set_x(x)
        self.set_y(y)

    def set_width(self, width):  # Задать ширину
        self.width = width
        self.set_size(self.width, self.height)

    def set_height(self, height):  # Задать высоту
        self.height = height
        self.set_size(self.width, self.height)

    def set_size(self, width, height):  # Задать ширину и высоту
        self.width = width
        self.height = height
        self.object = pygame.transform.scale(self.object, (self.width, self.height))

    def set_rotation(self, angle):  # Задать угол поворота (только 0, 90, 180, 270 градусов, ибо растровая картинка)
        self.object = pygame.transform.rotate(self.object, -self.angle)
        self.object = pygame.transform.rotate(self.object, -angle + self.angle)
        self.angle += angle - self.angle

    def get_rotation(self):  # Вернуть угол поворота
        return self.angle

    def set_image(self, img_src, width=None, height=None):  # Задать изображение спрайта
        self.object = pygame.image.load(img_src)
        self.object_rect = self.object.get_rect()

    def draw(self, screen):  # Вывод на экран
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        screen.blit(self.object, self.object_rect)


class AnimatedCharacter(Character):  # Анимированный персонаж
    def __init__(self, x, y, img_src='', sprites_cnt=1, width=16, height=16, loop=True,
                 time=1):  # img_src - изображение с набором спрайтов (без отступов, в один ряд), sprites_cnt -
        # количество спрайтов, loop - зацикливание анимации, time - время анимации
        super().__init__(x, y, img_src, width, height)
        self.original_time = time
        self.set_animation(img_src, sprites_cnt, loop, time)
        self.object = self.sprites[0]
        self.object_rect = self.sprites[0].get_rect()
        self.set_position(self.x, self.y)
        self.end = False

    def split_sprites(self, img_src, sprites_cnt=None, first_sprite=0,
                      last_sprite=-1):  # Разделение изображения img_src на спрайты
        if sprites_cnt is not None:
            self.sprites_cnt = sprites_cnt
        if last_sprite == -1:
            last_sprite = self.sprites_cnt
        sprites = []
        for c in range(first_sprite, last_sprite):
            sprites.append(img_src.subsurface((c * self.sprite_width, 0, self.sprite_width, self.sprite_height)))
        return sprites

    def update(self, dt):  # Обновление кадров анимации
        self.work_time += dt
        self.skip_frame = self.work_time // self.time
        if self.skip_frame > 0:
            self.work_time = self.work_time % self.time
            self.frame += self.skip_frame
            if self.frame >= len(self.sprites):
                if self.loop:
                    self.frame = 0
                else:
                    self.end = True

    def get_sprite(self):  # Вернуть спрайт
        try:
            return self.sprites[self.frame]
        except: return self.sprites[0]

    def set_animation(self, img_src, sprites_cnt, loop=True, time=1):  # Задать изображение со спрайтами
        self.img_src = pygame.image.load(img_src)
        self.sprite_width = self.img_src.get_rect().width // sprites_cnt
        self.sprite_height = self.img_src.get_rect().height
        self.sprites_cnt = sprites_cnt
        self.time = time
        self.work_time = 0
        self.skip_frame = 0
        self.frame = 0
        self.loop = loop
        self.sprites = self.split_sprites(self.img_src)

    def set_split_sprites_range(self, first_sprite, last_sprite):  # Задать диапазон для разделения спрайтов
        self.sprites_cnt = last_sprite - first_sprite - 1
        self.sprites = self.split_sprites(self.img_src, self.sprites_cnt, first_sprite - 1, last_sprite)

    def get_image_parts(self, img_src):
        height = pygame.image.load(img_src).get_rect().height
        width = pygame.image.load(img_src).get_rect().width
        return width // height

    def draw(self, screen, upd_time=1):  # Вывод на экран
        if self.visible:
            self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
            if not self.end:
                self.object = self.get_sprite()
                self.update(upd_time)
                self.set_rotation(self.angle)
                screen.blit(pygame.transform.scale(self.object, (self.width, self.height)), self.object_rect)
