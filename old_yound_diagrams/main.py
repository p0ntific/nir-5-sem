import random
import matplotlib.pyplot as plt
from collections import defaultdict
import numpy as np
from scipy.interpolate import griddata

class DiagramSimulator:
    """
    Класс для проведения симуляции и накопления результатов.
    """
    def __init__(self):
        self.total_cell_counts = defaultdict(int)  # Словарь для подсчета количества появления каждой клетки

    def simulate(self, n_steps=1000, alpha=1, runs=10):
        """
        Проводит симуляцию роста диаграммы указанное количество раз (runs).
        """
        for run in range(1, runs + 1):
            diagram = Diagram()
            diagram.simulate(n_steps=n_steps, alpha=alpha)
            # Увеличиваем счетчик для каждой клетки, которая появилась в текущей симуляции
            for cell in diagram.cells:
                self.total_cell_counts[cell] += 1
            print(f'Симуляция {run} завершена. Размер диаграммы: {len(diagram.cells)} клеток.')
    
    def visualize(self, filename=None):
        """
        Визуализирует накопленные результаты.
        """
        # Подготовка данных для визуализации
        x_coords = []
        y_coords = []
        frequencies = []

        max_count = max(self.total_cell_counts.values())

        for (x, y), count in self.total_cell_counts.items():
            x_coords.append(x*10)
            y_coords.append(y*10)
            frequencies.append(count)

        # Нормализация частот для корректного отображения
        frequencies_normalized = [count / max_count for count in frequencies]

        # Инвертирование нормализованных частот, чтобы цвета шли от темно-красного к светло-красному
        frequencies_inverted = [1 - f for f in frequencies_normalized]

        plt.figure(figsize=(10, 10))  # Изменяем цвет фона окна
        # Используем цветовую карту 'Reds_r' для диапазона от темно-красного до светло-красного
        scatter = plt.scatter(x_coords, y_coords, c=frequencies_inverted, cmap='Reds_r', s=1, marker='s')
        plt.colorbar(scatter, label='Частота появления клетки')
        plt.gca()
        plt.gca().set_aspect('equal', adjustable='box')
        plt.xlabel('x')
        plt.ylabel('y')
        plt.title('Накопленная диаграмма после 10 запусков')
        plt.grid(True)
        if filename:
            plt.savefig(filename)
        plt.show()
    
    def save_cells(self, filename):
        """
        Сохраняет накопленные результаты в файл.
        """
        with open(filename, 'w') as f:
            for (x, y), count in sorted(self.total_cell_counts.items()):
                f.write(f'{x},{y},{count}\n')

    def compute_limit_shape(self, scaling_factor=None):
        """
        Вычисляет предельную форму на основе накопленных данных.
        
        Parameters:
        -----------
        scaling_factor : float
            Коэффициент масштабирования. Если None, использует sqrt(n_steps)
        """
        if not self.total_cell_counts:
            raise ValueError("Нет данных для вычисления предельной формы")
        
        # Определяем масштабирующий фактор
        if scaling_factor is None:
            n = max(x + y for x, y in self.total_cell_counts.keys())
            scaling_factor = np.sqrt(n)
        
        # Масштабируем координаты и нормализуем частоты
        scaled_points = []
        frequencies = []
        max_freq = max(self.total_cell_counts.values())
        
        for (x, y), count in self.total_cell_counts.items():
            scaled_points.append([x/scaling_factor, y/scaling_factor])
            frequencies.append(count/max_freq)
        
        scaled_points = np.array(scaled_points)
        
        # Создаем регулярную сетку для интерполяции
        x_max = max(p[0] for p in scaled_points)
        y_max = max(p[1] for p in scaled_points)
        grid_x, grid_y = np.mgrid[0:x_max:100j, 0:y_max:100j]
        
        # Интерполируем данные
        grid_z = griddata(scaled_points, frequencies, (grid_x, grid_y), method='cubic')
        
        return grid_x, grid_y, grid_z

    def limit_shape_visualize(self, filename,  levels=10):
        """
        Визуализирует предельную форму с помощью контурного графика.
        
        Parameters:
        -----------
        levels : int
            Количество уровней контура
        """
        grid_x, grid_y, grid_z = self.compute_limit_shape()
        
        plt.figure(figsize=(10, 10))
        # Строим контурный график
        contour = plt.contour(grid_x, grid_y, grid_z, levels=levels)
        plt.clabel(contour, inline=True, fontsize=8)
        
        # Добавляем тепловую карту
        plt.imshow(grid_z.T, extent=[0, grid_x.max(), 0, grid_y.max()], 
                  origin='lower', cmap='viridis', alpha=0.5)
        
        plt.colorbar(label='Normalized frequency')
        plt.xlabel('x/√n')
        plt.ylabel('y/√n')
        plt.title('Limit Shape')
        plt.axis('equal')
        plt.grid(True)
        if filename:
            plt.savefig(filename)
        plt.show()
        return

class Diagram:
    """
    Класс для представления диаграммы и операций на ней.
    """
    def __init__(self):
        # Инициализируем диаграмму с начальной клеткой (0, 0)
        self.cells = set()
        self.cells.add((0, 0))
        
    def get_addable_cells(self):
        """
        Находит все клетки, которые можно добавить в диаграмму.
        """
        addable_cells = set()
        for x, y in self.cells:
            # Возможные новые клетки справа и сверху от текущей клетки
            neighbors = [(x + 1, y), (x, y + 1)]
            for nx, ny in neighbors:
                # Если соседняя клетка ещё не в диаграмме
                if (nx, ny) not in self.cells:
                    # Проверяем, можно ли добавить клетку на основе условий
                    has_support_below = ny == 0 or (nx, ny - 1) in self.cells
                    has_left_neighbor = nx == 0 or (nx - 1, ny) in self.cells
                    if has_support_below and has_left_neighbor:
                        addable_cells.add((nx, ny))
        return addable_cells
    
    def get_S(self, c, alpha=1):
        """
        Вычисляет S(c) для балансирования роста по направлениям x и y.
        S(c) = (x + 1 + y + 1) ** alpha
        """
        x, y = c
        total = (x + 1) + (y + 1)
        return total ** alpha
    
    def add_cell(self, c):
        """
        Добавляет новую клетку в диаграмму.
        """
        self.cells.add(c)
        
    def simulate(self, n_steps=1000, alpha=1):
        """
        Симулирует рост диаграммы за n_steps итераций.
        """
        for step in range(n_steps):
            # Получаем все добавляемые клетки
            addable_cells = self.get_addable_cells()
            S_values = []
            cells_list = list(addable_cells)
            # Вычисляем S(c) для каждой добавляемой клетки
            for c in cells_list:
                S_values.append(self.get_S(c, alpha))
            # Вычисляем вероятности для каждой клетки
            total_S = sum(S_values)
            probabilities = [S / total_S for S in S_values]
            # Случайно выбираем клетку для добавления на основе вероятностей
            c = random.choices(cells_list, weights=probabilities, k=1)[0]
            self.add_cell(c)
            # Можно опционально выводить прогресс
            # if (step + 1) % 100 == 0:
            #     print(f'Шаг {step + 1}: Размер диаграммы {len(self.cells)}')


def main():
    alpha = 1.1
    n_steps = 1000
    runs = 10
    
    simulator = DiagramSimulator()
    simulator.simulate(n_steps=n_steps, alpha=alpha, runs=runs)
    
    # Визуализируем обычную диаграмму
    simulator.visualize(filename=f'accumulated_diagram_alpha_{alpha}.png')
    
    # Визуализируем предельную форму
    simulator.limit_shape_visualize(filename=f'limit_shape_alpha_{alpha}.png')
    
    simulator.save_cells(f'accumulated_diagram_cells_alpha_{alpha}.txt')

if __name__ == '__main__':
    main()