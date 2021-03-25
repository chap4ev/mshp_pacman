import pygame
import sys
import os
from button import Button
from config import WIDTH, BLUE, BLACK, WHITE


# -------------------------------------------------------- Map
class Map:
    def __init__(self, name):
        self.name = name
        self.preview_img = pygame.image.load("maps/{}/map_preview.png".format(name))
        self.scores = []
        self.amount_of_scores = 0
        self.load_scores()
        self.data = []
        self.img = None
        self.count_of_grains = 0

    # Выгрузка рекордов из файла в память
    def load_scores(self):
        open('maps/{}/highscores.txt'.format(self.name), 'a').close()  # Создает файл, если его нет
        with open('maps/{}/highscores.txt'.format(self.name), 'r') as f:
            for line in f:
                self.scores.append(int(line))
        self.amount_of_scores = len(self.scores)
        print('loaded scores map:', self.name, self.scores)

    # Добавление нового рекорда (только в память)
    def add_new_score(self, num):
        self.amount_of_scores += 1
        self.scores.append(num)
        self.scores.sort(reverse=True)
        if len(self.scores) > 10:
            self.scores = self.scores[:-1]

    # Запись всех рекодов из памяти в файл
    def write_scores(self):
        with open('maps/{}/highscores.txt'.format(self.name), 'w') as f:
            for i in range(10 if self.amount_of_scores >= 10 else self.amount_of_scores):
                f.write('{}\n'.format(self.scores[i]))
        # print('written to file ', self.scores)

    def reload_data(self):
        with open("maps/{}/map_config.txt".format(self.name), 'r') as f:
            for line in f:
                line_data = []
                for i in range(28):
                    line_data.append(line[i])
                self.data.append(line_data)

    def load_img(self):
        self.img = pygame.image.load("maps/{}/map_img.png".format(self.name))


# -------------------------------------------------------- Texturepack
class Texturepack:
    def __init__(self, name):
        self.name = name
        self.preview_img = pygame.image.load("texturepacks/{}/preview.png".format(name))
        self.number = 0


# -------------------------------------------------------- ScoresMenu
class ScoresMenu:
    def __init__(self):
        self.__buttons = []
        self.__font = pygame.font.Font('font.ttf', 30)

        # Left arrow
        self.__buttons.append(
            Button(1, 40, 35, 31, 51, 'images/ui/arrow_left_static.png', 'images/ui/arrow_left_pressed.png'))
        # Right arrow
        self.__buttons.append(
            Button(2, 380, 35, 31, 51, 'images/ui/arrow_right_static.png', 'images/ui/arrow_right_pressed.png'))
        # Exit button
        self.__buttons.append(
            Button(3, 170, 480, 110, 47, 'images/ui/button_back_static.png', 'images/ui/button_back_pressed.png'))

    def check_events(self):
        response = None
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                pressed_button = self.__get_pressed_button()
                if pressed_button is not None:
                    # Смена карты
                    if pressed_button == 1:
                        response = 1
                    elif pressed_button == 2:
                        response = 2
                    # Выход из игры
                    elif pressed_button == 3:
                        response = 3
            elif event.type == pygame.KEYDOWN:
                # Смена карты
                if event.key == pygame.K_LEFT:
                    response = 1
                elif event.key == pygame.K_RIGHT:
                    response = 2
                elif event.key == pygame.K_ESCAPE:
                    response = 3
            # Выход из игры
            elif event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        return response

    def process_logic(self):
        for button in self.__buttons:
            button.logic(pygame.mouse.get_pos())

    def __get_pressed_button(self):  # Возвращает id кнопки на которую нажали
        for button in self.__buttons:
            if button.get_status() == 1:
                return button.get_id()
        return None

    def process_drawing(self, screen, map_):
        screen.fill(BLACK)

        for button in self.__buttons:  # отрисовка кнопок
            button.draw(screen)

        text = self.__font.render(map_.name, True, BLUE)  # отрисовка названия карты
        text_rect = text.get_rect(center=(WIDTH / 2, 60))
        screen.blit(text, text_rect)

        if map_.amount_of_scores == 0:
            text = self.__font.render('no scores', True, WHITE)
            screen.blit(text, (130, 140))
        else:
            j = 1
            for i in map_.scores:
                # print('{}'.format(i))
                text = self.__font.render('{}. {}'.format(j, i), True, WHITE)
                text_rect = text.get_rect(center=(WIDTH / 2, 80 + j * 35))
                screen.blit(text, text_rect)
                j += 1


# -------------------------------------------------------- TexturesMenu
class TexturesMenu:
    def __init__(self):
        self.__buttons = []
        self.__font = pygame.font.Font('font.ttf', 30)

        # Left arrow
        self.__buttons.append(
            Button(1, 40, 240, 31, 51, 'images/ui/arrow_left_static.png', 'images/ui/arrow_left_pressed.png'))
        # Right arrow
        self.__buttons.append(
            Button(2, 380, 240, 31, 51, 'images/ui/arrow_right_static.png', 'images/ui/arrow_right_pressed.png'))
        # Exit button
        self.__buttons.append(
            Button(3, 95, 450, 260, 47, 'images/ui/button_set_static.png', 'images/ui/button_set_pressed.png'))

    def check_events(self):
        response = None
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                pressed_button = self.__get_pressed_button()
                if pressed_button is not None:
                    # Смена текстурпака
                    if pressed_button == 1:
                        response = 1
                    elif pressed_button == 2:
                        response = 2
                    # Выход из меню
                    elif pressed_button == 3:
                        response = 3
            elif event.type == pygame.KEYDOWN:
                # Смена карты
                if event.key == pygame.K_LEFT:
                    response = 1
                elif event.key == pygame.K_RIGHT:
                    response = 2
                elif event.key == 13:
                    response = 3
            # Выход из игры
            elif event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        return response

    def process_logic(self):
        for button in self.__buttons:
            button.logic(pygame.mouse.get_pos())

    def __get_pressed_button(self):  # Возвращает id кнопки на которую нажали
        for button in self.__buttons:
            if button.get_status() == 1:
                return button.get_id()
        return None

    def process_drawing(self, screen, texturepack):
        screen.fill(BLACK)

        for button in self.__buttons:  # отрисовка кнопок
            button.draw(screen)

        text = self.__font.render(texturepack.name, True, BLUE)  # отрисовка названия карты
        text_rect = text.get_rect(center=(WIDTH / 2, 60))
        screen.blit(text, text_rect)

        screen.blit(texturepack.preview_img, (95, 130))


# -------------------------------------------------------- StartMenu
class StartMenu:
    def __init__(self, screen, texturepack):
        self.screen = screen  # Плоскость отрисовки

        self.main_menu_loop_run = False  # Переменная работы основного цикла
        self.scores_menu_opened = False  # True - Открыто меню рекордов; False - закрыто
        self.textures_menu_opened = False  # True - Открыто меню текстурпаков; False - закрыто

        self.__buttons = []
        self.__scores_buttons = []
        self.__font = pygame.font.Font('font.ttf', 40)
        self.scores_menu = ScoresMenu()
        self.textures_menu = TexturesMenu()

        self.maps = []              # Массив карт
        self.__number_of_maps = 0   # Сколько всего карт
        self.__map_num = 0          # Номер текущей карты
        self.__load_maps()          # Выгрузка рекордов всех карт

        self.texturepacks = []              # Массив текстурпаков
        self.__number_of_texturepacks = 0   # Сколько всего текстурпаков
        self.__texturepack_num = 0 if texturepack is None else texturepack          # Номер текущего текстурпака
        self.__load_texturepacks()          # Подгрузка текстурпаков

        self.start_menu_image = pygame.image.load("images/ui/main_menu.png")  # Фон основного меню

        # Start button
        self.__buttons.append(
            Button(1, 46, 350, 356, 71, 'images/ui/button_start_static.png', 'images/ui/button_start_pressed.png'))
        # Scores button
        self.__buttons.append(
            Button(2, 46, 450, 110, 47, 'images/ui/button_scores_static.png', 'images/ui/button_scores_pressed.png'))
        # Exit button
        self.__buttons.append(
            Button(3, 292, 450, 110, 47, 'images/ui/button_exit_static.png', 'images/ui/button_exit_pressed.png'))
        # Left arrow button
        self.__buttons.append(
            Button(4, 100, 230, 31, 51, 'images/ui/arrow_left_static.png', 'images/ui/arrow_left_pressed.png'))
        # Right arrow button
        self.__buttons.append(
            Button(5, 320, 230, 31, 51, 'images/ui/arrow_right_static.png', 'images/ui/arrow_right_pressed.png'))
        # textures settings button
        self.__buttons.append(
            Button(6, 169, 450, 110, 47, 'images/ui/button_settings_static.png',
                   'images/ui/button_settings_pressed.png'))

    def main_loop(self):
        self.main_menu_loop_run = True

        while self.main_menu_loop_run:

            if not self.scores_menu_opened and not self.textures_menu_opened:  # Сцена основного меню
                self.process_logic()
                self.check_events()
                self.process_drawing()

            elif self.scores_menu_opened:  # Сцена меню рекордов
                self.scores_menu.process_logic()
                response = self.scores_menu.check_events()
                if response == 1:
                    self.__switch_map(-1)
                elif response == 2:
                    self.__switch_map(1)
                elif response == 3:
                    self.scores_menu_opened = False
                self.scores_menu.process_drawing(self.screen, self.maps[self.__map_num])

            elif self.textures_menu_opened:  # Сцена меню рекордов
                self.textures_menu.process_logic()
                response = self.textures_menu.check_events()
                if response == 1:
                    self.__switch_texturepack(-1)
                elif response == 2:
                    self.__switch_texturepack(1)
                elif response == 3:
                    self.textures_menu_opened = False
                self.textures_menu.process_drawing(self.screen, self.texturepacks[self.__texturepack_num])

            pygame.display.flip()
            pygame.time.wait(20)

    def process_logic(self):
        # Логика кнопок
        for button in self.__buttons:
            button.logic(pygame.mouse.get_pos())

    # Отрисовка
    def process_drawing(self):
        self.screen.blit(self.maps[self.__map_num].preview_img, (168, 200))  # отрисовка превью картинки

        self.screen.blit(self.start_menu_image, (0, 0))  # отрисовка картинки менюшки

        for button in self.__buttons:  # отрисовка кнопок
            button.draw(self.screen)

        text = self.__font.render(self.maps[self.__map_num].name, True, BLUE)
        text_rect = text.get_rect(center=(WIDTH / 2, 165))
        self.screen.blit(text, text_rect)

    # Обработка ивентов
    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                pressed_button_id = self.__get_pressed_button()
                if pressed_button_id is not None:
                    # Выход из игры
                    if pressed_button_id == 3:
                        pygame.quit()
                        sys.exit()
                    # Вызов меню рекордов
                    elif pressed_button_id == 2:
                        self.scores_menu_opened = True
                    # Старт игры
                    elif pressed_button_id == 1:
                        self.main_menu_loop_run = False
                    # Смена карты
                    elif pressed_button_id == 4:
                        self.__switch_map(-1)
                    elif pressed_button_id == 5:
                        self.__switch_map(1)
                    # Вызов меню текстурпаков
                    elif pressed_button_id == 6:
                        self.textures_menu_opened = True
            elif event.type == pygame.KEYDOWN:
                # Смена карты
                if event.key == pygame.K_LEFT:
                    self.__switch_map(-1)
                    self.__buttons[3].set_pressed()
                elif event.key == pygame.K_RIGHT:
                    self.__switch_map(1)
                    self.__buttons[4].set_pressed()
            elif event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    def __get_pressed_button(self):  # Возвращает id кнопки на которую нажали
        for button in self.__buttons:
            if button.get_status() == 1:
                return button.get_id()
        return None

    """
    Работа с картами
    """

    def get_map_and_textures(self):  # Подготавливает map и texturepack и возвращает их
        self.maps[self.__map_num].reload_data()
        self.maps[self.__map_num].load_img()

        return self.maps[self.__map_num], self.texturepacks[self.__texturepack_num]

    def __load_maps(self):  # Выгрузка карт в память
        files = os.listdir('maps')
        for map_ in files:
            self.maps.append(Map(map_))
        self.__number_of_maps = len(self.maps)

    def __switch_map(self, num):  # смена номера карты на num
        self.__map_num = (self.__map_num + num) % self.__number_of_maps

    """
    Работа с текстурпаками
    """

    def __load_texturepacks(self):  # Выгрузка текстурпаков в память
        files = os.listdir('texturepacks')
        i = 0
        for texturepack in files:
            self.texturepacks.append(Texturepack(texturepack))
            self.texturepacks[i].number = i
            i += 1
        self.__number_of_texturepacks = len(self.texturepacks)

    def __switch_texturepack(self, num):  # Cмена номера текстурапка на num
        self.__texturepack_num = (self.__texturepack_num + num) % self.__number_of_texturepacks
