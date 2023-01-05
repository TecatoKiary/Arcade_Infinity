import random
import pygame
import pytmx
from others import TILED_MAP_DIR, PICTURE_WAllS, is_collide
import others
import sprites

# комната 704*704
# протяженность коридора 512 - 32
is_stay_gates = True  # Стоят ли ворота. Она понадобилась в одном месте


class RoomCorridor:
    def __init__(self, x, y, filename):
        self.map = pytmx.load_pygame(f'{TILED_MAP_DIR}\\{filename}.tmx')
        self.x = x * (704 + 512)
        self.y = y * (704 + 512)
        self.height = self.map.height
        self.width = self.map.width
        self.tile_size = self.map.tilewidth
        self.filename_room = filename
        self.picture_walls = dict()
        self.top_wall = False  # есть наверху полная стена или там коридор
        self.redrawing = True
        self.redrawing_monsters = []
        self.walls_gates = dict()
        self.torch_group = pygame.sprite.Group()
        self.monster_group = pygame.sprite.Group()
        self.drawing_monster_group = pygame.sprite.Group()
        self.add_flags()

    def add_flags(self):
        for y in range(self.height):
            for x in range(self.width):
                if self.map.get_tile_image(x, y, 0):
                    if self.map.tiledgidmap[self.map.get_tile_gid(x, y, 0)] == 1376:
                        sprites.Torch('torch_', self.x + self.tile_size * (x - 1),
                                      self.y + self.tile_size * (y - 1) - self.tile_size // 2, True)
                    elif self.map.tiledgidmap[self.map.get_tile_gid(x, y, 0)] == 1441:
                        self.torch_group.add(sprites.Torch('torch_', self.x + self.tile_size * (x - 1),
                                                           self.y + self.tile_size * (y - 1) - self.tile_size // 2,
                                                           False))
                    elif self.map.tiledgidmap[self.map.get_tile_gid(x, y, 0)] == 489:
                        sprites.Torch('candleA_0', self.x + self.tile_size * (x - 1),
                                      self.y + self.tile_size * (y - 1) - self.tile_size // 2, True)
                    elif self.map.tiledgidmap[self.map.get_tile_gid(x, y, 0)] == 553:
                        self.torch_group.add(sprites.Torch('candleA_0', self.x + self.tile_size * (x - 1),
                                                           self.y + self.tile_size * (y - 1) - self.tile_size // 2,
                                                           False))
                    elif self.map.tiledgidmap[self.map.get_tile_gid(x, y, 0)] == 615:
                        sprites.Torch('candleB_0', self.x + self.tile_size * (x - 1),
                                      self.y + self.tile_size * (y - 1), True)
                    elif self.map.tiledgidmap[self.map.get_tile_gid(x, y, 0)] == 550:
                        self.torch_group.add(sprites.Torch('candleB_0', self.x + self.tile_size * (x - 1),
                                                           self.y + self.tile_size * (y - 1), False))

    def render(self, screen, x_speed, y_speed, player):
        x_speed, y_speed = self.blit_tiles(screen, self.map, self.x, self.y, self.width, self.height, range(1, 3),
                                           functions=[self.is_render_picture_walls, is_collide],
                                           player=player, x_speed=x_speed,
                                           y_speed=y_speed)
        return x_speed, y_speed

    def render_passing_walls(self, screen, player):
        self.redrawing = True
        self.redrawing_monsters = [i for i in self.drawing_monster_group]
        self.blit_tiles(screen, self.map, self.x, self.y, self.width, self.height, [3],
                        functions=[self.redrawing_player],
                        player=player)
        self.torch_group.draw(screen)
        [i.increment_cnt() for i in self.torch_group]
        if self.redrawing:
            player.draw(screen)
        if self.redrawing_monsters:
            [i.draw(screen) for i in self.redrawing_monsters]

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
        [i.move(x, y) for i in self.torch_group]
        [i.move(x, y) for i in self.monster_group]

    def blit_tiles(self, screen, room, x_pos, y_pos, w, h, layers, functions=[], is_top_wall=False,
                   x_speed=None, y_speed=None, player=None, layers_collide=2):
        x1, y1, x2, y2 = self.rect_in_screen(x_pos, y_pos, w, h)
        for y in range(y1, y2):
            for x in range(x1, x2):
                for layer in layers:
                    if self.is_render_picture_walls in functions:
                        if (is_top_wall or layer == 2) and self.is_render_picture_walls(x, y):
                            image = self.picture_walls[f'{x} {y}'][0].get_tile_image(
                                *self.picture_walls[f'{x} {y}'][-1], 0)
                            screen.blit(image, (x_pos + x * self.tile_size, y_pos + y * self.tile_size))
                            continue
                    if type(self) == Room and layer == 1 and y == 43 and type(self.walls_gates['bottom']) != Gate:
                        continue
                    image = room.get_tile_image(x, y, layer)
                    if image:
                        screen.blit(image, (x_pos + x * self.tile_size, y_pos + y * self.tile_size))
                        if is_collide in functions and layer == layers_collide:
                            x_speed, y_speed = is_collide(player, image, x_pos + x * self.tile_size,
                                                          y_pos + y * self.tile_size, x_speed, y_speed)
                        if self.redrawing and self.redrawing_player in functions:
                            self.redrawing = self.redrawing_player(player, x, y)
                        if self.redrawing_player in functions:
                            for i in range(len(self.redrawing_monsters) - 1, -1, -1):
                                if not self.redrawing_player(self.redrawing_monsters[i], x, y):
                                    del self.redrawing_monsters[i]

        if x_speed is not None:
            return x_speed, y_speed

    def is_render_picture_walls(self, x, y):
        return self.picture_walls.get(f'{x} {y}')

    def redrawing_player(self, player, x, y):
        image_y = self.y + y * self.tile_size
        image_x = self.x + x * self.tile_size
        if 406 >= self.map.tiledgidmap[self.map.get_tile_gid(x, y, 3)] >= 404 or \
                (image_y + self.tile_size >= player.rect.y + player.rect.height >= image_y and (
                        player.rect.x + player.rect.width >= image_x >= player.rect.x or
                        player.rect.x + player.rect.width >= image_x >= player.rect.x)):
            # сложно объяснить зачем условие: делает, можно сказать, 3D объекты-декорации
            return False
        return True


class Room(RoomCorridor):
    def __init__(self, x, y, filename):
        super(Room, self).__init__(x, y, filename)

    def add_monsters(self):
        if self.filename_room not in ['room_with_chest', 'begin_room', 'end_room']:
            cnt_monsters = random.randrange(4, 11)  # экспериментально
            while cnt_monsters != 0:
                monster = sprites.Monster(0, 0)
                monster.rect.x = self.x + self.tile_size * random.randrange(3, self.width - 6)
                monster.rect.y = self.y + self.tile_size * random.randrange(6, self.height - 6)
                collide = [is_collide(monster, self.map.get_tile_image(x, y, 2), self.x + x * self.tile_size,
                                      self.y + y * self.tile_size, 2, 2) if self.map.get_tile_image(x, y, 2) else (2, 2)
                           for y in range(self.height) for x in range(self.width)]
                collide = list(set(collide))
                if pygame.sprite.spritecollideany(monster, sprites.barrel_group) or \
                        pygame.sprite.spritecollideany(monster, sprites.torch_group) or \
                        pygame.sprite.spritecollideany(monster, sprites.spike_group) or len(collide) > 1:
                    monster.kill()
                    continue
                self.monster_group.add(monster)
                self.drawing_monster_group.add(monster)
                cnt_monsters -= 1

    def render(self, screen, x_speed, y_speed, player):
        x_speed, y_speed = super(Room, self).render(screen, x_speed, y_speed, player)
        for key, wall in self.walls_gates.items():
            # Верхняя стена не должна накладываться на персонажа, а должно быть наоборот. Поэтому
            if key == 'top':
                if type(wall) == Gate:
                    if is_stay_gates:
                        wall.render(screen)
                        # x_speed, y_speed = wall.is_collide(player, x_speed, y_speed)
                    else:
                        wall.cnt = 0
                else:
                    x_speed, y_speed = self.blit_tiles(screen, wall, self.x, self.y, wall.width,
                                                       wall.height, [0], x_speed=x_speed, y_speed=y_speed,
                                                       player=player,
                                                       functions=[is_collide, self.is_render_picture_walls],
                                                       layers_collide=0, is_top_wall=True)
                continue
        self.blit_tiles(screen, self.map, self.x, self.y, self.width, self.height, range(4, len(self.map.layers)))
        return x_speed, y_speed

    def render_passing_walls(self, screen, x_speed, y_speed, player):
        self.drawing_monster_group.draw(screen)
        for key, wall in self.walls_gates.items():
            if key == 'top' or key == 'bottom':
                continue
            if type(wall) == Gate:
                if is_stay_gates:
                    wall.render(screen)
                    # x_speed, y_speed = wall.is_collide(player, x_speed, y_speed)
                else:
                    wall.cnt = 0
                continue
        super(Room, self).render_passing_walls(screen, player)
        for key, wall in self.walls_gates.items():
            if key == 'top':
                continue
            if type(wall) == Gate:
                if key == 'left' or key == 'right':
                    continue
                if is_stay_gates:
                    wall.render(screen)
                    # x_speed, y_speed = wall.is_collide(player, x_speed, y_speed)
                else:
                    wall.cnt = 0
                continue
            is_bottom = ((self.height - 3) * self.tile_size) if wall.filename.find(
                'bottom') != -1 else 0  # если нижняя стена
            # если правая стена:
            is_right = ((self.width - 2) * self.tile_size) if wall.filename.find('right') != -1 else 0
            x_speed, y_speed = self.blit_tiles(screen, wall, is_right + self.x, is_bottom + self.y, wall.width,
                                               wall.height, range(len(wall.layers)), functions=[is_collide],
                                               x_speed=x_speed, y_speed=y_speed, player=player, layers_collide=0)

        return x_speed, y_speed

    def set_walls(self, left, right, top, bottom):
        # Либо стена, либо коридор, где на концах расположены ворота
        self.walls_gates = {
            'left': pytmx.load_pygame(f'{TILED_MAP_DIR}\\left_wall.tmx') if left else
            Gate(self.x + self.tile_size,
                 self.y + self.tile_size * self.height // 2 - 7 * self.tile_size, 'vertical'),
            'right': pytmx.load_pygame(f'{TILED_MAP_DIR}\\right_wall.tmx') if right else
            Gate(self.x + self.tile_size * self.width - self.tile_size * 2,
                 self.y + self.tile_size * self.height // 2 - 7 * self.tile_size, 'vertical'),
            'top': pytmx.load_pygame(f'{TILED_MAP_DIR}\\top_wall.tmx') if top else
            Gate(self.x + self.tile_size * self.width // 2 - 4 * self.tile_size,
                 self.y + self.tile_size, 'horizontal', top_or_bottom='top'),
            'bottom': pytmx.load_pygame(f'{TILED_MAP_DIR}\\bottom_wall.tmx') if bottom else
            Gate(self.x + self.tile_size * self.width // 2 - 4 * self.tile_size,
                 self.y + self.tile_size * self.height - self.tile_size * 3, 'horizontal'),
        }
        self.top_wall = 0 if type(self.walls_gates['top']) == Gate else 1
        self.set_picture_walls()

    def set_picture_walls(self):
        x_pos = 2
        for _ in range(8):
            pic_wall = pytmx.load_pygame(random.choice(PICTURE_WAllS))
            if not self.top_wall and x_pos == 20:
                x_pos += 6
                continue
            i = 0
            for x in range(x_pos, x_pos + 4):
                j = 0
                for y in range(1, 4):
                    self.picture_walls[f'{x} {y}'] = [pic_wall, (i, j)]
                    j += 1
                i += 1
            x_pos += 6

    def move(self, x, y):
        super(Room, self).move(x, y)
        for key, wall in self.walls_gates.items():
            if type(wall) == Gate:
                wall.move(x, y)

    def self_move_of_monster(self):
        if is_stay_gates and len(self.monster_group.sprites()):
            monsters = [i for i in self.monster_group.sprites()]
            self.monster_group = pygame.sprite.Group()
            # print(monsters[0] == self.monster_group.sprites()[0])
            for i, wall in enumerate(self.walls_gates.items()):
                key, wall = wall
                is_bottom = ((self.height - 3) * self.tile_size) if key == 'bottom' else 0  # если нижняя стена
                # если правая стена:
                is_right = ((self.width - 2) * self.tile_size) if key == 'right' else 0
                if type(wall) == Gate:
                    for i in range(len(monsters) - 1, -1, -1):
                        monster = monsters[i]
                        monster.random_x, monster.random_y = wall.is_collide(monster, monster.random_x,
                                                                             monster.random_y)
                        if 0 == monster.random_x and monster.random_y == 0:
                            self.monster_group.add(monsters[i])
                            del monsters[i]
                    if not monsters:
                        [i.self_move() for i in self.monster_group]
                        return
                    continue
                for y in range(wall.height):
                    for x in range(wall.width):
                        image = wall.get_tile_image(x, y, 0)
                        if image:
                            for i in range(len(monsters) - 1, -1, -1):
                                monster = monsters[i]
                                monster.random_x, monster.random_y = is_collide(monster, image,
                                                                                self.x + x * self.tile_size + is_right,
                                                                                self.y + y * self.tile_size + is_bottom,
                                                                                monster.random_x, monster.random_y)
                                if 0 == monster.random_x and monster.random_y == 0:
                                    self.monster_group.add(monsters[i])
                                    del monsters[i]
                            if not monsters:
                                [i.self_move() for i in self.monster_group]
                                return
            for y in range(self.height):
                for x in range(self.width):
                    image = self.map.get_tile_image(x, y, 2)
                    if image:
                        for i in range(len(monsters) - 1, -1, -1):
                            monster = monsters[i]
                            monster.random_x, monster.random_y = is_collide(monster, image, self.x + x * self.tile_size,
                                                                            self.y + y * self.tile_size,
                                                                            monster.random_x, monster.random_y)
                            if 0 == monster.random_x and monster.random_y == 0:
                                self.monster_group.add(monsters[i])
                                del monsters[i]
                        if not monsters:
                            [i.self_move() for i in self.monster_group]
                            return
            for i in range(len(monsters) - 1, -1, -1):
                monster = monsters[i]
                for j in sprites.barrel_group:
                    monster.random_x, monster.random_y = j.is_collide(monster, monster.random_x, monster.random_y)
                    if 0 == monster.random_x and monster.random_y == 0:
                        self.monster_group.add(monster)
                        del monsters[i]
                        break
                if not monsters:
                    [i.self_move() for i in self.monster_group]
                    return
            for i in range(len(monsters) - 1, -1, -1):
                monster = monsters[i]
                for j in sprites.torch_group:
                    monster.random_x, monster.random_y = j.is_collide(monster, monster.random_x, monster.random_y)
                    if 0 == monster.random_x and monster.random_y == 0:
                        self.monster_group.add(monster)
                        del monsters[i]
                        break
                if not monsters:
                    [i.self_move() for i in self.monster_group]
                    return
            self.monster_group.add(i for i in monsters)
            [i.self_move() for i in self.monster_group]


class Corridor(RoomCorridor):
    def __init__(self, x, y, orientation):
        super(Corridor, self).__init__(x, y, f'{orientation}_corridor')
        if orientation == 'vertical':
            self.y += 672
            self.x += 288
        else:
            self.x += 672
            self.y += 336 - self.tile_size * 13 // 2 - 8

    def render(self, screen, x_speed, y_speed, player):
        global is_stay_gates
        # is_stay_gates = False if \
        #     self.x + 16 <= others.WIDTH // 2 <= self.x + self.width * self.tile_size - 16 and \
        #     self.y + 16 <= others.HEIGHT // 2 <= self.y + self.height * self.tile_size - 16 else True
        x_speed, y_speed = super(Corridor, self).render(screen, x_speed, y_speed, player)
        if not is_stay_gates:
            self.blit_tiles(screen, self.map, self.x, self.y, self.width, self.height, range(4, len(self.map.layers)))
        return x_speed, y_speed

    def render_passing_walls(self, screen, player):
        self.blit_tiles(screen, self.map, self.x, self.y, self.width, self.height, [3])


class Gate:
    def __init__(self, x, y, orientation, top_or_bottom=False):
        self.map = pytmx.load_pygame(TILED_MAP_DIR + f'\\{orientation}_gate.tmx')
        # Чтобы не делать два файла ворот разных размеров (6*3 и 6*4), решил сделать так:
        self.top = True if top_or_bottom == 'top' else False
        self.x = x
        self.y = y
        self.height = self.map.height + (1 if self.top else 0)
        self.width = self.map.width
        self.tile_size = self.map.tilewidth
        self.orientation = orientation
        self.cnt = 0  # макс 120
        self.step = 60 // self.height

    def move(self, x, y):
        self.x -= x
        self.y -= y

    def render(self, screen):
        t = False
        if self.orientation == 'vertical' and self.cnt < 60:
            self.increment_step()
            return
        for y in range(self.height):
            for x in range(1 if self.orientation == 'horizontal' else 0,
                           self.width - (1 if self.orientation == 'horizontal' else 0)):
                for layer in range(len(self.map.layers)):
                    if self.top and y >= 2:
                        image = self.map.get_tile_image(x, y - 1, layer)
                    else:
                        image = self.map.get_tile_image(x, y, layer)
                    if image:
                        if self.orientation == 'horizontal' and \
                                self.cnt // self.step == y:
                            image = pygame.transform.chop(image, [0,
                                                                  int(self.tile_size * (
                                                                          self.cnt % self.step) / self.step), 0,
                                                                  self.tile_size - int(self.tile_size * (
                                                                          self.cnt % self.step) / self.step)])
                            t = True
                        if self.orientation == 'horizontal':
                            screen.blit(image, (self.x + self.tile_size * x,
                                                self.y + self.tile_size * y - int(
                                                    self.tile_size * self.cnt / self.step) + self.tile_size *
                                                self.height))
                        else:
                            screen.blit(image, (self.x + self.tile_size * x,
                                                self.y + self.tile_size * y))

            if t:
                self.increment_step()
                return

    def increment_step(self):
        self.cnt += 1 if is_stay_gates and self.cnt < 60 else 0

    def is_collide(self, player, x_speed, y_speed):
        if is_stay_gates and any([x_speed, y_speed]):
            if self.orientation == 'vertical':
                for y in range(self.height):
                    image = self.map.get_tile_image(0, y, 0)
                    if image:
                        x_speed, y_speed = is_collide(player, image, self.x, self.y + y * self.tile_size,
                                                      x_speed, y_speed)
            elif self.orientation == 'horizontal':
                for x in range(self.width):
                    image = self.map.get_tile_image(x, 2, 0)
                    if image:
                        x_speed, y_speed = is_collide(player, image, x * self.tile_size + self.x,
                                                      (3 if self.top else 2) * self.tile_size + self.y,
                                                      x_speed, y_speed)
        return x_speed, y_speed
