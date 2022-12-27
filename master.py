import pygame
import random
from others import WIDTH, HEIGHT, SIZE, collide_rect
from room import Room, Corridor


class Labyrinth:
    def __init__(self):

        self.map_list = list([0] * 4 for _ in range(4))

        self.rooms = []
        self.corridors = []
        self.create_rooms()
        print(*self.map_list, sep='\n')

    def create_rooms(self):
        self.count_room = random.randrange(1, 4)  # кол-во доп комнат в уровне,
        # то есть без учета первой комнаты, комнаты с врагами(их 2) и последней комнаты
        coords_all_room = []  # список координат комнат
        coords_hor_cor = []  # список координат горизонтальных коридоров
        coords_ver_cor = []  # список координат вертикальных коридоров
        x, y = random.randrange(4), random.randrange(4)
        room = Room(x, y, f'begin_room')
        coords_all_room.append((x, y))
        self.map_list[y][x] = room
        self.rooms.append(room)
        for i in range(3):  # создание основной цепи комнат, то есть те комнаты, которые должны пройти
            d = [(0, -1), (0, 1), (1, 0), (-1, 0)]
            while 1:
                kx, ky = random.choice(d)
                if 4 > x + kx >= 0 and 4 > y + ky >= 0 and not self.map_list[y + ky][x + kx]:
                    if kx:
                        self.corridors.append(Corridor(min(x, x + kx), y, 'horizontal'))
                        coords_hor_cor.append((min(x, x + kx), y))
                    else:
                        self.corridors.append(Corridor(x, min(y, y + ky), 'vertical'))
                        coords_ver_cor.append((x, min(y, y + ky)))
                    x, y = x + kx, y + ky
                    room = Room(x, y, f'map{random.randrange(1, 4)}') if i < 2 else Room(x, y, f'end_room')
                    self.map_list[y][x] = room
                    self.rooms.append(room)
                    coords_all_room.append((x, y))
                    break
                else:
                    del d[d.index((kx, ky))]
        while self.count_room != 0:  # создание доп комнат
            x, y = random.randrange(4), random.randrange(4)
            if not self.map_list[y][x]:
                for kx, ky in [(0, -1), (0, 1), (1, 0), (-1, 0)]:
                    if 4 > x + kx >= 0 and 4 > y + ky >= 0 and self.map_list[y + ky][x + kx] \
                            and self.rooms[0] != self.map_list[y + ky][x + kx] and \
                            self.rooms[3] != self.map_list[y + ky][x + kx]:
                        room = Room(x, y, f'map{random.randrange(1, 4)}')
                        self.map_list[y][x] = room
                        self.rooms.append(room)
                        coords_all_room.append((x, y))
                        if kx:
                            self.corridors.append(Corridor(min(x, x + kx), y, 'horizontal'))
                            coords_hor_cor.append((min(x, x + kx), y))
                        else:
                            self.corridors.append(Corridor(x, min(y, y + ky), 'vertical'))
                            coords_ver_cor.append((x, min(y, y + ky)))
                        break
                if self.map_list[y][x]:
                    self.count_room -= 1
        for x, y in coords_all_room:  # вместо того чтобы просто пройтись по self.map_list лучше это
            walls = []
            for kx, ky in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                # Последние два условия проверяет на наличие коридоров между ними
                if 4 > x + kx >= 0 and 4 > y + ky >= 0 and self.map_list[y + ky][x + kx] and \
                        (kx == 0 or (min(x, kx + x), y) in coords_hor_cor) and \
                        (ky == 0 or (x, min(y, ky + y)) in coords_ver_cor):
                    walls.append(0)
                else:
                    walls.append(1)
            self.map_list[y][x].set_walls(*walls)

    def update(self, screen):
        for room in self.rooms:
            room.move()
            if collide_rect(0, 0, 1360, 780,
                            room.x, room.y, room.x + room.width * room.tile_size,
                            room.y + room.height * room.tile_size):
                room.render(screen)

        for corridor in self.corridors:
            corridor.move()
            if collide_rect(0, 0, WIDTH, HEIGHT,
                            corridor.x, corridor.y, corridor.x + corridor.width * corridor.tile_size,
                            corridor.y + corridor.height * corridor.tile_size):
                corridor.render(screen)


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('Game')
    screen = pygame.display.set_mode(SIZE)
    # pygame.FULLSCREEN | pygame.DOUBLEBUF
    clock = pygame.time.Clock()
    FPS = 60
    running = 1
    lab = Labyrinth()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.fill((0, 0, 0))
        lab.update(screen)
        pygame.display.update()
        clock.tick(FPS)
    pygame.quit()
