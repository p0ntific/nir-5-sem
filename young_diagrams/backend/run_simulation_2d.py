#!/usr/bin/env python3
"""
Скрипт для запуска 2D симуляций диаграмм Юнга.
"""
import os
import argparse
from diagrams2d import DiagramSimulator2D


def main():
    """
    Основная функция для запуска 2D симуляций диаграмм Юнга.
    """
    parser = argparse.ArgumentParser(description='Запуск 2D симуляций диаграмм Юнга')
    parser.add_argument('--alpha', type=float, default=1.0,
                      help='Степенной параметр для управления поведением роста (по умолчанию: 1.0)')
    parser.add_argument('--steps', type=int, default=1000,
                      help='Количество шагов для каждой симуляции (по умолчанию: 1000)')
    parser.add_argument('--runs', type=int, default=10,
                      help='Количество запусков симуляции (по умолчанию: 10)')
    parser.add_argument('--output-dir', type=str, default='results_2d',
                      help='Директория для сохранения выходных файлов (по умолчанию: results_2d)')
    
    args = parser.parse_args()
    
    # Создаем выходную директорию, если она не существует
    os.makedirs(args.output_dir, exist_ok=True)
    
    print(f"Запуск 2D симуляций диаграмм Юнга с alpha={args.alpha}")
    print(f"Шагов на симуляцию: {args.steps}")
    print(f"Количество запусков: {args.runs}")
    
    # Создаем и запускаем симулятор
    simulator = DiagramSimulator2D()
    simulator.simulate(n_steps=args.steps, alpha=args.alpha, runs=args.runs)
    
    # Базовое имя файла для выходных данных
    base_filename = f"{args.output_dir}/young_diagram_2d_alpha_{args.alpha}"
    
    # Сохраняем результаты
    print(f"Сохранение результатов в {args.output_dir}/...")
    
    # Сохраняем количество ячеек в файл
    simulator.save_cells(f"{base_filename}_cells.txt")
    
    # Генерируем визуализации
    print("Генерация визуализаций...")
    
    # Накопленная диаграмма
    simulator.visualize(filename=f"{base_filename}_heatmap.png")
    
    # Предельная форма
    simulator.limit_shape_visualize(filename=f"{base_filename}_limit_shape.png")
    
    print("Готово!")
    

if __name__ == "__main__":
    main() 