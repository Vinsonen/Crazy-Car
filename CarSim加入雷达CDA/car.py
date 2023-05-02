import math
import random
import sys
import os
from typing import Tuple

import neat
import pygame
import simulation
import numpy as np

f = 0.8

WIDTH = 1920 * f  #
HEIGHT = 1080 * f
window_size = (WIDTH, HEIGHT)

time_flip = 0.01  # 10ms

CAR_SIZE_X = 23.75*2 * f
CAR_SIZE_Y = 10*2 * f

BORDER_COLOR: tuple[int, int, int, int] = (255, 255, 255, 255)  # Color To Crash on Hit


class Car:

    def __init__(self):
        # Load Car Sprite and Rotate
        self.sprite = pygame.image.load('car.png').convert()  # Convert Speeds Up A Lot
        self.sprite = pygame.transform.scale(self.sprite, (CAR_SIZE_X, CAR_SIZE_Y))
        self.rotated_sprite = self.sprite

        # self.position = [690, 740] # Starting Position
        # self.position = [400 * f, 415 * f]  # Starting Position
        self.position = [840 * f, 930 * f]
        self.corners = []
        self.angle = 0
        self.speed = 0
        self.speed_set = False  # Flag For Default Speed Later on

        self.center = [self.position[0] + CAR_SIZE_X / 2, self.position[1] + CAR_SIZE_Y / 2]  # Calculate Center

        self.radars = []  # List For Sensors / Radars
        self.drawing_radars = []  # Radars To Be Drawn
        self.radars_enable = True

        self.alive = True  # Boolean To Check If Car is Crashed
        self.angle_enable = True
        self.drawradar_enable = True

        self.distance = 0  # Distance Driven
        self.time = 0  # Time Passed

    def draw(self, screen):
        screen.blit(self.rotated_sprite, self.position)  # Draw Sprite
        self.draw_radar(screen)  # OPTIONAL FOR SENSORS

    def draw_radar(self, screen):
        # Optionally Draw All Sensors / Radars
        if self.drawradar_enable:
            for radar in self.radars:   # 拿到目的坐标画曲线
                position = radar[0]
                pygame.draw.line(screen, (0, 255, 0), self.center, position, 1)
                pygame.draw.circle(screen, (0, 255, 0), position, 5)
        else:
            return

    def check_radar(self, degree, game_map):  # , midlength):   # degree 分别代表三个方向的雷达  检查到边缘的距离
        # midradar = False
        length = 0
        x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * length)
        y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * length)

        # While We Don't Hit BORDER_COLOR AND length < 300 (just a max) -> go further and further
        while not game_map.get_at((x, y)) == BORDER_COLOR and length < 245 * f:
            length = length + 1
            x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * length)
            y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * length)

        # Calculate Distance To Border And Append To Radars List
        dist = int(math.sqrt(math.pow(x - self.center[0], 2) + math.pow(y - self.center[1], 2)))
        self.radars.append([(x, y), dist])

    def get_data(self):
        # Get Distances To Border
        # 通过雷达来确定转弯方向
        radars = self.radars
        return_values = [0, 0, 0, 0, 0]
        for i, radar in enumerate(radars):
            return_values[i] = int(radar[1] / 30)

        return return_values

    def linearisierungDA(self, dist):
        A = 23962
        B = -20
        # 对dist进行等比例缩放  每个像素乘上比例*f
        real_dist = (dist * 1900) / WIDTH  # 图片上的960
        analogwert = (A / real_dist) + B
        return analogwert

    def rebound_action(self, game_map, point):
        # sfa反射角度的计算
        self.speed = 1

        point1 = [0, 0]
        radius = 20
        for i in range(0, 360, 10):
            angle = math.radians(i)
            x = point[0] + radius * math.cos(angle)
            y = point[1] + radius * math.sin(angle)
            if game_map.get_at([int(x), int(y)]) == BORDER_COLOR and game_map.get_at(
                    [int(point[0] + radius * math.cos(angle + 5)),
                     int(point[1] + radius * math.sin(angle + 5))]) == (0, 0, 0, 0):
                point1 = [int(x), int(y)]
                break

        # 计算两个反射面和入射角向量
        v1 = np.array([point1[0] - point[0], point1[1] - point[1]])  # np.array(point1) - np.array(point)
        theta = np.radians(self.angle)
        v2 = np.array([np.cos(theta), np.sin(theta)])

        # 计算反射向量   计算反射向量与参考坐标轴正方向的夹角，并转化为角度制的角度值
        reflection = v1 - 2 * (np.dot(v1, v2) / np.dot(v2, v2)) * v2
        angle_reflection = np.degrees(np.arctan2(reflection[1], reflection[0]))
        return angle_reflection

    def check_collision(self, game_map):
        # 检查碰撞
        # self.alive = True
        self.checkpoint_count = 0
        for point in self.corners:
            # If Any Corner Touches Border Color -> Crash
            # Assumes Rectangle
            check = True
            if game_map.get_at((int(point[0]), int(point[1]))) == BORDER_COLOR and check:
                self.checkpoint_count += 1
                if self.checkpoint_count >= 2:
                    self.alive = False

                status = simulation.switch_3button.get_status()
                check = not check
                if status == 0:
                    self.alive = False
                elif status == 1:
                    self.speed = 0
                    self.angle_enable, self.drawradar_enable = False, False
                elif status == 2:
                    self.angle = self.rebound_action(game_map, point)

            break

    def update(self, game_map):
        # Set The Speed To 20 For The First Time
        # Only When Having 4 Output Nodes With Speed Up and Down
        if not self.speed_set:
            self.speed = 2 * f
            self.speed_set = True

        # Get Rotated Sprite And Move Into The Right X-Direction
        # Don't Let The Car Go Closer Than 20px To The Edge
        self.rotated_sprite = self.rotate_center(self.sprite, self.angle)
        self.position[0] += math.cos(math.radians(360 - self.angle)) * self.speed
        self.position[0] = max(self.position[0], 20 * f)
        self.position[0] = min(self.position[0], WIDTH - 120 * f)

        # Increase Distance and Time
        self.distance += self.speed
        self.time += 1

        # Same For Y-Position
        self.position[1] += math.sin(math.radians(360 - self.angle)) * self.speed
        self.position[1] = max(self.position[1], 20)
        self.position[1] = min(self.position[1], WIDTH - 120)

        # Calculate New Center
        self.center = [int(self.position[0]) + CAR_SIZE_X / 2, int(self.position[1]) + CAR_SIZE_Y / 2]

        # Calculate Four Corners
        # Length Is Half The Side
        aus_pixel = 8
        length = 0.5 * CAR_SIZE_X + aus_pixel
        width = 0.5 * CAR_SIZE_Y + aus_pixel
        left_top = [self.center[0] + math.cos(math.radians(360 - (self.angle + 30))) * length,
                    self.center[1] + math.sin(math.radians(360 - (self.angle + 30))) * width]
        right_top = [self.center[0] + math.cos(math.radians(360 - (self.angle + 150))) * length,
                     self.center[1] + math.sin(math.radians(360 - (self.angle + 150))) * width]
        left_bottom = [self.center[0] + math.cos(math.radians(360 - (self.angle + 210))) * length,
                       self.center[1] + math.sin(math.radians(360 - (self.angle + 210))) * width]
        right_bottom = [self.center[0] + math.cos(math.radians(360 - (self.angle + 330))) * length,
                        self.center[1] + math.sin(math.radians(360 - (self.angle + 330))) * width]
        self.corners = [left_top, right_top, left_bottom, right_bottom]

        # Check Collisions And Clear Radars  检查碰撞
        self.check_collision(game_map)
        self.radars.clear()

        # From -90 To 120 With Step-Size 45 Check Radar
        if simulation.switch_2button.get_status() == 0:
            for d in range(-60, 61, 60):
                self.check_radar(d, game_map)

    def is_alive(self):
        # Basic Alive Function
        return self.alive

    def get_reward(self):
        # Calculate Reward (Maybe Change?)
        # return self.distance / 50.0
        return self.distance / (CAR_SIZE_X / 2)

    def rotate_center(self, image, angle):
        # Rotate The Rectangle
        # rectangle = image.get_rect()
        rotated_image = pygame.transform.rotate(image, angle)
        # rotated_rectangle = rectangle.copy()
        # rotated_rectangle.center = rotated_image.get_rect().center
        # rotated_image = rotated_image.subsurface(rotated_rectangle).copy()
        return rotated_image
