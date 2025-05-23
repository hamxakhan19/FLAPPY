import pygame
import sys
import random

pygame.init()

# Fullscreen setup
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("Flappy Bird Fullscreen")

# Load and scale images
bg = pygame.image.load("background.jpg")
bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))

bird_width = int(WIDTH * 0.1)
bird_height = int(bird_width * 0.7)

bird_imgs = [pygame.image.load("bird1.png"), pygame.image.load("bird3.png")]
bird_imgs = [pygame.transform.scale(img, (bird_width, bird_height)) for img in bird_imgs]

bird_dead_img = pygame.image.load("bird2.png")
bird_dead_img = pygame.transform.scale(bird_dead_img, (bird_width, bird_height))

pipe_width = int(WIDTH * 0.06)  # Reduced pipe width
pipe_height = int(HEIGHT * 0.6)

pipe_surface = pygame.Surface((pipe_width, pipe_height))
pipe_surface.fill((255, 255, 0))  # Yellow pipes

font = pygame.font.SysFont(None, int(WIDTH * 0.05))
title_font = pygame.font.SysFont('comicsansms', int(WIDTH * 0.12), bold=True)
clock = pygame.time.Clock()

gravity = 0.5 * (HEIGHT / 640)
jump = -8 * (HEIGHT / 640)
bird_x = int(WIDTH * 0.15)
bird_y = HEIGHT // 2
bird_movement = 0
pipe_gap = int(HEIGHT * 0.27)
pipe_distance = int(WIDTH * 0.55)
score = 0
best_score = 0

bg_x = 0
pipes = []

bird_frame = 0
last_frame_time = pygame.time.get_ticks()

game_active = False
game_over_time = 0
paused = False
show_startup = True

startup_bg_x = 0
startup_bird_x = bird_x
startup_bird_y = HEIGHT // 2
startup_bird_movement = 0
startup_bird_frame = 0
startup_last_frame_time = pygame.time.get_ticks()
startup_pipes = []

button_width, button_height = int(WIDTH * 0.3), int(HEIGHT * 0.1)
button_rect = pygame.Rect((WIDTH//2 - button_width//2, HEIGHT//2 + button_height), (button_width, button_height))

pause_button = pygame.Rect(WIDTH - 100, 20, 80, 40)
resume_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 - 20, 200, 60)

def rotate_bird(bird, movement):
    max_up_angle = -25
    max_down_angle = 25
    angle = max(min(-movement * 3, max_down_angle), max_up_angle)
    return pygame.transform.rotozoom(bird, angle, 1)

def create_pipe():
    height = random.randint(int(HEIGHT * 0.15), int(HEIGHT * 0.75))
    top_pipe = pipe_surface.get_rect(midbottom=(WIDTH + pipe_width, height - pipe_gap // 2))
    bottom_pipe = pipe_surface.get_rect(midtop=(WIDTH + pipe_width, height + pipe_gap // 2))
    return top_pipe, bottom_pipe

def reset_game():
    global pipes, bird_y, bird_movement, score, game_active, game_over_time, paused
    pipes = []
    bird_y = HEIGHT // 2
    bird_movement = 0
    score = 0
    game_active = True
    game_over_time = 0
    paused = False

def draw_pipes(pipes):
    for pipe in pipes:
        if pipe.bottom >= HEIGHT:
            screen.blit(pipe_surface, pipe)
        else:
            flip_pipe = pygame.transform.flip(pipe_surface, False, True)
            screen.blit(flip_pipe, pipe)

def check_collision(pipes, bird_rect):
    for pipe in pipes:
        if bird_rect.colliderect(pipe):
            return False
    if bird_rect.top <= 0 or bird_rect.bottom >= HEIGHT:
        return False
    return True

def draw_text_center(text, pos, color=(255,255,255), big=False):
    render = (title_font if big else font).render(text, True, color)
    rect = render.get_rect(center=pos)
    screen.blit(render, rect)

def game_over_screen():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    draw_text_center("Game Over", (WIDTH//2, HEIGHT//2 - int(HEIGHT * 0.05)))
    draw_text_center("Press SPACE to Restart", (WIDTH//2, HEIGHT//2 + int(HEIGHT * 0.05)), (200, 200, 200))

def draw_startup_screen():
    global startup_bg_x, startup_bird_x, startup_bird_y, startup_bird_movement, startup_bird_frame, startup_last_frame_time, startup_pipes

    startup_bg_x -= 1
    if startup_bg_x <= -WIDTH:
        startup_bg_x = 0
    screen.blit(bg, (startup_bg_x, 0))
    screen.blit(bg, (startup_bg_x + WIDTH, 0))

    now = pygame.time.get_ticks()
    if now - startup_last_frame_time > 200:
        startup_bird_frame = (startup_bird_frame + 1) % 2
        startup_last_frame_time = now

    startup_bird_movement += gravity / 4
    startup_bird_y += startup_bird_movement
    startup_bird_x += 2
    if startup_bird_y > HEIGHT//2 + 30:
        startup_bird_movement = -2
    if startup_bird_y < HEIGHT//2 - 30:
        startup_bird_movement = 2

    if len(startup_pipes) == 0 or startup_pipes[-1].centerx < WIDTH - pipe_distance:
        startup_pipes.extend(create_pipe())
    for pipe in startup_pipes:
        pipe.centerx -= 2
    startup_pipes = [pipe for pipe in startup_pipes if pipe.right > -pipe_width]
    draw_pipes(startup_pipes)

    bird_rect = bird_imgs[startup_bird_frame].get_rect(center=(startup_bird_x, int(startup_bird_y)))
    rotated_bird = rotate_bird(bird_imgs[startup_bird_frame], startup_bird_movement)
    rotated_rect = rotated_bird.get_rect(center=bird_rect.center)
    screen.blit(rotated_bird, rotated_rect)

    # Fixed FLAPPY title with proper spacing
    colors = [(255, 0, 0), (255, 165, 0), (255, 255, 0), (0, 200, 0), 
              (0, 0, 255), (128, 0, 128), (255, 0, 255)]
    
    title = "FLAPPY"
    x_offset = WIDTH//2 - 200  # Adjusted starting position
    y_pos = HEIGHT//2 - 100
    letter_spacing = 70  # Increased spacing between letters
    
    for i, ch in enumerate(title):
        color = colors[i % len(colors)]
        letter = title_font.render(ch, True, color)
        screen.blit(letter, (x_offset + i * letter_spacing, y_pos))

    # Simple play button without merging
    pygame.draw.rect(screen, (0, 200, 0), button_rect)
    pygame.draw.rect(screen, (255, 255, 255), button_rect, 3)  # White border
    play_text = font.render("PLAY", True, (255, 255, 255))
    screen.blit(play_text, (button_rect.centerx - play_text.get_width()//2, 
                          button_rect.centery - play_text.get_height()//2))

running = True
while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_SPACE:
                if game_active and not paused:
                    bird_movement = jump
                elif not game_active and not show_startup:
                    reset_game()
            if event.key == pygame.K_p and game_active:
                paused = not paused
        if event.type == pygame.MOUSEBUTTONDOWN:
            if show_startup and button_rect.collidepoint(event.pos):
                show_startup = False
                reset_game()
            if game_active and not paused and pause_button.collidepoint(event.pos):
                paused = True
            elif paused and resume_button.collidepoint(event.pos):
                paused = False

    if show_startup:
        draw_startup_screen()

    else:
        if game_active and not paused:
            bg_x -= 1
            if bg_x <= -WIDTH:
                bg_x = 0
            screen.blit(bg, (bg_x, 0))
            screen.blit(bg, (bg_x + WIDTH, 0))

            now = pygame.time.get_ticks()
            if now - last_frame_time > 80:
                bird_frame = (bird_frame + 1) % 2
                last_frame_time = now

            bird_movement += gravity
            bird_y += bird_movement
            bird_rect = bird_imgs[bird_frame].get_rect(center=(bird_x, bird_y))

            rotated_bird = rotate_bird(bird_imgs[bird_frame], bird_movement)
            rotated_rect = rotated_bird.get_rect(center=bird_rect.center)
            screen.blit(rotated_bird, rotated_rect)

            if len(pipes) == 0 or pipes[-1].centerx < WIDTH - pipe_distance:
                pipes.extend(create_pipe())
            for pipe in pipes:
                pipe.centerx -= 4
            pipes = [pipe for pipe in pipes if pipe.right > -pipe_width]
            draw_pipes(pipes)

            # Check collision
            if not check_collision(pipes, bird_rect):
                game_active = False
                if score > best_score:
                    best_score = score
                game_over_time = pygame.time.get_ticks()

            # Update score
            for pipe in pipes:
                if pipe.centerx == bird_x:
                    score += 0.5

            draw_text_center(f"Score: {int(score)}", (WIDTH // 2, int(HEIGHT * 0.1)))
            draw_text_center(f"Best: {int(best_score)}", (WIDTH // 2, int(HEIGHT * 0.15)))

            # Pause button
            pygame.draw.rect(screen, (200, 200, 0), pause_button)
            draw_text_center("Pause", pause_button.center, color=(0,0,0))

        elif paused:
            # Show paused screen
            draw_text_center("Paused", (WIDTH//2, HEIGHT//2 - 30), big=True)
            pygame.draw.rect(screen, (0, 200, 0), resume_button)
            draw_text_center("Resume", resume_button.center, color=(0,0,0))
        else:
            # Game over screen with falling bird rotation effect
            screen.blit(bg, (bg_x, 0))
            screen.blit(bg, (bg_x + WIDTH, 0))

            bird_movement += gravity
            bird_y += bird_movement

            angle = min(bird_movement * 5, 90)
            rotated_bird = pygame.transform.rotozoom(bird_dead_img, -angle, 1)
            rotated_rect = rotated_bird.get_rect(center=(bird_x, bird_y))

            screen.blit(rotated_bird, rotated_rect)

            draw_pipes(pipes)
            draw_text_center(f"Score: {int(score)}", (WIDTH // 2, int(HEIGHT * 0.1)))
            draw_text_center(f"Best: {int(best_score)}", (WIDTH // 2, int(HEIGHT * 0.15)))
            game_over_screen()

    pygame.display.update()

pygame.quit()
sys.exit()