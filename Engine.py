# Engine.py

import pygame
import numpy as np


class Transform3D:
    def __init__(self, position, velocity, size, angular_velocity=None):
        self.position = np.array(position, dtype=float)
        self.velocity = np.array(velocity, dtype=float)
        self.size = size
        self.rotation = np.eye(3)
        self.angular_velocity = angular_velocity if angular_velocity is not None else np.random.uniform(
            -0.5, 0.5, 3)

    def update(self, dt, speed_multiplier):
        self.position += self.velocity * dt * speed_multiplier
        theta = np.linalg.norm(self.angular_velocity * dt)
        if theta > 0:
            axis = self.angular_velocity / \
                np.linalg.norm(self.angular_velocity)
            K = np.array([
                [0, -axis[2], axis[1]],
                [axis[2], 0, -axis[0]],
                [-axis[1], axis[0], 0]
            ])
            R = np.eye(3) + np.sin(theta) * K + \
                (1 - np.cos(theta)) * np.dot(K, K)
            self.rotation = np.dot(R, self.rotation)

    def check_wall_collision(self, bounds):
        for i in range(3):
            if self.position[i] - self.size / 2 < bounds[i][0] or self.position[i] + self.size / 2 > bounds[i][1]:
                self.velocity[i] *= -1

    def get_corners(self):
        half_size = self.size / 2
        corners = np.array([
            [-half_size, -half_size, -half_size],
            [half_size, -half_size, -half_size],
            [half_size, half_size, -half_size],
            [-half_size, half_size, -half_size],
            [-half_size, -half_size, half_size],
            [half_size, -half_size, half_size],
            [half_size, half_size, half_size],
            [-half_size, half_size, half_size]
        ])
        return np.dot(self.rotation, corners.T).T + self.position


class Cube:
    def __init__(self, position, velocity, size, color, angular_velocity=None):
        self.transform = Transform3D(
            position, velocity, size, angular_velocity)
        self.color = color

    def update(self, dt, bounds, speed_multiplier):
        self.transform.update(dt, speed_multiplier)
        self.transform.check_wall_collision(bounds)

    def draw(self, screen, screen_width, screen_height, light_pos):
        corners = self.transform.get_corners()
        projected = []
        for corner in corners:
            scale = 700 / (corner[2] + 1000)
            x = int(screen_width / 2 + corner[0] * scale)
            y = int(screen_height / 2 - corner[1] * scale)
            projected.append((x, y))

        faces = [
            (0, 1, 2, 3),  # Front
            (4, 5, 6, 7),  # Back
            (0, 1, 5, 4),  # Bottom
            (2, 3, 7, 6),  # Top
            (0, 3, 7, 4),  # Left
            (1, 2, 6, 5),  # Right
        ]

        face_z_values = []
        for face in faces:
            z_mean = sum(corners[vertex][2] for vertex in face) / 4
            face_z_values.append((z_mean, face))

        face_z_values.sort(key=lambda x: x[0], reverse=True)

        for z_mean, face in face_z_values:
            v1 = corners[face[1]] - corners[face[0]]
            v2 = corners[face[2]] - corners[face[0]]
            normal = np.cross(v1, v2)
            normal = normal / np.linalg.norm(normal)

            light_dir = np.array(light_pos) - self.transform.position
            light_dir = light_dir / np.linalg.norm(light_dir)

            brightness = np.clip(np.dot(normal, light_dir), 0, 1)
            color = [int(c * brightness) for c in self.color]

            pygame.draw.polygon(
                screen, color, [projected[vertex] for vertex in face]
            )

            pygame.draw.polygon(
                screen, (0, 0, 0), [projected[vertex]
                                    for vertex in face], 2
            )

    def is_colliding(self, other_cube):
        min_self = self.transform.position - self.transform.size / 2
        max_self = self.transform.position + self.transform.size / 2
        min_other = other_cube.transform.position - other_cube.transform.size / 2
        max_other = other_cube.transform.position + other_cube.transform.size / 2

        return (
            min_self[0] <= max_other[0] and max_self[0] >= min_other[0] and
            min_self[1] <= max_other[1] and max_self[1] >= min_other[1] and
            min_self[2] <= max_other[2] and max_self[2] >= min_other[2]
        )

    def resolve_collision(self, other_cube):
        direction = self.transform.position - other_cube.transform.position
        distance = np.linalg.norm(direction)
        min_distance = (self.transform.size + other_cube.transform.size) / 2
        if distance < min_distance:
            overlap = min_distance - distance
            direction_normalized = direction / \
                (distance if distance != 0 else 1)
            self.transform.position += direction_normalized * (overlap / 2)
            other_cube.transform.position -= direction_normalized * \
                (overlap / 2)
            self.transform.velocity *= -1
            other_cube.transform.velocity *= -1
