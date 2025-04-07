import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict
from typing import Dict, Tuple, List, Set, Optional, Union, Any
import os
import sys

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.utils import save_cells_to_file, compute_limit_shape
from diagrams2d.young_diagram import Diagram2D


class DiagramSimulator2D:
    """
    Class for simulating 2D Young diagrams and accumulating results.
    """
    def __init__(self):
        """
        Initialize the simulator with empty cell counts.
        """
        self.total_cell_counts = defaultdict(int)  # Dictionary for counting occurrences of each cell
        
    def simulate(self, n_steps: int = 1000, alpha: float = 1.0, runs: int = 10, 
                 initial_cells: Optional[Set[Tuple[int, int]]] = None,
                 callback: Optional[callable] = None) -> None:
        """
        Conduct simulation of diagram growth for the specified number of runs.
        
        Parameters:
        -----------
        n_steps : int, default=1000
            Number of steps for each simulation.
        alpha : float, default=1.0
            Power parameter to control growth behavior.
        runs : int, default=10
            Number of simulations to run.
        initial_cells : Set[Tuple[int, int]], optional
            Initial set of cells for the simulation.
        callback : callable, optional
            Function to call after each step with the current state.
        """
        # Reset counters for new simulation
        self.total_cell_counts = defaultdict(int)
        
        for run in range(1, runs + 1):
            # Create a new diagram for each run
            diagram = Diagram2D(initial_cells)
            
            # Define callback function to track growth in real-time if provided
            def growth_callback(diagram, step):
                if callback:
                    # Store current state for external callback
                    temp_counts = self.total_cell_counts.copy()
                    for cell in diagram.cells:
                        temp_counts[cell] += 1
                    callback(temp_counts, step, run)
            
            # Run the simulation
            diagram.simulate(n_steps=n_steps, alpha=alpha, callback=growth_callback)
            
            # Increment counter for each cell that appeared in this simulation
            for cell in diagram.cells:
                self.total_cell_counts[cell] += 1
                
            print(f'Simulation {run} completed. Diagram size: {len(diagram.cells)} cells.')
    
    def visualize(self, filename: Optional[str] = None, 
                  cell_size: int = 10, grid: bool = True) -> None:
        """
        Visualize accumulated simulation results.
        
        Parameters:
        -----------
        filename : str, optional
            If provided, saves the visualization to this file.
        cell_size : int, default=10
            Size of each cell in the visualization.
        grid : bool, default=True
            Whether to display a grid.
        """
        if not self.total_cell_counts:
            print("No data to visualize. Run simulations first.")
            return
            
        # Prepare data for visualization
        x_coords = []
        y_coords = []
        frequencies = []
        
        max_count = max(self.total_cell_counts.values())
        
        for (x, y), count in self.total_cell_counts.items():
            x_coords.append(x * cell_size)
            y_coords.append(y * cell_size)
            frequencies.append(count)
        
        # Normalize frequencies for proper display
        frequencies_normalized = [count / max_count for count in frequencies]
        
        # Invert normalized frequencies for color mapping (dark red for high frequency)
        frequencies_inverted = [1 - f for f in frequencies_normalized]
        
        plt.figure(figsize=(10, 10))
        # Use 'Reds_r' colormap for dark red to light red range
        scatter = plt.scatter(x_coords, y_coords, c=frequencies_inverted, 
                             cmap='Reds_r', s=cell_size**2, marker='s')
        plt.colorbar(scatter, label='Cell frequency')
        
        # Set equal aspect ratio
        plt.gca().set_aspect('equal', adjustable='box')
        
        plt.xlabel('x')
        plt.ylabel('y')
        plt.title('Accumulated Young Diagram (2D)')
        
        if grid:
            plt.grid(True)
            
        if filename:
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            
        plt.show()
        
        # Return the figure for web API usage
        return plt.gcf()
    
    def save_cells(self, filename: str) -> None:
        """
        Save accumulated results to a file.
        
        Parameters:
        -----------
        filename : str
            Output filename.
        """
        save_cells_to_file(self.total_cell_counts, filename)

    def limit_shape_visualize(self, filename: Optional[str] = None, 
                             levels: int = 10) -> None:
        """
        Visualize the limit shape using a contour plot.
        
        Parameters:
        -----------
        filename : str, optional
            If provided, saves the visualization to this file.
        levels : int, default=10
            Number of contour levels.
        """
        if not self.total_cell_counts:
            print("No data to visualize. Run simulations first.")
            return
            
        # Compute the limit shape
        grid_x, grid_y, grid_z = compute_limit_shape(
            self.total_cell_counts, dimensions=2)
        
        plt.figure(figsize=(10, 10))
        
        # Plot contour graph
        contour = plt.contour(grid_x, grid_y, grid_z, levels=levels)
        plt.clabel(contour, inline=True, fontsize=8)
        
        # Add heatmap
        plt.imshow(grid_z.T, extent=[0, grid_x.max(), 0, grid_y.max()],
                  origin='lower', cmap='viridis', alpha=0.5)
        
        plt.colorbar(label='Normalized frequency')
        plt.xlabel('x/√n')
        plt.ylabel('y/√n')
        plt.title('2D Young Diagram Limit Shape')
        plt.axis('equal')
        plt.grid(True)
        
        if filename:
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            
        plt.show()
        
        # Return the figure for web API usage
        return plt.gcf()
        
    def get_json_data(self):
        """
        Get the data in a JSON-serializable format for the web API.
        
        Returns:
        --------
        dict
            Dictionary containing the cell data for visualization.
        """
        if not self.total_cell_counts:
            return {"error": "No data available. Run simulations first."}
            
        # Convert to a format suitable for JSON serialization
        cells_data = []
        max_count = max(self.total_cell_counts.values())
        
        for (x, y), count in self.total_cell_counts.items():
            normalized_count = count / max_count
            cells_data.append({
                "x": x,
                "y": y,
                "count": count,
                "normalized_count": normalized_count
            })
            
        return {
            "cells": cells_data,
            "max_count": max_count,
            "dimensions": {
                "max_x": max(x for x, _ in self.total_cell_counts.keys()) + 1,
                "max_y": max(y for _, y in self.total_cell_counts.keys()) + 1
            }
        } 