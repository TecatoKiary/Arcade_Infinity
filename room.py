import pygame
import pytmx
from others import TILED_MAP_DIR
import others


# комната 704*704
# протяженность коридора 512 - 32

class RoomCorridor:

    def __init__(self, x, y, filename, type):
        self.map = pytmx.load_pygame(f'{TILED_MAP_DIR}\\{filename}.tmx')
        self.x = x * (704 + 512)
        self.y = y * (704 + 512)
        self.height = self.map.height
        self.width = self.map.width
        self.tile_size = self.map.tilewidth
        self.type = type
        print(others.WIDTH)

    def render(self, screen, x_speed, y_speed, player):
        x1, y1, x2, y2 = self.rect_in_screen(self.x, self.y, self.width, self.height)
        for y in range(y1, y2):
            for x in range(x1, x2):
                for layer in range(2):
                    image = self.map.get_tile_image(x, y, layer)
                    if image:
                        screen.blit(image, (self.x + x * self.tile_size, self.y + y * self.tile_size))
                        if layer == 1 and any([x_speed, y_speed]):
                            x_speed, y_speed = self.is_collising(player, image,
                                                                 self.x + x * self.tile_size,
                                                                 self.y + y * self.tile_size, x_speed, y_speed)
        return x_speed, y_speed

    def render_passing_walls(self, screen, player):
        x1, y1, x2, y2 = self.rect_in_screen(self.x, self.y, self.width, self.height)
        redrawing = True
        for y in range(y1, y2):
            for x in range(x1, x2):
                image = self.map.get_tile_image(x, y, 2)
                if image:
                    screen.blit(image, (self.x + x * self.tile_size, self.y + y * self.tile_size))
                    image_y = self.y + y * self.tile_size
                    image_x = self.x + x * self.tile_size
                    # Знаю, что раздроблено
                    if 406 >= self.map.tiledgidmap[self.map.get_tile_gid(x, y, 2)] >= 404 or \
                            (image_y + self.tile_size >= player.rect.y + player.rect.height >= image_y and (
                                    player.rect.x +
                                    player.rect.width >= image_x >=
                                    player.rect.x or
                                    player.rect.x + player.rect.width >=
                                    image_x >= player.rect.x)):
                        # сложно объяснить зачем условие: делает, можно сказать, 3D объекты-декорации
                        redrawing = False
        # Декорации, которые ничем не мешают персонажам
        for y in range(y1, y2):
            for x in range(x1, x2):
                for layer in range(3, len(self.map.layers)):
                    image = self.map.get_tile_image(x, y, layer)
                    if image:
                        screen.blit(image, (self.x + x * self.tile_size, self.y + y * self.tile_size))
        if redrawing:
            player.draw()

    def rect_in_screen(self, x, y, width_dec, height_dec):
        """Возвращает начальные и конечные координаты ячеек комнаты, которые попадают на экран"""
        # Без этой оптимизации процесс отрисовки был бы ОЧЕНЬ долгим и просаживался бы FPS
        x1 = max(0, x)
        x2 = min(others.WIDTH, width_dec * self.tile_size + x)
        x1 = 0 if x1 == x else (-x // self.tile_size)
        x2 = width_dec if x2 == width_dec * self.tile_size + x \
            else width_dec - (width_dec * self.tile_size + x - others.WIDTH) // self.tile_size
        y1 = max(0, y)
        y2 = min(others.HEIGHT, height_dec * self.tile_size + y)
        y1 = 0 if y1 == y else (-y // self.tile_size)
        y2 = height_dec if y2 == height_dec * self.tile_size + y \
            else height_dec - (height_dec * self.tile_size + y - others.HEIGHT) // self.tile_size
        return x1, y1, x2, y2

    def move(self, x, y):
        self.x -= x
        self.y -= y

    def is_collising(self, player, image, x, y, x_speed, y_speed):
        # Можно сказать, создаем спрайт ячейки для проверки коллизии
        cell = pygame.sprite.Sprite()
        cell.image = image
        cell.rect = image.get_rect()
        cell.rect.x = x
        cell.rect.y = y
        height = player.rect.height  # сохранить точность роста персонажа
        cell.rect.x = cell.rect.x - x_speed
        player.rect.y += player.rect.height // 1.01  # Мы смотрим коллизию по ногам, а не по телу
        player.rect.height -= player.rect.height // 1.01
        if pygame.sprite.collide_rect(cell, player):
            cell.rect.x = cell.rect.x + x_speed
            x_speed = 0
        else:
            cell.rect.x = cell.rect.x + x_speed
        cell.rect.y = cell.rect.y - y_speed
        if pygame.sprite.collide_rect(cell, player):
            y_speed = 0
        cell.kill()  # утечка памяти
        player.rect.height = height  # возвращаем как было
        player.rect.y -= player.rect.height // 1.01
        return x_speed, y_speed


class Room(RoomCorridor):
    def __init__(self, x, y, filename):
        super(Room, self).__init__(x, y, filename, 'room')
        self.walls = []

    def render(self, screen, x_speed, y_speed, player):
        x_speed, y_speed = super(Room, self).render(screen, x_speed, y_speed, player)
        for wall in self.walls:
            # Верхняя стена не должна накладываться на персонажа, а должно быть наоборот. Поэтому
            if wall.filename.find('top') != -1:
                x1, y1, x2, y2 = self.rect_in_screen(self.x, self.y, wall.width, wall.height)
                for y in range(y1, y2):
                    for x in range(x1, x2):
                        for layer in range(len(wall.layers)):
                            image = wall.get_tile_image(x, y, layer)
                            if image:
                                screen.blit(image,
                                            (self.x + x * self.tile_size,
                                             self.y + y * self.tile_size,))
                                if layer == 0 and any([x_speed, y_speed]):
                                    x_speed, y_speed = self.is_collising(player, image,
                                                                         self.x + x * self.tile_size,
                                                                         self.y + y * self.tile_size,
                                                                         x_speed, y_speed)
        return x_speed, y_speed

    def render_passing_walls(self, screen, x_speed, y_speed, player):
        super(Room, self).render_passing_walls(screen, player)
        for wall in self.walls:
            if wall.filename.find('top') != -1:
                continue
            is_bottom = ((self.height - 3) * self.tile_size) if wall.filename.find(
                'bottom') != -1 else 0  # если нижняя стена
            # если правая стена:
            is_right = ((self.width - 2) * self.tile_size) if wall.filename.find('right') != -1 else 0
            x1, y1, x2, y2 = self.rect_in_screen(is_right + self.x, is_bottom + self.y, wall.width, wall.height)
            for y in range(y1, y2):
                for x in range(x1, x2):
                    for layer in range(len(wall.layers)):
                        image = wall.get_tile_image(x, y, layer)
                        if image:
                            screen.blit(image,
                                        (self.x + x * self.tile_size + is_right,
                                         self.y + y * self.tile_size + is_bottom))
                            if layer == 0 and any([x_speed, y_speed]):
                                x_speed, y_speed = self.is_collising(player, image,
                                                                     self.x + x * self.tile_size + is_right,
                                                                     self.y + y * self.tile_size + is_bottom,
                                                                     x_speed, y_speed)
        return x_speed, y_speed

    def set_walls(self, left, right, top, bottom):
        self.walls = []
        walls = ['left' if left else 0, 'right' if right else 0, 'top' if top else 0, 'bottom' if bottom else 0]
        for i in walls:
            if i:
                self.walls.append(pytmx.load_pygame(f'{TILED_MAP_DIR}\\{i}_wall.tmx'))


class Corridor(RoomCorridor):
    def __init__(self, x, y, orientation):
        super(Corridor, self).__init__(x, y, f'{orientation}_corridor', 'corridor')
        if orientation == 'vertical':
            self.y += 672
            self.x += 288
        else:
            self.x += 672
            self.y += 336 - self.tile_size * 13 // 2 - 8

    def render_passing_walls(self, screen, player):
        x1, y1, x2, y2 = self.rect_in_screen(self.x, self.y, self.width, self.height)
        for y in range(y1, y2):
            for x in range(x1, x2):
                image = self.map.get_tile_image(x, y, 2)
                if image:
                    screen.blit(image, (self.x + x * self.tile_size, self.y + y * self.tile_size))
