import pygame


class Button:
    def __init__(self, id, x, y, width, height, static_img, on_pressed_img):
        self.__id = id
        self.__x = x
        self.__y = y
        self.__width = width
        self.__height = height
        self.__img_static = pygame.image.load(static_img)
        self.__img_on_pressed = pygame.image.load(on_pressed_img)
        self.__status = 0  # 0 - курсор вне кнопки, 1 - курсор на кнопке, 2 - кнопка нажата
        self.__count = 0  # Время после нажатия (для статуса 2)

    def draw(self, screen):
        if self.__status == 0:
            screen.blit(self.__img_static, (self.__x, self.__y))
        elif self.__status == 1 or self.__status == 2:
            screen.blit(self.__img_on_pressed, (self.__x, self.__y))

    def logic(self, cur_xy):
        if self.__status != 2:
            if (self.__x <= cur_xy[0] <= self.__x + self.__width) and (self.__y <= cur_xy[1] <= self.__y + self.__height):
                self.__status = 1
            else:
                self.__status = 0

        if self.__status == 2:
            if self.__count == 0:
                self.__status = 0
            else:
                self.__count -= 1

    def get_status(self):
        return self.__status

    def set_pressed(self, time=3):
        self.__status = 2
        self.__count = time

    def get_id(self):
        return self.__id
