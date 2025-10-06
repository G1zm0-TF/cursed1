import pygame
import sys
import random
from typing import List
from game_objects import Paddle, Ball, Brick, PowerUp, Particle

# Константы
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)

class Game:
    """Основной класс игры"""
    
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Арканоид")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        self.reset_game()
    
    def reset_game(self) -> None:
        """Сброс состояния игры"""
        self.paddle = Paddle(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - 50)
        self.ball = Ball(self.paddle.rect.centerx, self.paddle.rect.top - 10)
        self.ball.sticky = True
        
        self.bricks: List[Brick] = []
        self.power_ups: List[PowerUp] = []
        self.particles: List[Particle] = []
        
        self.level = 1
        self.game_state = "playing"  # "playing", "game_over", "level_complete"
        self.create_level()
    
    def create_level(self) -> None:
        """Создание уровня с кирпичами"""
        self.bricks.clear()
        
        brick_colors = [
            (RED, 1), (ORANGE, 1), (YELLOW, 1), 
            (GREEN, 2), (BLUE, 2), (PURPLE, 3)
        ]
        
        for row in range(6):
            color, health = brick_colors[row]
            for col in range(10):
                brick_x = col * 80 + 15
                brick_y = row * 40 + 50
                self.bricks.append(Brick(brick_x, brick_y, color, health + self.level - 1))
    
    def spawn_particles(self, x: int, y: int, color: tuple, count: int = 10) -> None:
        """Создание частиц эффектов"""
        for _ in range(count):
            self.particles.append(Particle(x, y, color))
    
    def handle_events(self) -> None:
        """Обработка событий"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and self.ball.sticky:
                    self.ball.launch()
                elif event.key == pygame.K_r and self.game_state != "playing":
                    self.reset_game()
            
            if event.type == pygame.MOUSEBUTTONDOWN and self.ball.sticky:
                self.ball.launch()
    
    def update(self) -> None:
        """Обновление состояния игры"""
        if self.game_state != "playing":
            return
        
        # Управление ракеткой
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.paddle.move(-1)
        if keys[pygame.K_RIGHT]:
            self.paddle.move(1)
        
        # Если мяч прилип, двигаем его вместе с ракеткой
        if self.ball.sticky:
            self.ball.reset(self.paddle)
        
        # Обновление мяча
        self.ball.move()
        
        # Проверка столкновения мяча с ракеткой
        self.ball.check_collision(self.paddle)
        
        # Проверка столкновения мяча с кирпичами
        for brick in self.bricks[:]:
            if self.ball.active and self.ball.rect.colliderect(brick.rect):
                destroyed, power_up_type = brick.hit()
                
                if destroyed:
                    self.bricks.remove(brick)
                    self.paddle.score += brick.max_health * 10
                    
                    # Создание эффекта разрушения
                    self.spawn_particles(brick.rect.centerx, brick.rect.centery, brick.color, 15)
                    
                    # Создание бонуса
                    if power_up_type:
                        self.power_ups.append(
                            PowerUp(brick.rect.centerx - 15, brick.rect.centery, power_up_type)
                        )
                
                # Отскок мяча
                self.ball.speed_y *= -1
                break
        
        # Обновление бонусов
        for power_up in self.power_ups[:]:
            power_up.move()
            
            if not power_up.active:
                self.power_ups.remove(power_up)
            elif power_up.rect.colliderect(self.paddle.rect):
                power_up.apply(self.paddle, self.ball)
                self.power_ups.remove(power_up)
                
                # Эффект подбора бонуса
                self.spawn_particles(power_up.rect.centerx, power_up.rect.centery, 
                                   power_up.colors[power_up.type], 8)
        
        # Обновление частиц
        for particle in self.particles[:]:
            if not particle.update():
                self.particles.remove(particle)
        
        # Проверка условий завершения уровня
        if not self.bricks:
            self.level += 1
            self.ball.reset(self.paddle)
            self.create_level()
        
        # Проверка потери мяча
        if not self.ball.active:
            self.paddle.lives -= 1
            if self.paddle.lives <= 0:
                self.game_state = "game_over"
            else:
                self.ball.reset(self.paddle)
    
    def draw(self) -> None:
        """Отрисовка игры"""
        self.screen.fill(BLACK)
        
        # Отрисовка игровых объектов
        self.paddle.draw(self.screen)
        self.ball.draw(self.screen)
        
        for brick in self.bricks:
            brick.draw(self.screen)
        
        for power_up in self.power_ups:
            power_up.draw(self.screen)
        
        for particle in self.particles:
            particle.draw(self.screen)
        
        # Отрисовка интерфейса
        score_text = self.font.render(f"Счет: {self.paddle.score}", True, WHITE)
        lives_text = self.font.render(f"Жизни: {self.paddle.lives}", True, WHITE)
        level_text = self.font.render(f"Уровень: {self.level}", True, WHITE)
        
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(lives_text, (SCREEN_WIDTH - 150, 10))
        self.screen.blit(level_text, (SCREEN_WIDTH // 2 - 60, 10))
        
        # Сообщения
        if self.ball.sticky:
            message = self.small_font.render("Нажмите ПРОБЕЛ или ЛКМ для запуска мяча", True, YELLOW)
            self.screen.blit(message, (SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT - 30))
        
        if self.game_state == "game_over":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            
            game_over_text = self.font.render("ИГРА ОКОНЧЕНА", True, RED)
            score_text = self.font.render(f"Финальный счет: {self.paddle.score}", True, WHITE)
            restart_text = self.small_font.render("Нажмите R для перезапуска", True, YELLOW)
            
            self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50))
            self.screen.blit(score_text, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2))
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 + 50))
        
        pygame.display.flip()
    
    def run(self) -> None:
        """Главный игровой цикл"""
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)