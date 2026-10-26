import pygame
from math import pi, cos, sin
import obd

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
PINK = (227, 0, 166)

WIDTH, HEIGHT = 800, 480
center = (510, HEIGHT / 2)
clock_radius = 200

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dashboard")

conn = obd.OBD("socket://localhost:35000", baudrate=38400, fast=False)


speed_state = 10
rpm_state = 100


_fonts = {}


def write_text(text, size, position):
    if size not in _fonts:
        _fonts[size] = pygame.font.SysFont("Arial", size, True, False)
    surf = _fonts[size].render(text, True, WHITE)
    screen.blit(surf, surf.get_rect(center=position))


# theta is in degrees
def polar_to_cartesian(r, theta, width_center, height_center):
    x = r * sin(pi * theta / 180)
    y = r * cos(pi * theta / 180)
    return x + width_center, -(y - height_center)


# rg_end is non-inclusive
def clock_nums(rg_strt, rg_end, mult, size, r, angle, strt_angle, width_center, height_center):
    for number in range(rg_strt, rg_end, mult):
        write_text(str(number), size,
                   polar_to_cartesian(r, ((number / mult) * angle + strt_angle), width_center, height_center))


def ticks(rg_strt, rg_end, r, angle, strt_angle, width_center, height_center):
    for number in range(rg_strt, rg_end):
        tick_start = polar_to_cartesian(r, (number * angle + strt_angle), width_center, height_center)
        if number % 10 == 0:
            tick_end = polar_to_cartesian(r - 25, (number * angle + strt_angle), width_center, height_center)
        elif number % 5 == 0:
            tick_end = polar_to_cartesian(r - 20, (number * angle + strt_angle), width_center, height_center)
        else:
            tick_end = polar_to_cartesian(r - 15, (number * angle + strt_angle), width_center, height_center)
        pygame.draw.line(screen, PINK, tick_start, tick_end, 2)


clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

    screen.fill(BLACK)

    # SPEEDOMETER
    write_text("Speedometer", 30, (WIDTH / 4, (HEIGHT / 2) - (clock_radius / 2) - 35))
    clock_nums(0, 40, 5, 40, (clock_radius - 65), 38.57143, 223.2, (WIDTH / 4), (HEIGHT / 2) + 65)
    ticks(0, 36, (clock_radius - 15), 7.714286, 223.2, WIDTH / 4, (HEIGHT / 2) + 65)
    speed = max(0, min(35, speed_state))
    theta = (speed * (270.0 / 35.0)) + (223.2 - (270.0 / 35.0))
    pygame.draw.line(screen, PINK, ((WIDTH / 2) / 2, HEIGHT / 2 + 45),
                     polar_to_cartesian(140, theta, WIDTH / 4, (HEIGHT / 2) + 45), 4)
    pygame.draw.rect(screen, PINK, [WIDTH / 4.8, HEIGHT - 55, WIDTH / 12, HEIGHT / 9], 3)
    write_text(str(speed), 50, (WIDTH / 4, (HEIGHT - 30)))

    # RPM
    write_text("RPM Gauge", 30, ((WIDTH / 4) * 3, (HEIGHT / 2) - (clock_radius / 2) - 35))
    clock_nums(0, 5500, 500, 20, (clock_radius - 65), 27, 223.2, (WIDTH / 4) * 3, (HEIGHT / 2) + 65)
    ticks(0, 101, (clock_radius - 15), 2.7, 223.2, (WIDTH / 4) * 3, (HEIGHT / 2) + 65)
    rpm = max(0, min(5000, rpm_state))
    theta = (rpm * (270.0 / 5000.0)) + 223.2
    pygame.draw.line(screen, PINK, (((WIDTH / 4) * 3), (HEIGHT / 2) + 45),
                     polar_to_cartesian(140, theta, (WIDTH / 4) * 3, (HEIGHT / 2) + 45), 4)
    pygame.draw.rect(screen, PINK, [(WIDTH / 2) + (WIDTH / 4.8), HEIGHT - 55, WIDTH / 12, HEIGHT / 9], 3)
    write_text(str(rpm), 50, ((WIDTH / 4) * 3, (HEIGHT - 30)))

    r = conn.query(obd.commands.RPM)
    if not r.is_null():
        rpm_state = r.value.magnitude

    pygame.display.flip()
    clock.tick(60)

pygame.quit()