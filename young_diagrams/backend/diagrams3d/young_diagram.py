import random
from typing import Set, Tuple, List, Dict, Optional, Union


class Diagram3D:
    """
    Класс, представляющий 3D диаграмму Юнга с возможностями симуляции роста.
    
    3D диаграмма Юнга представляет собой коллекцию кубических ячеек с целочисленными координатами.
    Диаграмма следует правилу: если куб с координатами (x,y,z) находится в диаграмме,
    то все кубы с координатами (x',y',z'), где x' <= x, y' <= y, z' <= z, также должны быть в диаграмме.
    """
    def __init__(self, initial_cells: Optional[Set[Tuple[int, int, int]]] = None):
        """
        Инициализация 3D диаграммы Юнга.
        
        Параметры:
        -----------
        initial_cells : Set[Tuple[int, int, int]], optional
            Начальный набор ячеек. Если None, начинается с ячейки (0, 0, 0).
        """
        self.cells: Set[Tuple[int, int, int]] = initial_cells if initial_cells else {(0, 0, 0)}
        
    def get_addable_cells(self) -> Set[Tuple[int, int, int]]:
        """
        Находит все ячейки, которые можно добавить к диаграмме согласно правилам 3D диаграммы Юнга.
        Ячейка может быть добавлена, если у неё есть соседи во всех трех направлениях: слева, снизу и сзади.
        
        Возвращает:
        --------
        Set[Tuple[int, int, int]]
            Набор координат (x, y, z), которые можно добавить к диаграмме.
        """
        addable_cells = set()
        for x, y, z in self.cells:
            # Возможные новые ячейки в трех положительных направлениях
            neighbors = [(x + 1, y, z), (x, y + 1, z), (x, y, z + 1)]
            for nx, ny, nz in neighbors:
                # Если соседняя ячейка еще не в диаграмме
                if (nx, ny, nz) not in self.cells:
                    # Проверяем, есть ли у неё поддержка со всех трех сторон
                    has_support_below = ny == 0 or (nx, ny - 1, nz) in self.cells
                    has_left_neighbor = nx == 0 or (nx - 1, ny, nz) in self.cells
                    has_back_neighbor = nz == 0 or (nx, ny, nz - 1) in self.cells
                    
                    if has_support_below and has_left_neighbor and has_back_neighbor:
                        addable_cells.add((nx, ny, nz))
        return addable_cells
    
    def calculate_weight(self, cell: Tuple[int, int, int], alpha: float = 1.0) -> float:
        """
        Вычисляет вес S(c) для ячейки на основе её прямоугольного объема и параметра альфа.
        S(c) = (x + 1) * (y + 1) * (z + 1)) ** alpha
        
        В 3D мы используем объем прямоугольного параллелепипеда, образованного ячейкой и началом координат,
        в отличие от площади в 2D.
        
        Параметры:
        -----------
        cell : Tuple[int, int, int]
            Координаты ячейки (x, y, z).
        alpha : float, default=1.0
            Степенной параметр для управления поведением роста.
            
        Возвращает:
        --------
        float
            Вес ячейки.
        """
        x, y, z = cell
        # Вычисляем объем прямоугольного параллелепипеда
        volume = (x + 1) * (y + 1) * (z + 1)
        return volume ** alpha
    
    def add_cell(self, cell: Tuple[int, int, int]) -> None:
        """
        Добавляет новую ячейку к диаграмме.
        
        Параметры:
        -----------
        cell : Tuple[int, int, int]
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