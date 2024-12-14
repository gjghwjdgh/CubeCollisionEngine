# main.py

from Engine import Cube, np
import pygame
import random

pygame.init()

WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("3D 큐브 충돌 시뮬레이터")
clock = pygame.time.Clock()

cubes = [
    Cube(
        position=[
            random.uniform(-WIDTH // 2 + 100, WIDTH // 2 - 100),
            random.uniform(-HEIGHT // 2 + 100, HEIGHT // 2 - 100),
            random.uniform(300, 700),
        ],
        velocity=[
            random.uniform(-150, 150),
            random.uniform(-150, 150),
            random.uniform(-150, 150),
        ],
        size=100,
        color=(
            random.randint(100, 255),
            random.randint(100, 255),
            random.randint(100, 255),
        ),
        angular_velocity=np.random.uniform(-0.5, 0.5, 3),
    )
    for _ in range(10)
]

bounds = [[-WIDTH // 2, WIDTH // 2], [-HEIGHT // 2, HEIGHT // 2], [200, 800]]
light_pos = [0, 0, 0]
speed_multiplier = 1.0

background_stars = [
    (random.randint(0, WIDTH), random.randint(0, HEIGHT), random.randint(100, 255))
    for _ in range(200)
]


def draw_background(screen, width, height):
    for y in range(height):
        color = 50 + int((200 - 50) * (y / height))
        pygame.draw.line(screen, (color, color, color), (0, y), (width, y))

    for star in background_stars:
        pygame.draw.circle(
            screen, (star[2], star[2], star[2]), (star[0], star[1]), 2)


running = True
while running:
    dt = clock.tick(60) / 1000
    screen.fill((0, 0, 0))

    draw_background(screen, WIDTH, HEIGHT)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                speed_multiplier = 1.0
            elif event.key == pygame.K_2:
                speed_multiplier = 1.5
            elif event.key == pygame.K_3:
                speed_multiplier = 2.0
            elif event.key == pygame.K_4:
                speed_multiplier = 3.0

    for i, cube in enumerate(cubes):
        cube.update(dt, bounds, speed_multiplier)
        for j, other_cube in enumerate(cubes):
            if i != j and cube.is_colliding(other_cube):
                cube.resolve_collision(other_cube)

    cubes.sort(key=lambda c: c.transform.position[2])
    for cube in cubes:
        cube.draw(screen, WIDTH, HEIGHT, light_pos)

    pygame.display.flip()

pygame.quit()
