import copy
import random
import argparse

from itertools import product
from typing import Tuple, List, Iterator

import pyhocon
import numpy as np
import matplotlib.pyplot as plt

def find_neighbors(
    xy: Tuple[int, int],
    n_rows: int,
    n_cols: int,
    neighbor_size: int
) -> Iterator:
    """
        Finds the neighbors of a given (x, y) coordinate.
        `n_rows`, `n_cols` ensure that only a part of the
        neighborhood is counted along the boundary.

        Parameters
        -----------
            - xy: `Tuple[int, int]`
                - the coordinate of a given resident.
            - n_rows: `int`
                - number of rows in the grid.
            - n_cols: `int`
                - number of cols in the grid.
            - neighbor_size: `int`
                - size of the neighborhood in radius.
        Returns
        --------
            - `Iterator`
                - yields a single neighbor.
    """
    for c in product(
        *(range(
            n-neighbor_size, n+neighbor_size+1
        ) for n in xy)
    ):
        if (c != xy) and (c[0] in range(n_rows)) and (c[1] in range(n_cols)):
            yield c

def similarity(
    grid: np.ndarray,
    xy: Tuple[int, int],
    neighbor_size: int,
    tolerance: float
) -> bool:
    """
        Tells the given resident at (x,y) to move out or not.
        If the neighborhood has a fraction of residents with
        the same grouping as the given resident less than a 
        certain threshold, return False.

        Parameters
        -----------
            - grid: `np.ndarray`
                - the current state of the grid.
            - xy: `Tuple[int, int]`
                - the coordinate of a given resident.
            - neighbor_size: `int`
                - size of the neighborhood in radius.
            - tolerance: `float`
                - tolerance threshold.
        Returns
        --------    
            - `bool`
                - `True` if needs to be flipped, else `False`
    """
    # Need to move (True) if fraction of friendlies are below tolerance
    m, n = grid.shape
    neighborhood = [
        grid[k] for k in list(find_neighbors(xy, m, n, neighbor_size))
    ]
    cnt = neighborhood.count(grid[xy]) / len(neighborhood)
    
    if cnt < tolerance:
        return True
    else:
        return False

class SchellingModel:

    """
        Class for 2-agent schelling segregation model.

        Parameters
        -----------
            - size: `Tuple[int, int]`
                - size of the grid given in tuples.
            - neighbor_size: `int`
                - size of the neighbordhood given in radius.
            - neighbor_tol: `int`
                - tolerance threshold.
            - prior_dist: `List[float]`
                - a list of init. probability distribution of each group.
                  (0 for empty, -1 and 1 for each group)
            - max_frame: `int`
                - maximum frame to run the simulation.
            - show_every: `int`
                - shows grid at every `show_every` frames.
    """
    def __init__(
        self,
        size: Tuple[int, int],
        neighbor_size: int,
        neighbor_tol: float,
        prior_dist: List[float],
        max_frame: int=50,
        show_every: int=5
    ):
        self.size = size
        self.neighbor_size = neighbor_size
        self.neighbor_tol = neighbor_tol
        self.prior_dist = prior_dist
        
        self.max_frame = max_frame
        self.show_every = show_every

    def run(self):
        # Take height (# rows) and width (# cols)
        h, w = self.size

        # Randomly intialize grid.
        # There are three states, namely -1, 0, 1 where 0 is the empty space.
        grid = np.random.choice(3, size=self.size, p=self.prior_dist) - 1

        # Run for each frame
        frame = 0
        while frame < self.max_frame:
            if not frame % self.show_every:
                fig, ax = plt.subplots()
                fig.suptitle('Iteration %d' % frame, fontsize=10)
                ax.matshow(grid)

                # Press 'q' to proceed to the next snapshot
                plt.show()
            
            for i in range(h):
                for j in range(w):
                    # If space is empty, don't do anything.
                    if grid[(i,j)] == 0:
                        pass
                    # Else
                    else:
                        # If needs to be flipped, move the given resident somwhere empty.
                        # Leave the space empty when the resident moves out.
                        if similarity(grid, (i,j), self.neighbor_size, self.neighbor_tol):
                            empty1, empty2 = random.choice(np.argwhere(grid == 0))
                            grid[empty1, empty2] = grid[(i,j)]
                            grid[(i,j)] = 0
            frame += 1
                
if __name__ == '__main__':
    # Argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--config', 
        type=str,
        default='default'
    )
    args = parser.parse_args()
    
    # Build configuration
    config = pyhocon.ConfigFactory.parse_file('experiments.conf')[args.config]
    config_dict = {
        'size': (config['height'], config['width']),
        'neighbor_size': config['neighbor_size'],
        'neighbor_tol': config['neighbor_tol'],
        'prior_dist': config['prior_dist'],
        'max_frame': config['max_frame'],
        'show_every': config['show_every']
    }

    # Build model and run
    model = SchellingModel(**config_dict)
    model.run()
 