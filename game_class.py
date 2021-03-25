import pygame
import sys
from pacman import Pacman
from config import BLACK, WHITE
from ghosts import Blinky, Pinky, Inky, Clyde
from level_management import LevelManagement


class Game:
    def __init__(self, screen):
        self.game_loop_run = True
        self.screen = screen  # Плоскость отображения
        self.pacman_start_spawn = None
        self.fruit_spawn = None
        self.pacman = None
        self.level = LevelManagement()
        self.ghosts = list()
        self.grain_img = None
        self.big_grain_img = None
        self.fruits = dict()
        self.fruit_timer = 0
        self.eaten_fruits = list()
        self.big_grain_draw = True  # Отображаем большое зерно или нет. Чтобы мигание делать
        self.sum_of_eaten_grains = 0  # Счетчик съеденных зерен, нужен для последующего отображения вишен
        self.counter = 1  # Счетчик прохода по game_loop, нужен как таймер
        self.up_draw = True
        self.map = None  # Экземпляр класса карты, map.data - карта в виде символов:
        # 0 - стена
        # 1 - малое зерно
        # 2 - съеденное малое зерно
        # 3 - большое зерно
        # 4 - съеденное большое зерно
        # 5 - вишенка
        # 6 - съеденная вишенка
        # 7 - одна из 18 клеток комнаты спавна приведений
        # 8 - пустая клетка
        self.score = 0
        self.texturepack = None  # Текущий текстурпак (экземпляр класса Texturepack)
        self.lives = 3
        self.sounds = dict()

    def main_loop(self):
        print('game loop run')

        self.__process_logic()
        self.__process_drawing()
        pygame.display.flip()
        self.sounds['start_music'].play()
        pygame.time.wait(4500)

        while self.game_loop_run:
            if self.__check_event() == 1:
                self.game_loop_run = False
            self.__process_drawing()
            self.__process_logic()

            pygame.display.flip()
            pygame.time.wait(10)
        # После конца игры
        self.map.add_new_score(self.score)
        self.map.write_scores()
        print('game loop stop')

        return self.texturepack.number

    def __process_logic(self):
        self.pacman.move(self.map.data)
        self.level.manage(self.map.data, self.pacman, self.ghosts, self.score)
        self.check_pacman_ghost_collision()
        self.check_eaten_grains()
        if self.counter % 10 == 0:  # Типа таймера, чтобы мигали не сильно часто
            self.big_grain_draw = not self.big_grain_draw
        if self.counter % 20 == 0:
            self.up_draw = not self.up_draw
        self.counter += 1
        if self.counter == 1000:
            self.counter = 0
        if self.lives == 0:
            self.game_loop_run = False

        if self.sum_of_eaten_grains == self.map.count_of_grains:
            self.change_level()

        if self.sum_of_eaten_grains == 70 or self.sum_of_eaten_grains == 170:
            self.map.data[self.fruit_spawn[1]][self.fruit_spawn[0]] = '6'
            self.map.data[self.fruit_spawn[1]][self.fruit_spawn[0] - 1] = '6'
            self.fruit_timer = self.counter
            self.sounds['fruit'].play()
        if self.map.data[self.fruit_spawn[1]][self.fruit_spawn[0]] == '6':
            if self.counter - self.fruit_timer == 400 or 1000 - self.fruit_timer + self.counter == 400:  # Второе на
                self.map.data[self.fruit_spawn[1]][self.fruit_spawn[0]] = '5'  # случай, если сбросится counter
                self.map.data[self.fruit_spawn[1]][self.fruit_spawn[0] - 1] = '5'
        x, y = self.get_pacman_cell()
        if self.map.data[self.fruit_spawn[1]][self.fruit_spawn[0]] == '6' \
                and (x == self.fruit_spawn[0] or x == self.fruit_spawn[0] - 1) and y == self.fruit_spawn[1]:
            self.map.data[self.fruit_spawn[1]][self.fruit_spawn[0]] = '5'
            self.map.data[self.fruit_spawn[1]][self.fruit_spawn[0] - 1] = '5'
            self.score += 100
            if len(self.eaten_fruits) < 8:
                self.eaten_fruits.append(self.level.get_fruit())

    # Отрисовка не статичных объектов
    def __process_drawing(self):
        self.screen.fill(BLACK)
        # Очередь отрисовки:

        # 1. изображение карты map_img.png
        self.screen.blit(self.map.img, (0, 48))
        # 2. зерна и фрукты
        for i in range(31):
            for j in range(28):
                if self.map.data[i][j] == '1':
                    self.screen.blit(self.grain_img, (j * 16, (i * 16) + 48))
                elif self.map.data[i][j] == '3' and self.big_grain_draw:
                    self.screen.blit(self.big_grain_img, (j * 16, (i * 16) + 48))

        # 3. fruits
        if self.map.data[self.fruit_spawn[1]][self.fruit_spawn[0]] == '6':
            self.screen.blit(self.fruits[self.level.get_fruit()],
                             (self.fruit_spawn[0] * 16 - 16, self.fruit_spawn[1] * 16 + 40))

        # 4. pac man
        self.pacman.draw(self.screen)

        # 5. ghosts
        for ghost in self.ghosts:
            if not ghost.visible:
                self.level.pause_draw(self.pacman, ghost, self.screen, self.score)
            ghost.draw(self.screen)

        # 6. scores
        font = pygame.font.Font('font.ttf', 25)
        if self.up_draw:
            up = font.render('1UP', True, WHITE)  # Надпись над текущим счетом
            up_rect = up.get_rect(topleft=(16 * 2, 0))
            self.screen.blit(up, up_rect)

        score_now = font.render(str(self.score), True, WHITE)  # Текущий счет
        sc_rect = score_now.get_rect(topleft=(16 * 3, 20))
        self.screen.blit(score_now, sc_rect)

        hs_txt = font.render('HIGH SCORE', True, WHITE)  # Надпись над наибольшим счетом
        hs_txt_rect = hs_txt.get_rect(topleft=(16 * 9, 0))
        self.screen.blit(hs_txt, hs_txt_rect)
        if not self.map.scores:
            hs = font.render(str(self.score), True, WHITE)  # Наибольший счет
        else:
            hs = font.render(str(self.map.scores[0]) if self.map.scores[0] > self.score else str(self.score),
                             True, WHITE)  # Наибольший счет
        hs_rect = hs.get_rect(topleft=(16 * 14, 20))
        self.screen.blit(hs, hs_rect)

        # Жизни
        live_pacman = pygame.image.load('./texturepacks/{}/pacman/pacman_stand.png'.format(self.texturepack.name))
        live_pacman = pygame.transform.rotate(live_pacman, 90)
        for i in range(self.lives):
            self.screen.blit(live_pacman, (16 * 2 * (i + 1) + 5 * i, 34 * 16))

        i = 0
        for fruit in self.eaten_fruits:
            self.screen.blit(self.fruits[fruit], (32*(12-i), 34 * 16))
            i += 1

    # Обработка ивентов
    def __check_event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return 1
            self.pacman.check_event(event)

    def __reset_grains(self):
        for i in range(31):
            for j in range(28):
                if self.map.data[i][j] == '2':
                    self.map.data[i][j] = '1'
                elif self.map.data[i][j] == '4':
                    self.map.data[i][j] = '3'

    def set_start_params(self, arguments):
        self.map, self.texturepack = arguments
        print('loaded')

        self.pacman = Pacman(0, 0, 32, 32, 3, 3,
                             start_img_path='texturepacks/{}/pacman/pacman_stand.png'.format(self.texturepack.name))

        self.pacman_start_spawn = None
        self.fruit_spawn = None
        # Установка точки спавна PacMan'а и других необходимых элементов
        previous_char = None
        for i in range(31):
            for j in range(28):
                char = self.map.data[i][j]
                if char == '9' and previous_char == '9':
                    self.pacman_start_spawn = (j * 16 - 16, i * 16 + 40)
                elif char == '5' and previous_char == '5':
                    self.fruit_spawn = (j, i)  # Только координаты клетки
                elif char == '1' or char == '3':
                    self.map.count_of_grains += 1
                previous_char = self.map.data[i][j]
            previous_char = None

        if self.pacman_start_spawn is None:
            print('Error: No pacman start spawn point in map config file')
        if self.fruit_spawn is None:
            print('Error: No fruit spawn point in map config file')

        # Установка текстурок из текстурпака
        self.__set_textures()
        # Установка стартовой позиции пакмана
        self.pacman.set_position(self.pacman_start_spawn[0], self.pacman_start_spawn[1])
        self.level = LevelManagement()

        # установка остальных необходимых значений

        # привидения
        self.ghosts.append(Blinky(13 * 16, 11 * 16 + 48 - 8, self.texturepack.name))
        self.ghosts.append(Pinky(13 * 16, 14 * 16 + 48 - 8, self.texturepack.name))
        self.ghosts.append(Inky(11 * 16, 14 * 16 + 48 - 8, self.texturepack.name))
        self.ghosts.append(Clyde(15 * 16, 14 * 16 + 48 - 8, self.texturepack.name))

        # звуки

        self.sounds['dot1'] = pygame.mixer.Sound('./sounds/dot1.wav')
        self.sounds['dot2'] = pygame.mixer.Sound('./sounds/dot2.wav')
        self.sounds['fruit'] = pygame.mixer.Sound('./sounds/fruit.wav')
        self.sounds['death'] = pygame.mixer.Sound('./sounds/death.wav')
        self.sounds['start_music'] = pygame.mixer.Sound('./sounds/start_music.wav')
        self.sounds['eating_ghost'] = pygame.mixer.Sound('./sounds/eating_ghost.wav')

    def get_pacman_cell(self):  # Возвращает клетку, в которой находится пакман сейчас в виде колонка, строка
        return (self.pacman.x + 16) // 16, (self.pacman.y - 40) // 16

    def check_pacman_ghost_collision(self):
        for ghost in self.ghosts:
            if ghost.ghost_status < 2 and ghost.rect.colliderect(self.pacman.rect):
                self.pacman.rect = None
                self.map.data[self.fruit_spawn[1]][self.fruit_spawn[0]] = '5'  # Cброс фрукта
                self.map.data[self.fruit_spawn[1]][self.fruit_spawn[0] - 1] = '5'

                self.lives -= 1
                self.pacman.set_death_animation()
                self.pacman.movement_direction = 0
                for g in self.ghosts:
                    g.movement_direction = 0
                self.sounds['death'].set_volume(0.5)
                self.sounds['death'].play()
                for i in range(90):
                    self.__process_drawing()
                    pygame.display.flip()
                    pygame.time.wait(10)
                if self.lives == 0:
                    self.game_loop_run = False
                else:
                    self.pacman = Pacman(0, 0, 32, 32, 3, 3,
                                         start_img_path='texturepacks/{}/pacman/pacman_stand.png'.format(
                                             self.texturepack.name))
                    self.pacman.texture_stand = 'texturepacks/{}/pacman/pacman_stand.png'.format(
                        self.texturepack.name)
                    self.pacman.texture_eat = 'texturepacks/{}/pacman/pacman_eat.png'.format(
                        self.texturepack.name)
                    self.pacman.texture_death = 'texturepacks/{}/pacman/pacman_death.png'.format(
                        self.texturepack.name)
                    self.pacman.set_position(self.pacman_start_spawn[0], self.pacman_start_spawn[1])
                    self.pacman.move(self.map.data)
                    self.ghosts = list()

                    self.ghosts.append(Blinky(13 * 16, 11 * 16 + 48 - 8, self.texturepack.name))
                    self.ghosts.append(Pinky(13 * 16, 14 * 16 + 48 - 8, self.texturepack.name))
                    self.ghosts.append(Inky(11 * 16, 14 * 16 + 48 - 8, self.texturepack.name))
                    self.ghosts.append(Clyde(15 * 16, 14 * 16 + 48 - 8, self.texturepack.name))

                    self.level.reload()

                    self.__process_drawing()
                    pygame.display.flip()
                    pygame.time.wait(2000)
            elif ghost.rect.colliderect(self.pacman.rect):
                if ghost.ghost_status != 3:
                    ghost.visible = False
                    self.sounds['eating_ghost'].set_volume(0.5)
                    self.sounds['eating_ghost'].play()
                    self.score = self.level.ghost_destroy(self.map.data, self.ghosts, self.pacman, self.score)

    def check_eaten_grains(self):
        for i in range(31):
            for j in range(28):
                char = self.map.data[i][j]
                if (char == '1' or char == '3') and self.get_pacman_cell()[0] == j and self.get_pacman_cell()[1] == i:
                    if char == '1':
                        self.map.data[i][j] = '2'
                        self.score += 10
                        self.sum_of_eaten_grains += 1

                        if self.sum_of_eaten_grains % 2 == 0:
                            self.sounds['dot2'].stop()
                            self.sounds['dot1'].play()
                        else:
                            self.sounds['dot1'].stop()
                            self.sounds['dot2'].play()
                    elif char == '3':
                        self.map.data[i][j] = '4'
                        self.score += 50
                        self.sum_of_eaten_grains += 1
                        self.level.frightened(self.map.data, self.pacman, self.ghosts, self.score)

    def __set_textures(self):
        # grains
        self.grain_img = pygame.image.load('texturepacks/{}/grains/grain.png'.format(self.texturepack.name))
        self.big_grain_img = pygame.image.load('texturepacks/{}/grains/grain_big.png'.format(self.texturepack.name))
        # pacman
        self.pacman.texture_stand = 'texturepacks/{}/pacman/pacman_stand.png'.format(self.texturepack.name)
        self.pacman.texture_death = 'texturepacks/{}/pacman/pacman_death.png'.format(self.texturepack.name)
        self.pacman.texture_eat = 'texturepacks/{}/pacman/pacman_eat.png'.format(self.texturepack.name)
        # fruits
        self.fruits['cherry'] = pygame.image.load('texturepacks/{}/fruits/cherry.png'.format(self.texturepack.name))
        self.fruits['strawberry'] = pygame.image.load('texturepacks/{}/fruits/strawberry.png'.
                                                      format(self.texturepack.name))
        self.fruits['banana'] = pygame.image.load('texturepacks/{}/fruits/banana.png'.format(self.texturepack.name))
        self.fruits['apple'] = pygame.image.load('texturepacks/{}/fruits/apple.png'.format(self.texturepack.name))
        self.fruits['orange'] = pygame.image.load('texturepacks/{}/fruits/orange.png'.format(self.texturepack.name))

    def change_level(self):
        for i in range(8):
            self.screen.fill(BLACK)
            # Очередь отрисовки:

            # 1. изображение карты map_img.png
            if i % 2 == 0:
                self.screen.blit(self.map.img, (0, 48))
            else:
                self.screen.blit(pygame.image.load('./maps/{}/map_img_blink.png'.format(self.map.name)), (0, 48))

            # 3. pac man
            self.pacman.draw(self.screen)

            # 5. scores
            font = pygame.font.Font('font.ttf', 25)
            up = font.render('1UP', True, WHITE)  # Надпись над текущим счетом
            up_rect = up.get_rect(topleft=(16 * 2, 0))
            self.screen.blit(up, up_rect)

            score_now = font.render(str(self.score), True, WHITE)  # Текущий счет
            sc_rect = score_now.get_rect(topleft=(16 * 3, 20))
            self.screen.blit(score_now, sc_rect)

            hs_txt = font.render('HIGH SCORE', True, WHITE)  # Надпись над наибольшим счетом
            hs_txt_rect = hs_txt.get_rect(topleft=(16 * 9, 0))
            self.screen.blit(hs_txt, hs_txt_rect)
            if not self.map.scores:
                hs = font.render(str(self.score), True, WHITE)  # Наибольший счет
            else:
                hs = font.render(str(self.map.scores[0]) if self.map.scores[0] > self.score else str(self.score),
                                 True, WHITE)  # Наибольший счет
            hs_rect = hs.get_rect(topleft=(16 * 14, 20))
            self.screen.blit(hs, hs_rect)

            # Жизни
            live_pacman = pygame.image.load('./texturepacks/{}/pacman/pacman_stand.png'.format(self.texturepack.name))
            live_pacman = pygame.transform.rotate(live_pacman, 90)
            for j in range(self.lives):
                self.screen.blit(live_pacman, (16 * 2 * (j + 1) + 5 * j, 34 * 16))
            pygame.display.flip()
            pygame.time.wait(500)

        self.__reset_grains()
        self.map.data[self.fruit_spawn[1]][self.fruit_spawn[0]] = '5'  # Сброс фруктов
        self.map.data[self.fruit_spawn[1]][self.fruit_spawn[0] - 1] = '5'
        self.pacman.movement_direction = 0
        self.pacman.set_position(self.pacman_start_spawn[0], self.pacman_start_spawn[1])
        self.ghosts = list()
        self.ghosts.append(Blinky(13 * 16, 11 * 16 + 48 - 8, self.texturepack.name))
        self.ghosts.append(Pinky(13 * 16, 14 * 16 + 48 - 8, self.texturepack.name))
        self.ghosts.append(Inky(11 * 16, 14 * 16 + 48 - 8, self.texturepack.name))
        self.ghosts.append(Clyde(15 * 16, 14 * 16 + 48 - 8, self.texturepack.name))
        self.sum_of_eaten_grains = 0
        self.level.level += 1
