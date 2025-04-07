import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from collections import defaultdict
from typing import Dict, Tuple, List, Set, Optional, Union, Any
import os
import sys
from matplotlib import cm
import matplotlib.colors as mcolors

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.utils import save_cells_to_file, compute_limit_shape
from diagrams3d.young_diagram import Diagram3D


class DiagramSimulator3D:
    """
    Class for simulating 3D Young diagrams and accumulating results.
    """
    def __init__(self):
        """
        Initialize the simulator with empty cell counts.
        """
        self.total_cell_counts = defaultdict(int)  # Dictionary for counting occurrences of each cell
        
    def simulate(self, n_steps: int = 1000, alpha: float = 1.0, runs: int = 10, 
                 initial_cells: Optional[Set[Tuple[int, int, int]]] = None, 
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
        initial_cells : Set[Tuple[int, int, int]], optional
            Initial set of cells for the simulation.
        callback : callable, optional
            Function to call after each step with the current state.
        """
        # Reset counters for new simulation
        self.total_cell_counts = defaultdict(int)
        
        for run in range(1, runs + 1):
            # Create a new diagram for each run
            diagram = Diagram3D(initial_cells)
            
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
    
    def visualize(self, filename: Optional[str] = None, alpha_cubes: float = 0.7,
                 elev: int = 20, azim: int = -30) -> None:
        """
        Visualize accumulated 3D simulation results using voxels.
        
        Parameters:
        -----------
        filename : str, optional
            If provided, saves the visualization to this file.
        alpha_cubes : float, default=0.7
            Transparency of cubes.
        elev : int, default=20
            Elevation angle for the 3D view.
        azim : int, default=-30
            Azimuth angle for the 3D view.
        """
        if not self.total_cell_counts:
            print("No data to visualize. Run simulations first.")
            return
            
        # Find the dimensions of the 3D space
        max_x = max(x for x, _, _ in self.total_cell_counts.keys()) + 1
        max_y = max(y for _, y, _ in self.total_cell_counts.keys()) + 1
        max_z = max(z for _, _, z in self.total_cell_counts.keys()) + 1
        
        # Create a boolean array for voxel occupancy
        voxels = np.zeros((max_x, max_y, max_z), dtype=bool)
        
        # Create a color array for voxels
        max_count = max(self.total_cell_counts.values())
        colors = np.zeros(voxels.shape + (4,))  # RGBA colors
        
        # Fill the voxel and color arrays
        for (x, y, z), count in self.total_cell_counts.items():
            voxels[x, y, z] = True
            
            # Normalize count and create color (heat map from blue to red)
            normalized_count = count / max_count
            colors[x, y, z] = cm.plasma(normalized_count) 
            # Last value is alpha (transparency)
            colors[x, y, z, 3] = alpha_cubes  
        
        # Create the figure
        fig = plt.figure(figsize=(10, 10))
        ax = fig.add_subplot(111, projection='3d')
        
        # Plot the voxels
        ax.voxels(voxels, facecolors=colors, edgecolor='k', linewidth=0.5)
        
        # Set axis labels
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        
        # Set the viewing angle
        ax.view_init(elev=elev, azim=azim)
        
        # Correct the aspect ratio to ensure cubes are displayed as cubes, not as stretched boxes
        # Get the maximum size in any dimension
        max_dim = max(max_x, max_y, max_z)
        
        # Set equal aspect ratio for all axes
        ax.set_box_aspect([max_x/max_dim, max_y/max_dim, max_z/max_dim])
        
        # Set equal scale for all axes
        ax.set_xlim(0, max_dim)
        ax.set_ylim(0, max_dim)
        ax.set_zlim(0, max_dim)
        
        ax.set_title('3D Young Diagram Simulation')
        
        # Save if filename provided
        if filename:
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            
        plt.show()
        
        # Return the figure for web API usage
        return fig
    
    def visualize_point_cloud(self, filename: Optional[str] = None, 
                             alpha_points: float = 0.8, size_factor: int = 100) -> None:
        """
        Visualize accumulated 3D simulation results using a point cloud with varying sizes.
        
        Parameters:
        -----------
        filename : str, optional
            If provided, saves the visualization to this file.
        alpha_points : float, default=0.8
            Transparency of points.
        size_factor : int, default=100
            Size multiplier for the points.
        """
        if not self.total_cell_counts:
            print("No data to visualize. Run simulations first.")
            return
            
        # Extract coordinates and counts
        x_coords = []
        y_coords = []
        z_coords = []
        sizes = []
        colors = []
        
        max_count = max(self.total_cell_counts.values())
        
        for (x, y, z), count in self.total_cell_counts.items():
            x_coords.append(x)
            y_coords.append(y)
            z_coords.append(z)
            
            # Size proportional to count
            normalized_count = count / max_count
            sizes.append(normalized_count * size_factor)
            colors.append(normalized_count)
        
        # Create the figure
        fig = plt.figure(figsize=(10, 10))
        ax = fig.add_subplot(111, projection='3d')
        
        # Create a scatter plot
        scatter = ax.scatter(x_coords, y_coords, z_coords, 
                           c=colors, cmap='plasma', s=sizes, alpha=alpha_points)
        
        # Add a color bar
        plt.colorbar(scatter, ax=ax, label='Normalized Frequency')
        
        # Set axis labels
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        
        # Get the maximum size in any dimension
        max_dim = max(max(x_coords), max(y_coords), max(z_coords)) + 1
        
        # Set equal aspect ratio for all axes
        ax.set_box_aspect([1, 1, 1])
        
        # Set equal limits for all axes
        ax.set_xlim(0, max_dim)
        ax.set_ylim(0, max_dim)
        ax.set_zlim(0, max_dim)
        
        ax.set_title('3D Young Diagram Point Cloud')
        
        # Save if filename provided
        if filename:
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            
        plt.show()
        
        # Return the figure for web API usage
        return fig
    
    def save_cells(self, filename: str) -> None:
        """
        Save accumulated results to a file.
        
        Parameters:
        -----------
        filename : str
            Output filename.
        """
        save_cells_to_file(self.total_cell_counts, filename)
        
    def visualize_limit_shape(self, filename: Optional[str] = None, 
                             level: float = 0.5, alpha_surface: float = 0.7) -> None:
        """
        Visualize the limit shape using isosurfaces in 3D.
        
        Parameters:
        -----------
        filename : str, optional
            If provided, saves the visualization to this file.
        level : float, default=0.5
            Isosurface level to display (between 0 and 1).
        alpha_surface : float, default=0.7
            Transparency of the surface.
        """
        if not self.total_cell_counts:
            print("No data to visualize. Run simulations first.")
            return
            
        try:
            # This function requires skimage
            from skimage import measure
        except ImportError:
            print("This visualization requires scikit-image. Please install it with:")
            print("pip install scikit-image")
            return
            
        # Compute the limit shape
        grid_x, grid_y, grid_z, grid_v = compute_limit_shape(
            self.total_cell_counts, dimensions=3)
        
        # Extract the isosurface at the specified level
        verts, faces, _, _ = measure.marching_cubes(grid_v, level=level)
        
        # Scale the vertices back to the original coordinate system
        x_size, y_size, z_size = grid_x.max(), grid_y.max(), grid_z.max()
        verts[:, 0] *= x_size / grid_v.shape[0]
        verts[:, 1] *= y_size / grid_v.shape[1] 
        verts[:, 2] *= z_size / grid_v.shape[2]
        
        # Create the figure
        fig = plt.figure(figsize=(10, 10))
        ax = fig.add_subplot(111, projection='3d')
        
        # Plot the isosurface
        mesh = ax.plot_trisurf(verts[:, 0], verts[:, 1], verts[:, 2],
                              triangles=faces, cmap='viridis', alpha=alpha_surface)
        
        # Set axis labels
        ax.set_xlabel('x/n^(1/3)')
        ax.set_ylabel('y/n^(1/3)')
        ax.set_zlabel('z/n^(1/3)')
        
        # Set equal aspect ratio
        ax.set_box_aspect([1, 1, 1])
        
        ax.set_title(f'3D Young Diagram Limit Shape (Isosurface at level {level})')
        
        # Save if filename provided
        if filename:
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            
        plt.show()
        
        # Return the figure for web API usage
        return fig
        
    def visualize_slices(self, filename: Optional[str] = None, 
                        num_slices: int = 3) -> None:
        """
        Visualize 2D slices of the 3D diagram at different z-levels.
        
        Parameters:
        -----------
        filename : str, optional
            If provided, saves the visualization to this file.
        num_slices : int, default=3
            Number of z-slices to display.
        """
        if not self.total_cell_counts:
            print("No data to visualize. Run simulations first.")
            return
            
        # Find the range of z values
        z_values = [z for _, _, z in self.total_cell_counts.keys()]
        min_z, max_z = min(z_values), max(z_values)
        
        # Determine slice positions
        if num_slices == 1:
            slice_positions = [min_z]
        else:
            slice_positions = np.linspace(min_z, max_z, num_slices, dtype=int)
        
        # Create figure with subplots
        fig, axes = plt.subplots(1, len(slice_positions), figsize=(15, 5))
        if num_slices == 1:
            axes = [axes]
            
        # Set a title for the entire figure
        fig.suptitle('3D Young Diagram Z-Slices', fontsize=16)
        
        # Maximum count for normalization
        max_count = max(self.total_cell_counts.values())
        
        # Process each slice
        for i, z in enumerate(slice_positions):
            # Extract cells at this z level
            slice_cells = {(x, y): count for (x, y, z_val), count in self.total_cell_counts.items() if z_val == z}
            
            if not slice_cells:
                axes[i].text(0.5, 0.5, f'No cells at z={z}', 
                           horizontalalignment='center', verticalalignment='center')
                axes[i].set_title(f'z = {z}')
                continue
                
            # Prepare data for visualization
            x_coords, y_coords, frequencies = [], [], []
            for (x, y), count in slice_cells.items():
                x_coords.append(x)
                y_coords.append(y)
                frequencies.append(count / max_count)
                
            # Create the scatter plot for this slice
            scatter = axes[i].scatter(x_coords, y_coords, c=frequencies, cmap='plasma', 
                                   s=100, alpha=0.8, edgecolors='k', marker='s')
            
            axes[i].set_title(f'z = {z}')
            axes[i].set_xlabel('x')
            axes[i].set_ylabel('y')
            axes[i].grid(True)
            axes[i].set_aspect('equal')
            
        # Add a global colorbar
        plt.colorbar(scatter, ax=axes, label='Normalized Frequency')
        
        plt.tight_layout(rect=[0, 0, 1, 0.95])  # Adjust layout to make room for suptitle
        
        # Save if filename provided
        if filename:
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            
        plt.show()
        
        # Return the figure for web API usage
        return fig
        
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
        
        for (x, y, z), count in self.total_cell_counts.items():
            normalized_count = count / max_count
            cells_data.append({
                "x": x,
                "y": y,
                "z": z,
                "count": count,
                "normalized_count": normalized_count
            })
            
        return {
            "cells": cells_data,
            "max_count": max_count,
            "dimensions": {
                "max_x": max(x for x, _, _ in self.total_cell_counts.keys()) + 1,
                "max_y": max(y for _, y, _ in self.total_cell_counts.keys()) + 1,
                "max_z": max(z for _, _, z in self.total_cell_counts.keys()) + 1
            }
        } 