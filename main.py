import random
import matplotlib.pyplot as plt

class Diagram:
    """
    Class to represent the diagram and perform operations on it.
    """
    def __init__(self):
        # Initialize the diagram with the starting cell at (0, 0)
        self.cells = set()
        self.cells.add((0, 0))
        
    def get_addable_cells(self):
        """
        Find all cells that can be added to the diagram.
        A cell (x, y) can be added if it is adjacent to the existing diagram,
        meaning either (x - 1, y) or (x, y - 1) is in the diagram.
        """
        addable_cells = set()
        for x, y in self.cells:
            # Potential new cells to the right and above the current cell
            neighbors = [(x + 1, y), (x, y + 1)]
            for nx, ny in neighbors:
                # If the neighbor is not already in the diagram
                if (nx, ny) not in self.cells:
                    # Check if it can be added based on the existing diagram
                    if ((nx - 1, ny) in self.cells) or ((nx, ny - 1) in self.cells):
                        addable_cells.add((nx, ny))
        return addable_cells
    
    def get_S(self, c, alpha=1):
        """
        Compute S(c) = (area of rectangle defined by (0,0) and c) raised to the power alpha.
        """
        x, y = c
        area = (x + 1) * (y + 1)
        return area ** alpha
    
    def add_cell(self, c):
        """
        Add a new cell to the diagram.
        """
        self.cells.add(c)
        
    def simulate(self, n_steps=1000, alpha=1):
        """
        Simulate the growth of the diagram over n_steps iterations.
        """
        for step in range(n_steps):
            # Get all addable cells
            addable_cells = self.get_addable_cells()
            S_values = []
            cells_list = list(addable_cells)
            # Compute S(c) for each addable cell
            for c in cells_list:
                S_values.append(self.get_S(c, alpha))
            # Compute probabilities for each cell
            total_S = sum(S_values)
            probabilities = [S / total_S for S in S_values]
            # Randomly select a cell to add based on probabilities
            c = random.choices(cells_list, weights=probabilities, k=1)[0]
            self.add_cell(c)
            # Optionally, print progress every 100 steps
            if (step + 1) % 100 == 0:
                print(f'Step {step + 1}: Diagram size {len(self.cells)}')
                
    def visualize(self, filename=None):
        """
        Visualize the diagram using matplotlib.
        """
        x_coords = [x for x, y in self.cells]
        y_coords = [y for x, y in self.cells]
        plt.scatter(x_coords, y_coords)
        plt.gca().set_aspect('equal', adjustable='box')
        plt.xlabel('x')
        plt.ylabel('y')
        plt.title('Diagram after {} steps'.format(len(self.cells) - 1))
        if filename:
            plt.savefig(filename)
        plt.show()
        
    def save_cells(self, filename):
        """
        Save the list of cells to a file.
        """
        with open(filename, 'w') as f:
            for x, y in sorted(self.cells):
                f.write(f'{x},{y}\n')

def main():
    alpha = 1        
    n_steps = 1000  
    diagram = Diagram()
    diagram.simulate(n_steps=n_steps, alpha=alpha)
    diagram.visualize(filename='diagram.png')
    diagram.save_cells('diagram_cells.txt')

if __name__ == '__main__':
    main()
