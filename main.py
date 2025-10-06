import pygame
from game import Game

def main():
    """Основная функция запуска игры"""
    # Инициализация Pygame
    pygame.init()
    
    # Создание и запуск игры
    game = Game()
    game.run()

if __name__ == "__main__":
    main()