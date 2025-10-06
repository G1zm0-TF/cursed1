import pygame
import random
import math
from typing import List, Tuple, Optional
from game_config import SpeedController

class Paddle:
    """Класс для ракетки игрока"""
    
    def __init__(self, x: int, y: int, speed: int = 8):
        self.rect = pygame.Rect(x, y, 100, 20)
        self.speed = speed
        self.color = (0, 255, 0)  # GREEN
        self.lives = 3
        self.score = 0
    
    def move(self, direction: int) -> None:
        """Перемещение ракетки"""
        self.rect.x += direction * self.speed
        
        # Ограничение движения в пределах экрана
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > 800:  # SCREEN_WIDTH
            self.rect.right = 800
    
    def draw(self, screen: pygame.Surface) -> None:
        """Отрисовка ракетки"""
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)  # WHITE
    
    def shrink(self) -> None:
        """Уменьшение размера ракетки"""
        if self.rect.width > 50:
            old_center = self.rect.center
            self.rect.width -= 10
            self.rect.center = old_center
    
    def grow(self) -> None:
        """Увеличение размера ракетки"""
        if self.rect.width < 150:
            old_center = self.rect.center
            self.rect.width += 10
            self.rect.center = old_center

class Ball:
    """Класс для мяча"""
    
    def __init__(self, x: int, y: int):
        self.rect = pygame.Rect(x, y, 15, 15)
        self.speed_x = 5 * random.choice([-1, 1])
        self.speed_y = -5
        self.color = (255, 255, 255)  # WHITE
        self.active = True
        self.sticky = False  # Мяч прилипает к ракетке
        self.power_ball = False  # Мяч разрушает блоки за один удар
        self.speed_controller = SpeedController()
    
    def move(self) -> None:
        """Перемещение мяча"""
        if self.active and not self.sticky:
            self.rect.x += self.speed_x
            self.rect.y += self.speed_y
            
            # Отскок от стен
            if self.rect.left <= 0 or self.rect.right >= 800:  # SCREEN_WIDTH
                self.speed_x *= -1
            if self.rect.top <= 0:
                self.speed_y *= -1
            
            # Проверка выхода за нижнюю границу
            if self.rect.top > 600:  # SCREEN_HEIGHT
                self.active = False
    
    def draw(self, screen: pygame.Surface) -> None:
        """Отрисовка мяча"""
        if self.active:
            color = (255, 255, 0) if self.power_ball else self.color  # YELLOW if power_ball
            pygame.draw.ellipse(screen, color, self.rect)
            pygame.draw.ellipse(screen, (255, 255, 255), self.rect, 2)  # WHITE
    
    def reset(self, paddle: 'Paddle') -> None:
        """Сброс мяча на ракетку"""
        self.rect.centerx = paddle.rect.centerx
        self.rect.bottom = paddle.rect.top - 5
        self.speed_x = 5 * random.choice([-1, 1])
        self.speed_y = -5
        self.active = True
        self.sticky = True
        self.power_ball = False
        self.speed_controller.reset_speed(self)
    
    def launch(self) -> None:
        """Запуск мяча с ракетки"""
        if self.sticky:
            self.sticky = False
    
    def check_collision(self, paddle: 'Paddle') -> bool:
        """Проверка столкновения с ракеткой"""
        if (self.active and not self.sticky and 
            self.rect.colliderect(paddle.rect) and self.speed_y > 0):
            
            # Расчет угла отскока в зависимости от места попадания
            relative_intersect_x = paddle.rect.centerx - self.rect.centerx
            normalized_intersect_x = relative_intersect_x / (paddle.rect.width / 2)
            bounce_angle = normalized_intersect_x * (math.pi / 3)  # Макс угол 60 градусов
            
            self.speed_y = -abs(self.speed_y)
            self.speed_x = -math.sin(bounce_angle) * 7
            
            # Ограничение скорости
            max_speed = 10
            self.speed_x = max(min(self.speed_x, max_speed), -max_speed)
            
            return True
        return False

# Остальные классы Brick, PowerUp, Particle остаются без изменений
class Brick:
    """Класс для кирпича"""
    
    def __init__(self, x: int, y: int, color: Tuple[int, int, int], health: int = 1):
        self.rect = pygame.Rect(x, y, 75, 30)
        self.color = color
        self.health = health
        self.max_health = health
        self.power_up_chance = 0.2  # 20% шанс выпадения бонуса
    
    def draw(self, screen: pygame.Surface) -> None:
        """Отрисовка кирпича"""
        if self.health > 0:
            pygame.draw.rect(screen, self.color, self.rect)
            
            # Рисуем трещины для поврежденных кирпичей
            if self.health < self.max_health:
                crack_color = (max(0, self.color[0] - 50), 
                             max(0, self.color[1] - 50), 
                             max(0, self.color[2] - 50))
                pygame.draw.line(screen, crack_color, 
                               self.rect.topleft, self.rect.bottomright, 2)
                pygame.draw.line(screen, crack_color, 
                               self.rect.topright, self.rect.bottomleft, 2)
            
            pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)  # WHITE
    
    def hit(self) -> Tuple[bool, Optional[str]]:
        """Обработка попадания по кирпичу"""
        self.health -= 1
        destroyed = self.health <= 0
        
        # Проверка на выпадение бонуса
        power_up = None
        if destroyed and random.random() < self.power_up_chance:
            power_up = random.choice(["expand", "shrink", "life", "power_ball"])
        
        return destroyed, power_up

class PowerUp:
    """Класс для бонусов"""
    
    def __init__(self, x: int, y: int, type: str):
        self.rect = pygame.Rect(x, y, 30, 30)
        self.type = type
        self.speed = 3
        self.active = True
        
        # Цвета для разных типов бонусов
        self.colors = {
            "expand": (0, 255, 0),  # GREEN
            "shrink": (255, 0, 0),  # RED
            "life": (255, 255, 0),  # YELLOW
            "power_ball": (255, 165, 0)  # ORANGE
        }
    
    def move(self) -> None:
        """Перемещение бонуса"""
        self.rect.y += self.speed
        if self.rect.top > 600:  # SCREEN_HEIGHT
            self.active = False
    
    def draw(self, screen: pygame.Surface) -> None:
        """Отрисовка бонуса"""
        if self.active:
            pygame.draw.rect(screen, self.colors[self.type], self.rect)
            pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)  # WHITE
            
            # Рисуем символ бонуса
            font = pygame.font.Font(None, 20)
            symbols = {
                "expand": "+",
                "shrink": "-",
                "life": "♥",
                "power_ball": "★"
            }
            text = font.render(symbols[self.type], True, (255, 255, 255))  # WHITE
            text_rect = text.get_rect(center=self.rect.center)
            screen.blit(text, text_rect)
    
    def apply(self, paddle: 'Paddle', ball: 'Ball') -> None:
        """Применение эффекта бонуса"""
        if self.type == "expand":
            paddle.grow()
        elif self.type == "shrink":
            paddle.shrink()
        elif self.type == "life":
            paddle.lives += 1
        elif self.type == "power_ball":
            ball.power_ball = True

class Particle:
    """Класс для частиц эффектов"""
    
    def __init__(self, x: int, y: int, color: Tuple[int, int, int]):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(2, 5)
        self.speed_x = random.uniform(-3, 3)
        self.speed_y = random.uniform(-3, 3)
        self.life = random.randint(20, 40)
    
    def update(self) -> bool:
        """Обновление состояния частицы"""
        self.x += self.speed_x
        self.y += self.speed_y
        self.life -= 1
        self.size = max(0, self.size - 0.1)
        return self.life > 0 and self.size > 0
    
    def draw(self, screen: pygame.Surface) -> None:
        """Отрисовка частицы"""
        if self.life > 0:
            alpha = min(255, self.life * 6)
            color_with_alpha = (*self.color, alpha)
            
            # Создаем поверхность с альфа-каналом
            particle_surface = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, color_with_alpha, 
                             (int(self.size), int(self.size)), int(self.size))
            screen.blit(particle_surface, (int(self.x - self.size), int(self.y - self.size)))