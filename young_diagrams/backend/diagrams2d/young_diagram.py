import random
from typing import Set, Tuple, List, Dict, Optional, Union


class Diagram2D:
    """
    Класс, представляющий 2D диаграмму Юнга с возможностями симуляции роста.
    """
    def __init__(self, initial_cells: Optional[Set[Tuple[int, int]]] = None):
        """
        Инициализация 2D диаграммы Юнга.
        
        Параметры:
        -----------
        initial_cells : Set[Tuple[int, int]], optional
            Начальный набор ячеек. Если None, начинается с ячейки (0, 0).
        """
        self.cells: Set[Tuple[int, int]] = initial_cells if initial_cells else {(0, 0)}
        
    def get_addable_cells(self) -> Set[Tuple[int, int]]:
        """
        Находит все ячейки, которые можно добавить к диаграмме согласно правилам диаграммы Юнга.
        Ячейка может быть добавлена, если у неё есть соседи слева и снизу.
        
        Возвращает:
        --------
        Set[Tuple[int, int]]
            Набор координат (x, y), которые можно добавить к диаграмме.
        """
        addable_cells = set()
        for x, y in self.cells:
            # Возможные новые ячейки справа и сверху
            neighbors = [(x + 1, y), (x, y + 1)]
            for nx, ny in neighbors:
                # Если соседняя ячейка еще не в диаграмме
                if (nx, ny) not in self.cells:
                    # Проверяем, есть ли у неё поддержка снизу и слева
                    has_support_below = ny == 0 or (nx, ny - 1) in self.cells
                    has_left_neighbor = nx == 0 or (nx - 1, ny) in self.cells
                    if has_support_below and has_left_neighbor:
                        addable_cells.add((nx, ny))
        return addable_cells
    
    def calculate_weight(self, cell: Tuple[int, int], alpha: float = 1.0) -> float:
        """
        Вычисляет вес S(c) для ячейки на основе её прямоугольной площади и параметра альфа.
        S(c) = (x + 1 + y + 1) ** alpha = (x + y + 2) ** alpha
        
        Параметры:
        -----------
        cell : Tuple[int, int]
            Координаты ячейки (x, y).
        alpha : float, default=1.0
            Степенной параметр для управления поведением роста.
            
        Возвращает:
        --------
        float
            Вес ячейки.
        """
        x, y = cell
        total = (x + 1) + (y + 1)  # Площадь прямоугольника
        return total ** alpha
    
    def add_cell(self, cell: Tuple[int, int]) -> None:
        """
        Добавляет новую ячейку к диаграмме.
        
        Параметры:
        -----------
        cell : Tuple[int, int]
            Координаты ячейки для добавления.
        """
        self.cells.add(cell)
        
    def simulate(self, n_steps: int = 1000, alpha: float = 1.0, 
                 callback: Optional[callable] = None) -> None:
        """
        Симулирует рост диаграммы в течение n_steps итераций.
        
        Параметры:
        -----------
        n_steps : int, default=1000
            Количество шагов для симуляции.
        alpha : float, default=1.0
            Параметр, влияющий на поведение роста.
        callback : callable, optional
            Функция, которая вызывается после каждого шага с текущим состоянием.
        """
        for step in range(n_steps):
            # Получаем все ячейки, которые можно добавить
            addable_cells = self.get_addable_cells()
            if not addable_cells:  # Если ячеек для добавления нет, останавливаем симуляцию
                break
                
            # Вычисляем веса для каждой добавляемой ячейки
            weights = []
            cells_list = list(addable_cells)
            
            # Вычисляем S(c) для каждой добавляемой ячейки
            for cell in cells_list:
                weights.append(self.calculate_weight(cell, alpha))
                
            # Вычисляем вероятности для каждой ячейки
            total_weight = sum(weights)
            probabilities = [w / total_weight for w in weights]
            
            # Случайно выбираем ячейку для добавления на основе вероятностей
            cell = random.choices(cells_list, weights=probabilities, k=1)[0]
            self.add_cell(cell)
            
            # Вызываем callback, если он предоставлен
            if callback and step % 10 == 0:  # Вызываем callback чаще для визуализации
                callback(self, step)
                
    def size(self) -> int:
        """
        Получает количество ячеек в диаграмме.
        
        Возвращает:
        --------
        int
            Количество ячеек в диаграмме.
        """
        return len(self.cells) 