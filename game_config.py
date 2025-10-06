import random
from typing import Dict, Tuple, List

class GameConfig:
    """Класс для управления настройками игры"""
    
    # Уровни сложности
    DIFFICULTY_LEVELS = {
        "easy": {
            "ball_speed": 5,
            "paddle_speed": 7,
            "power_up_chance": 0.3,
            "initial_lives": 5
        },
        "normal": {
            "ball_speed": 6,
            "paddle_speed": 8,
            "power_up_chance": 0.2,
            "initial_lives": 3
        },
        "hard": {
            "ball_speed": 7,
            "paddle_speed": 9,
            "power_up_chance": 0.1,
            "initial_lives": 2
        },
        "expert": {
            "ball_speed": 8,
            "paddle_speed": 10,
            "power_up_chance": 0.05,
            "initial_lives": 1
        }
    }
    
    # Скорости мяча для разных уровней игры
    BALL_SPEEDS = {
        "slow": 4,
        "medium": 6,
        "fast": 8,
        "very_fast": 10
    }
    
    @staticmethod
    def get_difficulty_settings(difficulty: str) -> Dict:
        """Получить настройки для выбранного уровня сложности"""
        return GameConfig.DIFFICULTY_LEVELS.get(difficulty, GameConfig.DIFFICULTY_LEVELS["normal"])
    
    @staticmethod
    def get_available_difficulties() -> List[str]:
        """Получить список доступных уровней сложности"""
        return list(GameConfig.DIFFICULTY_LEVELS.keys())
    
    @staticmethod
    def get_available_ball_speeds() -> List[str]:
        """Получить список доступных скоростей мяча"""
        return list(GameConfig.BALL_SPEEDS.keys())

class SpeedController:
    """Класс для управления скоростью мяча"""
    
    def __init__(self, base_speed: int = 6):
        self.base_speed = base_speed
        self.current_speed_multiplier = 1.0
        self.max_speed = 12
        self.min_speed = 3
        
    def set_ball_speed(self, ball, speed_level: str) -> None:
        """Установить скорость мяча по уровню"""
        speed = GameConfig.BALL_SPEEDS.get(speed_level, self.base_speed)
        self._apply_speed_to_ball(ball, speed)
    
    def set_difficulty(self, ball, difficulty: str) -> None:
        """Установить скорость на основе уровня сложности"""
        settings = GameConfig.get_difficulty_settings(difficulty)
        speed = settings["ball_speed"]
        self._apply_speed_to_ball(ball, speed)
    
    def _apply_speed_to_ball(self, ball, speed: int) -> None:
        """Применить скорость к мячу"""
        # Сохраняем направление
        direction_x = 1 if ball.speed_x >= 0 else -1
        direction_y = 1 if ball.speed_y >= 0 else -1
        
        # Устанавливаем новую скорость с ограничениями
        new_speed = max(self.min_speed, min(speed, self.max_speed))
        
        # Обновляем скорость мяча
        current_speed = (abs(ball.speed_x) + abs(ball.speed_y)) / 2
        if current_speed > 0:
            ratio_x = abs(ball.speed_x) / current_speed
            ratio_y = abs(ball.speed_y) / current_speed
            
            ball.speed_x = direction_x * new_speed * ratio_x
            ball.speed_y = direction_y * new_speed * ratio_y
        else:
            ball.speed_x = direction_x * new_speed * 0.7
            ball.speed_y = direction_y * new_speed * 0.7
    
    def increase_speed(self, ball, multiplier: float = 1.1) -> None:
        """Увеличить скорость мяча"""
        self.current_speed_multiplier *= multiplier
        self._apply_relative_speed(ball)
    
    def decrease_speed(self, ball, multiplier: float = 0.9) -> None:
        """Уменьшить скорость мяча"""
        self.current_speed_multiplier *= multiplier
        self._apply_relative_speed(ball)
    
    def _apply_relative_speed(self, ball) -> None:
        """Применить относительное изменение скорости"""
        # Ограничиваем множитель
        self.current_speed_multiplier = max(0.5, min(2.0, self.current_speed_multiplier))
        
        # Вычисляем базовую скорость
        current_total_speed = (abs(ball.speed_x) + abs(ball.speed_y)) / 2
        base_speed = current_total_speed / self.current_speed_multiplier
        
        # Новая скорость с учетом множителя
        new_speed = base_speed * self.current_speed_multiplier
        new_speed = max(self.min_speed, min(new_speed, self.max_speed))
        
        # Сохраняем направление и пропорции
        direction_x = 1 if ball.speed_x >= 0 else -1
        direction_y = 1 if ball.speed_y >= 0 else -1
        
        current_speed = (abs(ball.speed_x) + abs(ball.speed_y)) / 2
        if current_speed > 0:
            ratio_x = abs(ball.speed_x) / current_speed
            ratio_y = abs(ball.speed_y) / current_speed
            
            ball.speed_x = direction_x * new_speed * ratio_x
            ball.speed_y = direction_y * new_speed * ratio_y
    
    def reset_speed(self, ball) -> None:
        """Сбросить скорость к базовой"""
        self.current_speed_multiplier = 1.0
        self._apply_speed_to_ball(ball, self.base_speed)
    
    def get_current_speed_info(self, ball) -> Dict[str, float]:
        """Получить информацию о текущей скорости"""
        horizontal_speed = abs(ball.speed_x)
        vertical_speed = abs(ball.speed_y)
        total_speed = (horizontal_speed + vertical_speed) / 2
        
        return {
            "horizontal": horizontal_speed,
            "vertical": vertical_speed,
            "total": total_speed,
            "multiplier": self.current_speed_multiplier
        }
    
    def calculate_level_speed_increase(self, ball, level: int) -> None:
        """Увеличить скорость в зависимости от уровня"""
        increase_per_level = 0.1  # 10% увеличение за уровень
        multiplier = 1.0 + (level - 1) * increase_per_level
        self.current_speed_multiplier = multiplier
        self._apply_relative_speed(ball)

class PowerUpEffects:
    """Класс для эффектов бонусов, влияющих на скорость"""
    
    @staticmethod
    def apply_speed_boost(ball, speed_controller: SpeedController, duration: int = 300) -> Dict:
        """Применить временное ускорение мяча"""
        speed_controller.increase_speed(ball, 1.3)
        return {"type": "speed_boost", "duration": duration, "active": True}
    
    @staticmethod
    def apply_slow_down(ball, speed_controller: SpeedController, duration: int = 300) -> Dict:
        """Применить временное замедление мяча"""
        speed_controller.decrease_speed(ball, 0.7)
        return {"type": "slow_down", "duration": duration, "active": True}