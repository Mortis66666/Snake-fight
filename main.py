import pygame
import random
import time
import enum
from dataclasses import dataclass

pygame.init()


width, height = 600, 600
win = pygame.display.set_mode((width, height))
pygame.display.set_caption("Snake Fight")

font = pygame.font.SysFont("comicsans", 30)


# Colours

WHITE = (233, 233, 233)
BLACK = (0, 0, 0)
RED = (233, 0, 0)
GREEN = (0, 233, 0)
BLUE = (0, 0, 233)
PURPLE = (233, 0, 233)


greencrash = pygame.USEREVENT + 1
bluecrash = pygame.USEREVENT + 2

class direction(enum.Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

class species(enum.Enum):
    NORMAL = 2
    MAGIC = 1

@dataclass
class Food:
    x = width//2
    y = height//2
    type = species.NORMAL

    def blit(self):
        pygame.draw.circle(win, (RED if self.type == species.NORMAL else PURPLE), (self.x, self.y), 10)

    def ate(self):
        self.x = random.choice(list(range(0, 601, 5)))
        self.y = random.choice(list(range(0, 601, 5)))
        self.type = species(bool(random.randint(0, 5))+1)

    def reset(self):
        self.x = width//2
        self.y = height//2
        self.type = species.NORMAL

    @property
    def value(self):
        return 1 if self.type == species.NORMAL else 3

@dataclass
class SnakeBody:

    x: int
    y: int
    color: tuple

    def blit(self):
        pygame.draw.circle(win, self.color, (self.x, self.y), 10)

    def move(self, direction: direction):
        match direction:
            case direction.RIGHT:
                self.x += 5
            case direction.LEFT:
                self.x -= 5
            case direction.UP:
                self.y -= 5
            case direction.DOWN:
                self.y += 5

        if self.x < 0:
            self.x += width

        elif self.x > width:
            self.x = width - self.x

        if self.y < 0:
            self.y += height

        elif self.y > height:
            self.y = height - self.y

    @property
    def position(self):
        return self.x, self.y

    def move_to(self, postiion: tuple):
        self.x, self.y = postiion


@dataclass
class Snake:

    facing: direction
    body: list
    color: tuple
    waiting = 0


    def blit(self):

        for cell in self.body:
            cell.blit()

    def move(self, food: Food, snake):
        
        position = None
        for index, cell in enumerate(self.body):

            if index == 0:
                position = cell.position
                cell.move(self.facing)
            
            else:
                prev = cell.position
                cell.move_to(position)
                position = prev

        if self.waiting:
            self.body.append(SnakeBody(position[0], position[1], self.color))
            self.waiting -= 1

        x, y = self.body[0].position
        
        if abs(x - food.x) < 11 and abs(y - food.y) < 11:
            self.eat(food)

        if self.colliderect(snake):
            if self.color == GREEN:
                pygame.event.post(pygame.event.Event(greencrash))
            else:
                pygame.event.post(pygame.event.Event(bluecrash))
        if self.colliderect(self, ignore_head = True):
            if self.color == GREEN:
                pygame.event.post(pygame.event.Event(greencrash))
            else:
                pygame.event.post(pygame.event.Event(bluecrash))


    def change_direction(self, direction: direction):
        self.facing = direction

    def __iter__(self):
        self.i = 0
        return self

    def __next__(self):
        if self.i == len(self.body) - 1:
            raise StopIteration
        else:
            x = self.i
            self.i += 1
            return self.body[x]

    def eat(self, food: Food):
        self.waiting += food.value
        food.ate()

    def colliderect(self, snake, ignore_head = False) -> bool:
        return self.body[0].position in map(lambda x:x.position, [x for i, x in enumerate(snake.body) if i>0 or not ignore_head])

    def handle(self, key):
        if self.color == GREEN:
            if key[pygame.K_w] and self.facing != direction.DOWN:
                self.change_direction(direction.UP)
            elif key[pygame.K_s] and self.facing != direction.UP:
                self.change_direction(direction.DOWN)
            elif key[pygame.K_a] and self.facing != direction.RIGHT:
                self.change_direction(direction.LEFT)
            elif key[pygame.K_d] and self.facing != direction.LEFT:
                self.change_direction(direction.RIGHT)

        else:
            if key[pygame.K_UP] and self.facing != direction.DOWN:
                self.change_direction(direction.UP)
            elif key[pygame.K_DOWN] and self.facing != direction.UP:
                self.change_direction(direction.DOWN)
            elif key[pygame.K_LEFT] and self.facing != direction.RIGHT:
                self.change_direction(direction.LEFT)
            elif key[pygame.K_RIGHT] and self.facing != direction.LEFT:
                self.change_direction(direction.RIGHT)

                






class Game:

    food = Food()

    green_snake = Snake(direction.RIGHT, [
        SnakeBody(width//2 - 160, height//2, GREEN),
        SnakeBody(width//2 - 165, height//2, GREEN)
        ], GREEN)

    blue_snake = Snake(direction.LEFT, [
        SnakeBody(width//2 + 160, height//2, BLUE),
        SnakeBody(width//2 + 165, height//2, BLUE)
        ], BLUE)


    def draw(self): # the draw function
        win.fill(BLACK)

        self.food.blit()
        self.green_snake.blit()
        self.blue_snake.blit()

        pygame.display.update()

    def choose(self) -> int:
        return random.randint(0, 1)

    def move(self):
        if self.choose():
            self.green_snake.move(self.food, self.blue_snake)
            self.blue_snake.move(self.food, self.green_snake)
        else:
            self.blue_snake.move(self.food, self.green_snake)
            self.green_snake.move(self.food, self.blue_snake)

    def handle(self, key):
        if self.choose():
            self.green_snake.handle(key)
            self.blue_snake.handle(key)
        else:
            self.blue_snake.handle(key)
            self.green_snake.handle(key)



    def start(self):

        # In game data
        run = True
        start = False
        clock = pygame.time.Clock()
        fps = 60 # Frame per second
        crashed = []
    

        while run:
            clock.tick(fps)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    pygame.quit()
                elif event.type == pygame.KEYDOWN:
                    start = True
                    pressed = pygame.key.get_pressed()
                    self.handle(pressed)
                if event.type == greencrash:
                    crashed.append("Blue")
                if event.type == bluecrash:
                    crashed.append("Green")

            if crashed:
                run = False
                text = None
                if len(crashed) == 2:
                    text = font.render("Draw", True, WHITE)
                else:
                    text = font.render(f"{crashed[0]} win", True, WHITE)

                win.blit(text, (width//2 - text.get_width()//2, 0))
                pygame.display.update()
                time.sleep(3)

                self.food.reset()
                self.green_snake = Snake(direction.RIGHT, [
                    SnakeBody(width//2 - 160, height//2, GREEN),
                    SnakeBody(width//2 - 165, height//2, GREEN)
                    ], GREEN)

                self.blue_snake = Snake(direction.LEFT, [
                    SnakeBody(width//2 + 160, height//2, BLUE),
                    SnakeBody(width//2 + 165, height//2, BLUE)
                    ], BLUE)

                self.start()


            if run:
                if start:
                    self.move()
                self.draw()


if __name__ == "__main__":
    game = Game()
    game.start()
