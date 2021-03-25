import random
import time
import pygame

from config import WHITE


class LevelManagement:
    def __init__(self, level=1):
        self.time = time.time()
        self.start_time = self.time
        self.waves = 1  # волна
        self.status = 1  # 0 - преследование, 1 - разбегание, 2 - страх, -1 - пауза
        self.level = level  # уровень
        self.scatter_time = 7  # время разбегания
        self.chase_time = 20  # время преследования
        self.frightened_time = 8  # время испуга
        self.ghosts_blinking_time = 3  # время, которое будут мигать призраки
        self.ghosts_blinking = False  # мигание призрака
        self.__font = pygame.font.Font('font.ttf', 20)
        self.pause = False  # пауза
        self.pause_range = 0  # смещение времени при паузе
        self.pause_time = -1  # время для паузы
        self.ghost_scores = -1  # подсчёт очков при съедании призраков

    def reload(self):
        self.__init__(self.level)

    def manage(self, map, pacman, ghosts, scores):  # управление волнами
        if self.status == 0 and int(time.time() - self.time) >= self.chase_time:  # Разбегание
            self.time = time.time()
            self.status = (self.status + 1) % 2
        elif self.status == 1 and time.time() - self.time >= self.scatter_time:  # Преследование
            self.time = time.time()
            self.status = (self.status + 1) % 2
            self.waves += 1
        elif self.status == 2 and time.time() - self.time >= self.frightened_time:
            self.time = time.time()
            self.status = 0
            for ghost in ghosts:
                if ghost.ghost_status != 3:
                    ghost.set_scatter_img()
                    ghost.absolute_speed = ghost.normal_speed
                    if ghost.inside_ghost_house:
                        ghost.set_moving_animation(1)
        if self.status == 2 and time.time() - self.time >= self.frightened_time - self.ghosts_blinking_time:
            self.ghosts_blinking = True
        self.move(map, pacman, ghosts, scores)

    def level_control(self):  # управление уровнями
        if self.level == 0:
            if self.waves < 3:
                self.chase_time = 20
                self.scatter_time = 7
            elif self.waves == 3:
                self.scatter_time = 5
            elif self.waves > 3:
                self.chase_time = time.time() + 1

    def move(self, map, pacman, ghosts, scores):  # управление призраками
        for ghost in ghosts:
            if ghost.inside_ghost_house:
                ghost.moving_inside_ghost_room()
                ghost.inside_room_start_moving = False
            if self.status != 1:
                if ghost.ghost_status != 3:
                    if ghost.name == "blinky":
                        ghost.set_chase_mode(map, pacman.get_pacman_cell())
                        ghost.move(map)
                    if ghost.name == "pinky":
                        ghost.set_pinky_chase_mode(map, pacman.get_pacman_cell(), pacman.movement_direction)
                        ghost.move(map)
                    if ghost.name == "inky":
                        if scores > 300:
                            ghost.set_inky_chase_mode(map, pacman.get_pacman_cell(), pacman.movement_direction, ghosts[0].get_ghost_cell())
                            ghost.move(map)
                        elif time.time() - self.start_time > 5:
                            ghost.set_scatter_mode(map)
                            ghost.move(map)
                    if ghost.name == "clyde" and scores > 800:
                        ghost.set_clyde_chase_mode(map, pacman.get_pacman_cell())
                        ghost.move(map)
            if self.status == 1 and ghost.ghost_status != 3 :
                if ghost.name == "clyde" and scores < 800: pass
                elif ghost.name == "inky" and time.time() - self.start_time < 5: pass
                else:
                    ghost.set_scatter_mode(map)
                    ghost.move(map)
            if ghost.ghost_status == 3:
                ghost.return_to_ghost_room(map)
                ghost.move(map)
            elif self.status == 2 and ghost.ghost_status == 2 and not ghost.pause:
                ghost.set_frightened_mode(map, self.ghosts_blinking)
            if ghost.pause:
                self.time = time.time() - self.pause_range

    def get_fruit(self):
        if self.level == 1:
            return 'cherry'
        elif self.level == 2:
            return 'strawberry'
        elif self.level == 3:
            return 'apple'
        elif self.level == 4:
            return 'banana'
        elif self.level == 5:
            return 'orange'
        else:
            x = random.randint(1, 5)
            if x == 1:
                return 'cherry'
            elif x == 2:
                return 'strawberry'
            elif x == 3:
                return 'apple'
            elif x == 4:
                return 'banana'
            elif x == 5:
                return 'orange'

    def ghost_destroy(self, map, ghosts, pacman, score): # пауза при уничтожении призрака
        if time.time() - self.pause_time >= 1 and self.pause_time >= 0:
            for ghost in ghosts:
                if not ghost.visible:
                    ghost.return_to_ghost_room(map)
                    ghost.set_moving_animation(ghost.movement_direction)
                ghost.pause = False
                ghost.visible = True
            pacman.pause = False
            pacman.visible = True
            self.pause = False
            self.pause_time = -1
            self.pause_range = 0
        else:
            self.pause = True
            destroyed_ghosts_count = 0
            for ghost in ghosts:
                if not ghost.visible:
                    destroyed_ghosts_count += 1
                    if destroyed_ghosts_count > 1:
                        ghost.visible = True
                ghost.pause = True
            if self.pause_time == -1:
                self.pause_time = time.time()
                self.ghost_scores += 1
                score += 200*(2**self.ghost_scores)
            pacman.pause = True
            pacman.visible = False
            self.pause_range = time.time() - self.time
        return score

    def pause_draw(self, pacman, ghost, screen, score):  # вывод кол-ва очков
        if self.pause:
            text = self.__font.render(str(200*(2**self.ghost_scores)), True, WHITE)  # отрисовка названия карты
            text_rect = ((pacman.x + ghost.x)/2-10, (pacman.y + ghost.y)/2, 20, 5)
            screen.blit(text, text_rect)

    def frightened(self, map, pacman, ghosts, scores):
        self.ghosts_blinking = False
        for ghost in ghosts:
            if ghost.ghost_status != 3:
                ghost.set_frightened_mode(map)
                ghost.absolute_speed = ghost.frightened_speed
        self.status = 2
        self.time = time.time()
        self.ghost_scores = -1

