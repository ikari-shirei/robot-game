import pygame
from random import randint

""" 

AdventuresOfRobo

Your target in this game is to collect 100 coins without getting
attacked by monsters twice. If monsters catch you in the default world
they will take you into the dark world. You have to resist their attack for
30 seconds in this world. If they catch you in the dark world, the game is over.

You also have an energy bar. It increases one by one based on coins you collect.
If you have 10 energy you can turn the world into an alternate world. In this world
there are ten doors and as soon as those doors detect any monsters in the world, they rush
forward on them and send them all to the dark world where the darkness prevails.
You lose 10 energy if the monsters take you into the dark world, so be careful.

Good luck.

Keys:
- Enter: Start game
- ESC: Quit game
- X: Turn the world into alternate world
- Left Arrow: Robot goes left
- Right Arrow: Robot goes right

"""


class Robo:
    def __init__(self, SCREEN_W, SCREEN_H, avatar):
        self.x = SCREEN_W / 2 - avatar.get_width()
        self.y = SCREEN_H - avatar.get_height()
        self.x_vel = 0
        self.y_vel = 0

    def move_robo(self):
        self.x += self.x_vel
        self.y += self.y_vel

    def __repr__(self):
        return f"Robo x:{self.x} y:{self.y}"


class Monster:
    def __init__(self, SCREEN_W, SCREEN_H, avatar):
        self.x = randint(0, SCREEN_W - avatar.get_width())
        self.y = randint(200, 2000) * -1
        self.x_vel = 0
        self.y_vel = randint(3, 5)

    def move_monster(self):
        self.y += self.y_vel
        self.x += self.x_vel

    def __repr__(self):
        return f"MONSTER x:{self.x} y:{self.y}"


class Coin:
    def __init__(self, SCREEN_W, SCREEN_H, avatar):
        self.x = randint(0, SCREEN_W - avatar.get_width())
        self.y = randint(200, 2000) * -1
        self.x_vel = 0
        self.y_vel = 1.5

    def move_coin(self):
        self.y += self.y_vel
        self.x += self.x_vel

    def __repr__(self):
        return f"COIN x:{self.x} y:{self.y}"


class Door:
    current_location = 0
    count = 0

    def __init__(self, SCREEN_W, SCREEN_H, avatar):
        self.x = Door.current_location
        self.y = SCREEN_H - avatar.get_height() * 2.2
        self.x_vel = 0
        self.y_vel = 0
        Door.current_location += avatar.get_width() + 15
        Door.count += 1

        if Door.count >= 10:
            Door.count = 0
            Door.current_location = 0

    def move_door(self):
        self.y += self.y_vel
        self.x += self.x_vel

    def catch_monster(self, mn: Monster):
        if mn:
            if mn.y <= self.y:
                self.y_vel = -3

    def __repr__(self):
        return f"DOOR x:{self.x} y:{self.y}"


class AdventuresOfRobo:
    def __init__(self):
        pygame.init()

        self.SCREEN_W = 640
        self.SCREEN_H = 480

        self.window = pygame.display.set_mode((self.SCREEN_W, self.SCREEN_H))
        self.robot = pygame.image.load("robot.png")
        self.monster = pygame.image.load("monster.png")
        self.coin = pygame.image.load("coin.png")
        self.door = pygame.image.load("door.png")

        self.def_font1 = pygame.font.SysFont("georgia", 24)
        self.def_font2 = pygame.font.SysFont("georgia", 14)

        self.default_color = (255, 255, 255)
        self.dark_world_color = (0, 0, 0)
        self.alternate_world_color = (36, 214, 43)

        self.clock = pygame.time.Clock()
        self.clock_speed = 60

        self.wealth = 0
        self.target_wealth = 100
        self.energy = 0
        self.alternate_energy_amount = 10

        self.monster_coin_count = 20
        self.dark_world_monster_multiplier = 2
        self.monsters = self.create_monsters()
        self.coins = self.create_coins()
        self.doors = []

        self.is_game = True
        self.is_game_started = False
        self.is_won = False

        self.is_default_world = True
        self.is_dark_world = False
        self.is_alternate_world = False

        self.general_counter = 1
        self.dark_world_counter = 30

    def execute(self):
        rb = Robo(self.SCREEN_W, self.SCREEN_H, self.robot)

        while True:
            if self.is_game == False:
                self.show_ending_info()
                self.is_game_started = False

            self.check_events(rb)

            if self.is_game_started and self.is_game:
                self.limit_walls_robo(rb)
                rb.move_robo()

                if self.is_default_world:
                    self.execute_default_world(rb)
                if self.is_dark_world:
                    self.execute_dark_world(rb)

                    if self.dark_world_counter <= 0:
                        self.is_default_world = True
                        self.is_dark_world = False
                        self.is_alternate_world = False
                        self.reset_counters()
                        self.reset_coin_and_monsters()
                        self.monsters = self.create_monsters()

                    if self.dark_world_counter < 30 and self.dark_world_counter > 0:
                        if len(self.monsters) <= 10:
                            self.monsters += self.create_monsters()

                if self.is_alternate_world:
                    self.execute_alternate_world(rb)

                    if len(self.doors) <= 0:
                        self.is_default_world = True
                        self.is_dark_world = False
                        self.is_alternate_world = False
                        self.reset_counters()
                        self.reset_monsters()
                        self.monsters = self.create_monsters()

                self.window.blit(self.robot, (rb.x, rb.y))

            if not self.is_game_started and self.is_game:
                self.show_starting_info()

            pygame.display.flip()
            self.clock.tick(self.clock_speed)

    def execute_default_world(self, rb):
        self.window.fill(self.default_color)
        self.show_info(color=self.dark_world_color)

        for mn in self.monsters:
            mn.move_monster()
            self.monster_landing(mn)
            self.monster_attack(mn, rb)
            self.window.blit(self.monster, (mn.x, mn.y))

        for cn in self.coins:
            cn.move_coin()
            self.coin_gain(cn, rb)
            self.window.blit(self.coin, (cn.x, cn.y))

        self.add_coin_and_monsters()

    def execute_dark_world(self, rb):
        self.window.fill(self.dark_world_color)
        self.show_info(color=self.default_color)
        self.dark_world_count_info(color=self.default_color)

        self.window.blit(self.robot, (rb.x, rb.y))

        for mn in self.monsters:
            mn.move_monster()
            self.monster_landing(mn)
            self.monster_attack(mn, rb, current_world="dark_world")
            self.window.blit(self.monster, (mn.x, mn.y))

        if self.general_counter % 60 == 0:
            self.dark_world_counter -= 1

        self.general_counter += 1

    def execute_alternate_world(self, rb):
        self.window.fill(self.alternate_world_color)
        self.show_info(color=self.dark_world_color)

        for mn in self.monsters:
            mn.move_monster()
            self.monster_landing(mn)
            self.monster_attack(mn, rb)
            self.window.blit(self.monster, (mn.x, mn.y))

        for cn in self.coins:
            cn.move_coin()
            self.coin_gain(cn, rb)
            self.window.blit(self.coin, (cn.x, cn.y))

        self.alternate_world_gates()
        self.add_coin_and_monsters()

    def alternate_world_gates(self):
        for dr in self.doors:
            self.window.blit(self.door, (dr.x, dr.y))

            # Remove doors outside of windows
            if dr.y + self.door.get_height() + 20 < -1 or dr.y > self.SCREEN_H or dr.x < -1 or dr.x > self.SCREEN_W:
                self.doors = list(filter(lambda x: x != dr, self.doors))

            for mn in self.monsters:
                if mn.y + self.monster.get_height() > 0:
                    dr.catch_monster(mn)

                    if dr.y <= mn.y:
                        self.monsters = list(
                            filter(lambda x: x != mn, self.monsters))

            dr.move_door()

    def check_events(self, rb: Robo):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    rb.x_vel = -10
                if event.key == pygame.K_RIGHT:
                    rb.x_vel = 10
                if event.key == pygame.K_x:
                    self.open_alternate_world()
                if event.key == pygame.K_RETURN:
                    self.reset_game()
                if event.key == pygame.K_ESCAPE:
                    exit()

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    rb.x_vel = 0
                if event.key == pygame.K_RIGHT:
                    rb.x_vel = 0

    def limit_walls_robo(self, rb: Robo):
        if rb.x <= 0:
            rb.x_vel = 0
            rb.x = 1
        if rb.x >= self.SCREEN_W - self.robot.get_width():
            rb.x_vel = 0
            rb.x = (self.SCREEN_W - self.robot.get_width()) - 1
        if rb.y <= 0:
            rb.y_vel = 0
            rb.y = 1
        if rb.y >= self.SCREEN_H - self.robot.get_height():
            rb.y_vel = 0
            rb.y = (self.SCREEN_H - self.robot.get_height()) - 1

    def create_monsters(self, amount: int = None) -> list:
        if amount == None:
            amount = self.monster_coin_count

        return [Monster(self.SCREEN_W, self.SCREEN_H, self.monster) for i in range(amount)]

    def create_coins(self, amount: int = None) -> list:
        if amount == None:
            amount = self.monster_coin_count
        return [Coin(self.SCREEN_W, self.SCREEN_H, self.coin) for i in range(amount)]

    def create_doors(self, amount: int = 10) -> list:
        return [Door(self.SCREEN_W, self.SCREEN_H, self.door) for i in range(amount)]

    def monster_landing(self, mn: Monster):
        if mn.y >= self.SCREEN_H - self.monster.get_height():
            mn.y_vel = self.SCREEN_H - self.monster.get_height() - 1
            mn.y_vel = -10

            if mn.x + self.monster.get_width() < self.SCREEN_W // 2:
                mn.x_vel = randint(1, 5)
            else:
                mn.x_vel = randint(1, 5) * -1

        if mn.x + self.monster.get_width() < 0 or mn.x + self.monster.get_width() > self.SCREEN_W:
            self.monsters = list(filter(lambda x: x != mn, self.monsters))

    def monster_attack(self, mn: Monster, rb: Robo, current_world: str = 'default_world'):
        if mn.x <= rb.x + self.robot.get_width() / 2 and mn.x >= rb.x - self.robot.get_width() / 2:
            if mn.y <= rb.y + self.robot.get_height() / 2 and mn.y >= rb.y - self.robot.get_height() / 2:
                if current_world == 'dark_world':
                    self.is_game = False
                else:
                    self.is_default_world = False
                    self.is_alternate_world = False
                    self.is_dark_world = True

                    if self.energy >= self.alternate_energy_amount:
                        self.energy -= self.alternate_energy_amount
                    elif self.energy < self.alternate_energy_amount:
                        self.energy = 0

                self.monsters = []
                self.coins = []

                self.monsters = self.create_monsters(
                    self.monster_coin_count * self.dark_world_monster_multiplier)

    def coin_gain(self, cn: Coin, rb: Robo):
        if cn.x <= rb.x + self.robot.get_width() / 2 and cn.x >= rb.x - self.robot.get_width() / 2:
            if cn.y <= rb.y + self.robot.get_height() / 2 and cn.y >= rb.y - self.robot.get_height() / 2:
                self.coins = list(
                    filter(lambda coin: coin != cn, self.coins))
                self.wealth += 1
                self.energy += 1

                if self.wealth == self.target_wealth:
                    self.is_game = False
                    self.is_won = True

    def show_info(self, color: tuple):
        wealth_text = self.def_font1.render(
            f"Wealth: {self.wealth}", True, color)
        self.window.blit(
            wealth_text, (self.SCREEN_W - wealth_text.get_width() - 10, 10))

        energy_text = self.def_font1.render(
            f"Energy: {self.energy}", True, color)
        self.window.blit(
            energy_text, (self.SCREEN_W - energy_text.get_width() - 10, 10 + energy_text.get_height()))

        skill1_text = self.def_font2.render(
            f"X - Alternate World ({self.alternate_energy_amount})", True, color)
        self.window.blit(
            skill1_text, (self.SCREEN_W - skill1_text.get_width() - 10, 10 + energy_text.get_height() * 3))

    def dark_world_count_info(self, color):
        counter_text = self.def_font1.render(
            f"Remaining: {self.dark_world_counter}", True, color)
        self.window.blit(
            counter_text, (self.SCREEN_W - counter_text.get_width() - 10, 10 + counter_text.get_height() * 4))

    def add_coin_and_monsters(self, amount: int = None):
        if amount == None:
            amount = self.monster_coin_count

        if self.general_counter % 500 == 0:
            [self.monsters.append(i) for i in self.create_monsters(
                amount)]
            [self.coins.append(i)
             for i in self.create_coins(amount)]

        self.general_counter += 1

    def open_alternate_world(self):
        if self.energy >= self.alternate_energy_amount and self.is_alternate_world == False:
            self.energy -= self.alternate_energy_amount

            self.doors = self.create_doors(10)

            self.is_default_world = False
            self.is_dark_world = False
            self.is_alternate_world = True

            self.reset_counters()

    def reset_coin_and_monsters(self, amount: int = None):
        if amount == None:
            amount = self.monster_coin_count

        self.monsters = []
        self.coins = []
        [self.monsters.append(i) for i in self.create_monsters(
            amount)]
        [self.coins.append(i)
         for i in self.create_coins(amount)]

    def reset_monsters(self, amount: int = 0):
        if amount == None:
            amount = self.monster_coin_count

        self.monsters = []
        [self.monsters.append(i) for i in self.create_monsters(
            amount)]

    def reset_counters(self):
        self.general_counter = 1
        self.dark_world_counter = 30

    def show_starting_info(self, color: tuple = (1, 1, 1)):
        self.window.fill((255, 255, 255))

        def create_text(text):
            return self.def_font1.render(
                f"{text}", True, (color))

        header = create_text("AdventuresOfRobo")
        self.window.blit(
            header, (50, header.get_height()))

        description = create_text(
            f"Collect {self.target_wealth} coins to win.")
        self.window.blit(
            description, (50, description.get_height() * 2))

        description = create_text("Monsters will take you to the dark world.")
        self.window.blit(
            description, (50, description.get_height() * 3))

        description = create_text("Don't let them catch you.")
        self.window.blit(
            description, (50, description.get_height() * 4))

        description = create_text("Click enter to start.")
        self.window.blit(
            description, (50, description.get_height() * 6))

    def show_ending_info(self, color: tuple = (1, 1, 1)):
        self.window.fill((255, 255, 255))

        def create_text(text):
            return self.def_font1.render(
                f"{text}", True, (color))

        if self.is_won:
            header = create_text("YOU WON!")
            self.window.blit(
                header, (50, header.get_height()))

            description = create_text("Congratulations")
            self.window.blit(
                description, (50, description.get_height() * 2))

            description = create_text("Enter to play again, esc to exit.")
            self.window.blit(
                description, (50, description.get_height() * 4))

        else:
            header = create_text("YOU LOST!")
            self.window.blit(
                header, (50, header.get_height()))

            description = create_text(f"Your wealth: {self.wealth}")
            self.window.blit(
                description, (50, description.get_height() * 2))

            description = create_text(f"Target wealth: {self.target_wealth}")
            self.window.blit(
                description, (50, description.get_height() * 3))

            description = create_text("Enter to play again, esc to exit.")
            self.window.blit(
                description, (50, description.get_height() * 4))

    def reset_game(self):
        if self.is_game_started == False:
            self.wealth = 0
            self.energy = 0

            self.monsters = self.create_monsters()
            self.coins = self.create_coins()
            self.doors = []

            self.is_game = True
            self.is_game_started = True
            self.is_won = False

            self.is_default_world = True
            self.is_dark_world = False
            self.is_alternate_world = False

            self.reset_counters()


new_game = AdventuresOfRobo()
new_game.execute()
