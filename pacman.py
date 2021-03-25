from character import AnimatedCharacter
import pygame


class Pacman(AnimatedCharacter):
    def __init__(self, x, y, width, height, speed=3, time=1,
                 start_img_path="./texturepacks/Classic/pacman/pacman_eat.png"):
        super().__init__(x, y, start_img_path, 4, width, height, True, time)
        self.movement_direction = 0  # 0 - стоит на месте, 1 - движется вверх, 2 - вниз, 3 - влево, 4 - вправов
        self.movement_direction_queue = 0  # 0 - стоит на месте, 1 - движется вверх, 2 - вниз, 3 - влево, 4 - вправов
        self.animation_status = 0  # 0 - есть, 1 - анимация смерти, 2 - стоять
        self.vertical_speed = 0
        self.horisontal_speed = 0
        self.absolute_speed = speed
        self.map = map

        self.texture_stand = None
        self.texture_eat = None
        self.texture_death = None

    def change_direction(self, map):  # Проверка на возможность поворота
        self.set_eat_animation()
        if self.movement_direction_queue == 3 and map[(self.y + 16 - 48) // 16][(self.x - 2) // 16] != "0":
            self.movement_direction = 3
            self.movement_direction_queue = 0
        elif self.movement_direction_queue == 4 and map[(self.y + 16 - 48) // 16][(self.x + 34) // 16] != "0":
            self.movement_direction = 4
            self.movement_direction_queue = 0
        elif self.movement_direction_queue == 1 and map[(self.y - 44) // 16][(self.x + 16) // 16] != "0":
            self.movement_direction = 1
            self.movement_direction_queue = 0
        elif self.movement_direction_queue == 2 and map[(self.y - 10) // 16][(self.x + 16) // 16] != "0":
            self.movement_direction = 2
            self.movement_direction_queue = 0

    def check_collision(self, map):  # Проверка на столкновение со стенами
        if self.movement_direction == 3 and map[(self.y + 16 - 48) // 16][(self.x + 6) // 16] != "0":
            self.set_rotation(270)  # Поворот изображения до 270
            self.set_y(self.y // 16 * 16 + 8)
            self.vertical_speed = 0
            self.horisontal_speed = -self.absolute_speed
        elif self.movement_direction == 4 and map[(self.y + 16 - 48) // 16][(self.x + 26) // 16] != "0":
            self.set_rotation(90)  # Поворот изображения до 90
            self.set_y(self.y // 16 * 16 + 8)
            self.vertical_speed = 0
            self.horisontal_speed = self.absolute_speed
        elif self.movement_direction == 1 and map[(self.y - 42) // 16][(self.x + 16) // 16] != "0":
            self.set_rotation(0)  # Поворот изображения до 0
            self.set_x(self.x // 16 * 16 + 8)
            self.vertical_speed = -self.absolute_speed
            self.horisontal_speed = 0
        elif self.movement_direction == 2 and map[(self.y - 22) // 16][(self.x + 16) // 16] != "0":
            self.set_rotation(180)  # Поворот изображения до 180
            self.set_x(self.x // 16 * 16 + 8)
            self.vertical_speed = self.absolute_speed
            self.horisontal_speed = 0
        else:
            self.horisontal_speed = 0
            self.vertical_speed = 0
            self.movement_direction = 0
            self.set_stand_animation()

    def check_event(self, event):  # Проверка событий
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w or event.key == pygame.K_UP:  # Идти вверх
                self.movement_direction_queue = 1
            elif event.key == pygame.K_a or event.key == pygame.K_LEFT:  # Идти влево
                self.movement_direction_queue = 3
            elif event.key == pygame.K_s or event.key == pygame.K_DOWN:  # Идти вниз
                self.movement_direction_queue = 2
            elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:  # Идти вправо
                self.movement_direction_queue = 4

    def position_logic(self):  # Изменение положения пакмана с учётом телепортов
        if self.x > 448:
            self.set_position(-self.width, self.y + self.vertical_speed)
        if self.x < -self.width:
            self.set_position(440, self.y + self.vertical_speed)
        else:
            self.set_position(self.x + self.horisontal_speed, self.y + self.vertical_speed)

    def move(self, map):  # Движение
        if not self.pause:
            try:
                self.change_direction(map)
            except IndexError:
                pass
            try:
                self.check_collision(map)
            except IndexError:
                pass
            self.position_logic()

    def set_eat_animation(self):
        if self.animation_status == 2 or self.animation_status == 1:
            self.animation_status = 0
            self.set_animation(self.texture_eat, self.get_image_parts(self.texture_eat), True, self.original_time)

    def set_death_animation(self):
        if not self.animation_status == 1:
            self.animation_status = 1
            self.set_animation(self.texture_death, self.get_image_parts(self.texture_death), False, self.original_time*2)

    def set_stand_animation(self):
        if self.animation_status == 0 or self.animation_status == 1:
            self.animation_status = 2
            self.set_animation(self.texture_stand, 1)

    def get_pos(self):
        return self.x, self.y

    def get_pacman_cell(self):  # Возвращает клетку, в которой находится пакман сейчас в виде колонка, строка
        return (self.x + 16) // 16, (self.y - 40) // 16

    def draw(self, screen, upd_time=1):
        super().draw(screen, upd_time)
        if self.pause:
            self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        else:
            self.rect = pygame.Rect(self.x + self.width/4, self.y + self.height/4, self.width/2, self.height/2)
