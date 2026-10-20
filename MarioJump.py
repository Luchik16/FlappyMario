import pygame
from sys import exit
import random


GAME_WIDTH = 360
GAME_HEIGHT = 640


bird_x = GAME_WIDTH / 8
bird_y = GAME_HEIGHT / 2
bird_width = 34
bird_height = 24


class Bird(pygame.Rect):
    def __init__(self, img):
        pygame.Rect.__init__(self, bird_x, bird_y, bird_width, bird_height)
        self.img = img



pipe_x = GAME_WIDTH
pipe_y = 0
pipe_width = 64
pipe_height = 512


class Pipe(pygame.Rect):
    def __init__(self, img, is_top):
        pygame.Rect.__init__(self, pipe_x, pipe_y, pipe_width, pipe_height)
        self.img = img
        self.is_top = is_top
        self.passed = False


background_image = pygame.image.load("flappybirdbg.png")
bird_image = pygame.image.load("flappybird.png")
bird_image = pygame.transform.scale(bird_image, (bird_width, bird_height))
top_pipe_image = pygame.image.load("toppipe.png")
top_pipe_image = pygame.transform.scale(top_pipe_image, (pipe_width, pipe_height))
bottom_pipe_image = pygame.image.load("bottompipe.png")
bottom_pipe_image = pygame.transform.scale(bottom_pipe_image, (pipe_width, pipe_height))


bird = Bird(bird_image)
pipes = []
velocity_x = -2
velocity_y = 0
gravity = 0.4
score = 0
best_score = 0
game_over = False

sucking = False
suck_pipe = None
suck_speed = 3


def set_game_over():
    global game_over, best_score
    game_over = True
    best_score = max(best_score, int(score))



def draw_text_centered(surface, text, font, color, center_y, shadow=True):
    """Рисует текст по центру экрана по горизонтали, с тенью."""
    if shadow:
        shadow_render = font.render(text, True, (0, 0, 0))
        shadow_rect = shadow_render.get_rect(center=(GAME_WIDTH // 2 + 2, center_y + 2))
        surface.blit(shadow_render, shadow_rect)
    text_render = font.render(text, True, color)
    text_rect = text_render.get_rect(center=(GAME_WIDTH // 2, center_y))
    surface.blit(text_render, text_rect)


def draw_game_over():
   
    overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 140))

    
    panel = pygame.Rect(0, 0, 280, 230)
    panel.center = (GAME_WIDTH // 2, GAME_HEIGHT // 2)
    pygame.draw.rect(overlay, (35, 35, 45, 230), panel, border_radius=18)
    pygame.draw.rect(overlay, (255, 255, 255, 255), panel, width=3, border_radius=18)
    window.blit(overlay, (0, 0))

    
    draw_text_centered(window, "GAME OVER", font_big, (255, 80, 80), panel.top + 50)
    draw_text_centered(window, f"Score: {int(score)}", font_medium, "white", panel.top + 110)
    draw_text_centered(window, f"Best: {best_score}", font_medium, (255, 215, 0), panel.top + 150)

    
    if (pygame.time.get_ticks() // 500) % 2 == 0:
        draw_text_centered(window, "Press SPACE to restart", font_small, (200, 200, 200), panel.top + 200, shadow=False)


def draw():
    window.blit(background_image, (0, 0))
    window.blit(bird.img, bird)  

    for pipe in pipes:
        window.blit(pipe.img, pipe)

    if game_over:
        draw_game_over()
    else:
        
        draw_text_centered(window, str(int(score)), font_big, "white", 45)


def suck_in():
    """Затягивает птицу внутрь трубы. Когда она полностью скрылась, то Game Over."""
    global sucking

    target_x = suck_pipe.x + suck_pipe.width // 2 - bird.width // 2
    dx = target_x - bird.x
    bird.x += max(-suck_speed, min(suck_speed, dx))

    if suck_pipe.is_top:
        bird.y -= suck_speed
        inside = bird.bottom <= suck_pipe.bottom - bird.height
    else:
        bird.y += suck_speed
        inside = bird.y >= suck_pipe.y + bird.height

    if inside and bird.x == target_x:
        sucking = False
        set_game_over()


def move():
    global velocity_y, score, sucking, suck_pipe

    if sucking:
        suck_in()
        return

    velocity_y += gravity
    bird.y += velocity_y
    bird.y = max(bird.y, 0)

    if bird.y > GAME_HEIGHT:
        set_game_over()
        return

    for pipe in pipes:
        pipe.x += velocity_x

        if not pipe.passed and bird.x > pipe.x + pipe.width:
            score += 0.5
            pipe.passed = True

        if bird.colliderect(pipe):
            sucking = True
            suck_pipe = pipe
            return

    while len(pipes) > 0 and pipes[0].x < -pipe_width:
        pipes.pop(0)


def create_pipes():
    random_pipe_y = pipe_y - pipe_height / 4 - random.random() * (pipe_height / 2)
    opening_space = GAME_HEIGHT / 4

    top_pipe = Pipe(top_pipe_image, True)
    top_pipe.y = random_pipe_y
    pipes.append(top_pipe)

    bottom_pipe = Pipe(bottom_pipe_image, False)
    bottom_pipe.y = top_pipe.y + top_pipe.height + opening_space
    pipes.append(bottom_pipe)


pygame.init()
window = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
pygame.display.set_caption("Flappy Bird")
clock = pygame.time.Clock()

font_big = pygame.font.SysFont("Comic Sans MS", 45, bold=True)
font_medium = pygame.font.SysFont("Comic Sans MS", 30)
font_small = pygame.font.SysFont("Comic Sans MS", 20)

create_pipes_timer = pygame.USEREVENT + 0
pygame.time.set_timer(create_pipes_timer, 1500)

while True:  
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if event.type == create_pipes_timer and not game_over and not sucking:
            create_pipes()

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SPACE, pygame.K_x, pygame.K_UP):
                if sucking:
                    continue

                if game_over:
                    
                    bird.x = bird_x
                    bird.y = bird_y
                    velocity_y = 0
                    pipes.clear()
                    score = 0
                    sucking = False
                    suck_pipe = None
                    game_over = False
                else:
                    velocity_y = -6

    
    if not game_over:
        move()
    draw()
    pygame.display.update()
    clock.tick(60)