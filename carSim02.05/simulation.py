import math
import random
import sys
import os
from typing import Tuple

import neat
import pygame

from car import Car
from toggle_button import ToggleButton

f = 1.6

WIDTH = 1920/2 * f     #
HEIGHT = 1080/2 * f
window_size = (WIDTH, HEIGHT)

time_flip = 0.01  # 10ms

CAR_SIZE_X = 23.75 * f
CAR_SIZE_Y = 10 * f

BORDER_COLOR: tuple[int, int, int, int] = (255, 255, 255, 255)  # Color To Crash on Hit

current_generation = 0  # Generation counter

# Initialize PyGame And The Display
pygame.init()
screen = pygame.display.set_mode(window_size, pygame.RESIZABLE)  # , pygame.FULLSCREEN

# 创建按钮
switch_button = ToggleButton(WIDTH / 1.5, HEIGHT - 150, 'crash', 'rebound', 'stop')
switch_button.draw(screen)


def run_simulation(genomes, config):

    # Empty Collections For Nets and Cars
    nets = []
    cars = []

    # For All Genomes Passed Create A New Neural Network
    for i, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        g.fitness = 0

        cars.append(Car())

    # Clock Settings
    # Font Settings & Loading Map
    clock = pygame.time.Clock()
    generation_font = pygame.font.SysFont("Arial", 15)
    alive_font = pygame.font.SysFont("Arial", 10)
    game_map = pygame.image.load('map.png').convert()        # Convert Speeds Up A Lot
    game_map = pygame.transform.scale(game_map, window_size)

    global current_generation
    current_generation += 1

    # Simple Counter To Roughly Limit Time (Not Good Practice)
    counter = 0

    while True:
        # Exit On Quit Event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            switch_button.handle_event(event)

        # For Each Car Get The Acton It Takes
        for i, car in enumerate(cars):
            output = nets[i].activate(car.get_data())
            choice = output.index(max(output))
            jia = 0.5 * f

            if car.angle_enable:
                if choice == 0:
                    car.angle += 10  # Left
                elif choice == 1:
                    car.angle -= 10  # Right
                elif choice == 2:
                    if (car.speed - jia > 4):
                        car.speed -= jia  # Slow Down
                else:
                    car.speed += jia  # Speed Up
            else:
                break

        # Check If Car Is Still Alive
        # Increase Fitness If Yes And Break Loop If Not
        still_alive = 0
        for i, car in enumerate(cars):
            if car.is_alive():
                still_alive += 1
                car.update(game_map)
                genomes[i][1].fitness += car.get_reward()

        if still_alive == 0:
            break

        counter += 1
        if counter == 15 * 40:  # Stop After About 20 Seconds
            break

        # Draw Map And All Cars That Are Alive
        screen.blit(game_map, (0, 0))
        for car in cars:
            if car.is_alive():
                car.draw(screen)

        # Display Info
        text = generation_font.render("Generation: " + str(current_generation), True, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = (900 / 4 * f, 450 / 2 * f)
        screen.blit(text, text_rect)

        text = alive_font.render("Still Alive: " + str(still_alive), True, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = (900 / 4 * f, 490 / 2 * f)
        screen.blit(text, text_rect)

        switch_button.draw(screen)
        pygame.display.flip()
        clock.tick(1 / time_flip)  # 100 FPS 10ms