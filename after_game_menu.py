import pygame
import sys
import os
from button import Button
from config import WIDTH, BLUE, BLACK, WHITE


class Gameover:
    def __init__(self, score, screen):
        self.__buttons = []
        self.__font = pygame.font.Font('font.ttf', 50)
        self.score = score
        self.screen = screen

        self.__buttons.append(
            Button(1, 46, 350, 260, 47, 'images/ui/button_restart_static.png', 'images/ui/button_restart_pressed.png'))

        self.__buttons.append(
            Button(2, 46, 450, 233, 47, 'images/ui/button_menu_static.png',
                   'images/ui/button_menu_pressed.png'))

        self.__buttons.append(
            Button(3, 292, 450, 110, 47, 'images/ui/button_exit_static.png', 'images/ui/button_exit_pressed.png'))

    def main_loop(self):
        print('after game menu run')
        while True:
            self.process_logic()
            response = self.check_events()
            if response == 1:
                return 1
            elif response == 2:
                return None
            self.process_drawing()

    def check_events(self):
        response = None
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                pressed_button = self.__get_pressed_button()
                if pressed_button is not None:
                    # Рестарт
                    if pressed_button == 1:
                        response = 1
                    # Меню
                    elif pressed_button == 2:
                        response = 2
                    # Выход
                    elif pressed_button == 3:
                        pygame.quit()
                        sys.exit()
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

    def process_drawing(self):
        self.screen.fill(BLACK)

        for button in self.__buttons:  # отрисовка кнопок
            button.draw(self.screen)

        game_over = self.__font.render('GAME OVER', True, BLUE)
        game_over_rect = game_over.get_rect(center=(WIDTH / 2, 60))
        self.screen.blit(game_over, game_over_rect)

        new_font = pygame.font.Font('font.ttf', 40)

        score_txt = new_font.render('SCORE: {}'.format(self.score), True, WHITE)
        score_txt_rect = score_txt.get_rect(topleft=(game_over_rect.x, 120))
        self.screen.blit(score_txt, score_txt_rect)

        pygame.display.flip()
