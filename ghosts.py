import random
import time

from character import AnimatedCharacter
import pygame


class Ghost(AnimatedCharacter):
    def __init__(self, x, y, name, scatter_point=(0, 0), texture='Classic', width=32, height=32,
                 ghost_room_exit_point=(13, 14), time=8):
        self.name = name  # Имя призрака
        self.img = "./texturepacks/" + texture + "/ghosts/" + self.name + "_moving.png"  # Текстура преследования
        self.frightened_img = "./texturepacks/" + texture + "/ghosts/fear_moving.png"  # Текстура в состоянии страха

        super().__init__(x, y, self.img, self.get_image_parts(self.img), width, height, True, time)
        self.start_x = x  # Начальная позиция X
        self.start_y = y  # Начальная позиция Y
        self.returning_room = False  # Переменная, отвечающая за возврат призраков домой

        self.movement_direction = 0  # 0 - стоит на месте, 1 - движется вверх, 2 - вниз, 3 - влево, 4 - вправо
        self.movement_direction_queue = 0  # Очередь поворота
        self.vertical_speed = 0  # Вертикальная скорость
        self.horisontal_speed = 0  # Горизонтальная скорость
        self.normal_speed = 2  # Обычная скорость
        self.frightened_speed = 1  # Скорость при движении в состоянии испуга
        self.absolute_speed = self.normal_speed  # Абсолютная скорость
        self.returning_speed = 4  # Скорость при возврате домой
        self.current_cell = list  # Ячейка в двумерном массиве, где находится призрак
        self.ghost_room_exit_point = ghost_room_exit_point  # Координата точки выхода из дома
        self.ghost_status = 0  # 0 - режим преследования, 1 - режим разбегания, 2 - режим страха,
        # 3 - режим возвращения домой
        self.inside_ghost_house = True  # Переменная, отвечающая за нахождение призрака внутри дома
        self.scatter_point = scatter_point  # Точка, к которой стремится призрак во время разбегания
        self.inside_room_moving_direction = 1  # Движение внутри дома. 1 - вверх, -1 - вниз
        self.inside_room_start_moving = False  # Начинал ли призрак двигаться
        self.inside_house_time = 0
        self.inside_waiting_time = 0

    def set_moving_animation(self, direction):  # Изменить текстуру направления призрака
        if self.ghost_status < 2:
            if direction == 1:
                self.movement_direction = 1
                self.set_split_sprites_range(5, 6)
            if direction == 2:
                self.movement_direction = 2
                self.set_split_sprites_range(7, 8)
            if direction == 3:
                self.movement_direction = 3
                self.set_split_sprites_range(3, 4)
            if direction == 4:
                self.movement_direction = 4
                self.set_split_sprites_range(1, 2)
        if self.ghost_status == 3:
            if direction == 1:
                self.set_split_sprites_range(3, 3)
            if direction == 2:
                self.movement_direction = 2
                self.set_split_sprites_range(4, 4)
            if direction == 3:
                self.movement_direction = 3
                self.set_split_sprites_range(2, 2)
            if direction == 4:
                self.movement_direction = 4
                self.set_split_sprites_range(1, 1)

    def change_direction(self, map):  # Проверка на возможность поворота
        if self.movement_direction_queue == 3 and map[(self.y + 8 - 48) // 16][(self.x - 2) // 16] != "0":
            self.movement_direction = 3
            self.movement_direction_queue = 0
        elif self.movement_direction_queue == 4 and map[(self.y + 8 - 48) // 16][(self.x + 34) // 16] != "0":
            self.movement_direction = 4
            self.movement_direction_queue = 0
        elif self.movement_direction_queue == 1 and \
                ((map[(self.y - 44) // 16][(self.x + 8) // 16] != "0" and self.movement_direction == 4)
                 or (map[(self.y - 44) // 16][(self.x + 22) // 16] != "0" and self.movement_direction == 3)):
            self.movement_direction = 1
            self.movement_direction_queue = 0
        elif self.movement_direction_queue == 2 and \
                ((map[(self.y - 10) // 16][(self.x + 8) // 16] != "0" and self.movement_direction == 4)
                 or (map[(self.y - 10) // 16][(self.x + 22) // 16] != "0" and self.movement_direction == 3)):
            self.movement_direction = 2
            self.movement_direction_queue = 0

    def check_collision(self, map):  # Проверка на столкновение со стенами
        if self.movement_direction == 3 and map[(self.y + 16 - 48) // 16][(self.x + 6) // 16] != "0":
            self.set_y(self.y // 16 * 16 + 8)
            self.vertical_speed = 0
            self.horisontal_speed = -self.absolute_speed
        elif self.movement_direction == 4 and map[(self.y + 16 - 48) // 16][(self.x + 26) // 16] != "0":
            self.set_y(self.y // 16 * 16 + 8)
            self.vertical_speed = 0
            self.horisontal_speed = self.absolute_speed
        elif self.movement_direction == 1 and map[(self.y - 42) // 16][(self.x + 16) // 16] != "0":
            self.set_x(self.x // 16 * 16 + 8)
            self.vertical_speed = -self.absolute_speed
            self.horisontal_speed = 0
        elif self.movement_direction == 2 and map[(self.y - 24) // 16][(self.x + 16) // 16] != "0":
            self.set_x(self.x // 16 * 16 + 8)
            self.vertical_speed = self.absolute_speed
            self.horisontal_speed = 0

    def position_logic(self):  # Изменение положения пакмана с учётом телепортов
        if self.x > 448:
            self.set_position(-self.width, self.y + self.vertical_speed)
        if self.x < -self.width:
            self.set_position(440, self.y + self.vertical_speed)
        elif self.movement_direction > 0:
            self.set_position(self.x + self.horisontal_speed, self.y + self.vertical_speed)

    def get_ghost_cell(self):
        return (self.x + 16) // 16, (self.y - 40) // 16

    def move(self, map):  # Движение
        self.set_moving_animation(self.movement_direction)
        if not self.pause:
            if not self.inside_ghost_house:
                try:
                    self.change_direction(map)
                except IndexError:
                    pass
                try:
                    self.check_collision(map)
                except IndexError:
                    pass
                self.position_logic()
            else:
                if self.x != self.start_x and self.y != self.start_y:
                    self.inside_room_start_moving = True
                else:
                    self.inside_room_start_moving = False
                self.ghost_room_exit(map)

    def set_chase_mode(self, map, target_position):  # Двигаться к точке target_position
        try:
            pos = self.get_ghost_cell()  # Текущая позиция призрака
            minimum_distance = 1000  # Переменная, которая участвует в поиске наиименьшего пути до цели
            direction = 0
            if map[pos[1]][pos[0] - 1] != '0' and self.get_points_distance((target_position[1], target_position[0]),
                                                                           (pos[1], pos[0] - 1)) <= minimum_distance \
                    and self.movement_direction != 4 and self.current_cell != pos:  # Возможность поворота в лев сторону
                direction = 3
                minimum_distance = self.get_points_distance((target_position[1], target_position[0]),
                                                            (pos[1], pos[0] - 1))

            if map[pos[1]][pos[0] + 1] != '0' and self.get_points_distance((target_position[1], target_position[0]), (
                    pos[1], pos[0] + 1)) <= minimum_distance and self.movement_direction != 3\
                    and self.current_cell != pos:  # Возможность поворота в правую сторону
                direction = 4
                minimum_distance = self.get_points_distance((target_position[1], target_position[0]),
                                                            (pos[1], pos[0] + 1))

            if map[pos[1] + 1][pos[0]] != '0' and self.get_points_distance((target_position[1], target_position[0]), (
                    pos[1] + 1, pos[0])) <= minimum_distance and self.movement_direction != 1\
                    and self.current_cell != pos:  # Возможность поворота вниз
                direction = 2
                minimum_distance = self.get_points_distance((target_position[1], target_position[0]),
                                                            (pos[1] + 1, pos[0]))

            if map[pos[1] - 1][pos[0]] != '0' and self.get_points_distance((target_position[1], target_position[0]), (
                    pos[1] - 1, pos[0])) <= minimum_distance and self.movement_direction != 2\
                    and self.current_cell != pos:  # Возможность поворота вверх
                direction = 1
                minimum_distance = self.get_points_distance((target_position[1], target_position[0]),
                                                            (pos[1] - 1, pos[0]))

            # Выбор стороны, в которую можно повернуть
            if direction > 0:
                self.current_cell = pos
                if self.movement_direction == 0:
                    self.movement_direction_queue = direction
                if self.movement_direction == 1 and direction != 2:
                    self.movement_direction_queue = direction
                if self.movement_direction == 2 and direction != 1:
                    self.movement_direction_queue = direction
                if self.movement_direction == 3 and direction != 4:
                    self.movement_direction_queue = direction
                if self.movement_direction == 4 and direction != 3:
                    self.movement_direction_queue = direction
        except IndexError:
            pass

    def ghost_room_exit(self, map):  # Настраивается выход из дома призраков
        if self.inside_ghost_house and not self.returning_room and \
                not self.pause and time.time() - self.inside_house_time > self.inside_waiting_time:
            self.inside_room_start_moving = True
            if abs((self.ghost_room_exit_point[0] * 16) - self.x) >= self.absolute_speed:
                # Двигаемся по X, до момента, когда координаты выхода из дома и самого призрака не совпадут
                direct = ((self.ghost_room_exit_point[0] * 16) - self.x) / abs(
                    (self.ghost_room_exit_point[0] * 16) - self.x)  # Определение направления движения
                self.set_x(int(self.x + direct * self.absolute_speed))  # Изменение координаты X
                if direct > 0:
                    self.set_moving_animation(4)  # Задаёт анимацию движения в правую сторону
                else:
                    self.set_moving_animation(3)  # Задаёт анимацию движения в левую сторону
            elif self.y > (self.ghost_room_exit_point[1] - 1) * 16 + 10:  # Двигаемся по Y до момента выхода из комнаты
                self.set_y(self.y - self.absolute_speed)
                self.set_x((self.ghost_room_exit_point[0] * 16))
                self.set_moving_animation(1)  # Задаёт анимацию движения вверх
            else:  # Если призрак вышел из дома
                self.inside_ghost_house = False
                self.movement_direction = 1
                if self.ghost_status == 2:
                    self.movement_direction = 1
                    self.set_frightened_mode(map)

    def ghost_room_enter(self, map):  # Настраивается возвращение на начальную позицию для призрака
        if not self.pause:
            self.inside_ghost_house = True
            if self.y < self.start_y:  # Двигаемся по Y до start_y
                self.set_y(self.y + self.absolute_speed)
                self.set_moving_animation(2)
            elif abs(self.start_x - self.x) >= self.absolute_speed:  # Двигаемся по X до start_x
                direct = (self.start_x - self.x) / abs(self.start_x - self.x)  # Определение направления движения
                self.set_x(int(self.x + direct * self.absolute_speed))  # Изменение координаты X
                if direct > 0:
                    self.set_moving_animation(4)  # Задаёт анимацию движения в правую сторону
                else:
                    self.set_moving_animation(3)  # Задаёт анимацию движения в левую сторону
            else:
                self.inside_house_time = time.time()
                self.inside_room_start_moving = False
                self.inside_ghost_house = True
                self.returning_room = False
                self.set_scatter_img()
                self.ghost_status = 1
                self.ghost_status = 0
                self.move(map)

    def set_scatter_mode(self, map):  # Состояние разбегания призраков
        self.set_chase_mode(map, self.scatter_point)  # Двигаться к назначеной точке

    def set_frightened_mode(self, map, blink=False):  # Режим испуга
        self.set_frightened_img(blink)  # Задать изображение страха
        self.set_chase_mode(map, (random.randint(0, 32), random.randint(0, 32)))  # Движение к случайной точке на карте

    def set_frightened_img(self, blink=False):  # Установить изображение, используемое при состоянии страха у призраков
        if self.ghost_status < 2:
            self.set_animation(self.frightened_img, self.get_image_parts(self.frightened_img), True, self.time)
        if blink:  # Задаёт мигание для призраков
            self.set_split_sprites_range(5, 8)  # Задать диапазон спрайтов
        else:
            self.set_split_sprites_range(5, 6)
        self.ghost_status = 2

    def set_scatter_img(self):  # Установить обычное изображение у призраков (начальное изображение при старте игры)
        if self.ghost_status > 1:
            self.set_animation(self.img, self.get_image_parts(self.img), True, self.time)
            self.ghost_status = 0  # Состояние преследования

    @staticmethod
    def get_points_distance(p1, p2):  # Получение расстояния между двумя точками
        return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5

    def return_to_ghost_room(self, map):  # Возвращение призрака себе домой после смерти
        self.absolute_speed = self.returning_speed
        if self.returning_room:  # Проверяет, дошёл ли призрак до дома или нет.
            self.absolute_speed = self.normal_speed
            self.movement_direction = 0
            self.ghost_room_enter(map)  # Возвратиться на свою начальную позицию в доме

        else:  # Если призрак не находится рядом с домом
            self.set_chase_mode(map, self.ghost_room_exit_point)  # Следовать ко входу в дом (ghost_room_exit_point))
            self.ghost_status = 3  # Установить статус страха у призрака
            if self.y == 216 and abs(self.x - 206) < self.absolute_speed:  # Если у входа в дом
                self.returning_room = True  # Перемещаться внутри дома

    def moving_inside_ghost_room(self):
        if not self.pause:
            if not self.inside_room_start_moving:
                self.set_y(self.y + self.frightened_speed * self.inside_room_moving_direction)
                if self.y < 260 or self.y > 270:
                    self.inside_room_moving_direction *= -1
                self.set_moving_animation(2 - (1 - self.inside_room_moving_direction) / 2)


class Blinky(Ghost):  # Красный
    def __init__(self, x, y, texture):
        super().__init__(x, y, "blinky", (30, -30), texture)
        self.start_y = 264
        self.inside_ghost_house = False


class Pinky(Ghost):  # Розовый
    def __init__(self, x, y, texture):
        super().__init__(x, y, "pinky", (0, 0), texture)
        self.inside_waiting_time = 1

    def set_pinky_chase_mode(self, map, target_position, target_direction):  # Алгоритм преследования для Pinky
        if target_direction == 1:
            self.set_chase_mode(map, (target_position[0], target_position[1] - 4))
        elif target_direction == 2:
            self.set_chase_mode(map, (target_position[0], target_position[1] + 4))
        elif target_direction == 3:
            self.set_chase_mode(map, (target_position[0] - 4, target_position[1]))
        elif target_direction == 4:
            self.set_chase_mode(map, (target_position[0] + 4, target_position[1]))
        elif target_direction == 0:
            self.set_chase_mode(map, (target_position[0], target_position[1]))


class Inky(Ghost):  # Голубой
    def __init__(self, x, y, texture):
        super().__init__(x, y, "inky", (30, 30), texture)
        self.inside_waiting_time = 5

    def set_inky_chase_mode(self, map, target_position, target_direction, blinky_position):  # Алгоритм преследования
        if target_direction == 1:
            target = (target_position[0], target_position[1] - 2)
        elif target_direction == 2:
            target = (target_position[0], target_position[1] + 2)
        elif target_direction == 3:
            target = (target_position[0] - 2, target_position[1])
        elif target_direction == 4:
            target = (target_position[0] + 2, target_position[1])
        elif target_direction == 0:
            target = (target_position[0], target_position[1])

        target = (blinky_position[0] + (target_position[0] - blinky_position[0]) * 2,
                  blinky_position[1] + (target_position[1] - blinky_position[1]) * 2)
        self.set_chase_mode(map, (target[0], target[1]))


class Clyde(Ghost):  # Оранжевый
    def __init__(self, x, y, texture):
        super().__init__(x, y, "clyde", (0, 30), texture)
        self.inside_waiting_time = 6

    def set_clyde_chase_mode(self, map, target_position):  # Алгоритм преследования для Clyde
        if self.get_points_distance(self.get_ghost_cell(), target_position) > 8:
            self.set_chase_mode(map, target_position)
        else:
            self.set_scatter_mode(map)
