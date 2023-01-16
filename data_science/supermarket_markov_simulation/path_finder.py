"""
Implementation of the A* pathfinding algorithm which is an addition to the Dijkstra algorithm,
which finds the shortest paths between two nodes (called "cells" here). Dijkstra is slow under
some circumstances, so A* adds a heuristic ("h") of how far (in e.g. euclidian distance or
manhattan distance) we need to go to the end node. Added to the shortest distance from one node to
another to the end node ("g") as defined in the Dijkstra algorithm, this combined value "f"
prioritizes nodes that go roughly in the right direction (that is, adds larger weights to those
that aren't such that they drop in the queue of nodes to be explored and thus are explored later).
Due to h, we actually penalize far away nodes so much, that we may end up never needing to explore
them because they are so far down in our queue, which is why A* is so much faster.
In short: Dijkstra pursues faster paths first (i.e. shorter spaced nodes or small g's), A* does too,
but only if they are roughly going towards the end node (small g's relative to small h's)
# For Dijkstra see: https://www.youtube.com/watch?v=GazC3A4OQTE
# For A* see: https://www.youtube.com/watch?v=ySN5Wnu88nE
"""
import heapq
from dataclasses import dataclass, field
from random import randint
from enum import Enum
from config import Locations, STORE_LOCATIONS, MARKET, UNWALKABLES


@dataclass
class Cell:
    """
    Holds information about a cell in a 2D map.
    """

    x_coord: int
    y_coord: int
    symbol: int
    g_shortest_distance: int = 0  # shortest distance from current to end cell
    h_best_guess_heuristic: int = 0  # best guess distance estimate from current to end cell
    f_added_g_h: int = 0  # combined g and h
    parent: bool = None

    def __lt__(self, other):
        """
        Enable lt dunder method since heapq compares values in a sorted list. @dataclass(Order=True)
        won't work since the __lt__ comparison is different. This will result in the path costs being
        reduced for the total path which will result in longer, inefficient paths to the target.
        """
        return self.f_added_g_h < other.f_added_g_h


@dataclass
class PathFinder:
    """Performs path finding process using the heapq module."""

    grid: str | list[list[str], ...]
    unwalkables: list[str, ...]
    start_symbol: str = "G"
    end_symbol: str = "E"
    store_locations: dict[Enum, ...] = field(default_factory=dict)
    is_efficient: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.grid, list):  # if string
            self.grid = [list(row) for row in self.grid.split("\n")]
        # Grid must be a 2D list of n by m Cell objects with x,y coordinates and the cell's symbol.
        self.grid = [
            [Cell(x_coord, y_coord, symbol) for y_coord, symbol in enumerate(row)]
            for x_coord, row in enumerate(self.grid)
        ]
        self.start_cell, self.end_cell = self._find_start_end()
        # If customer is inefficient, extend unwalkables (all symbols become unwalkable)
        if not self.is_efficient:
            self.unwalkables.extend([key for key in self.store_locations if key != "E"])

    def _find_start_end(self) -> tuple[Cell, Cell]:
        """Defines start and end cells depending on efficiency of customer."""
        #! This method has complex logic and could be improved.
        # Search the grid for the start and, if customer enter or exits or is efficient, end_cell
        for row in self.grid:
            for cell in row:
                if cell.symbol == self.start_symbol:
                    start_cell = cell
                # Customers that are efficient or enter/exit, move directly to target location
                if cell.symbol == self.end_symbol and (
                    self.end_symbol in [Locations.ENTRANCE.value, Locations.EXIT.value]
                    or self.is_efficient
                ):
                    end_cell = cell
        # Search end_cell for inefficient customers, who don't enter or exit. They move in the
        # general area of the target location: one and only one cell next to any target symbol.
        if not self.is_efficient and self.end_symbol not in [
            Locations.ENTRANCE.value,
            Locations.EXIT.value,
        ]:
            if self.store_locations:
                x_minmax, y_minmax = self.store_locations[self.end_symbol]
                attempts = 0
                while attempts <= 500:
                    target_x = randint(x_minmax[0], x_minmax[1])
                    target_y = randint(y_minmax[0], y_minmax[1])
                    if self.grid[target_y][target_x].symbol != self.end_symbol:
                        end_cell = self.grid[target_y][target_x]
                        break
                    attempts += 1
                else:
                    raise ValueError(
                        "Failed to find target location after 500 attempts. Consider reducing"
                        " the target area!"
                    )
            else:
                raise ValueError("Store locations dictionary is empty. Did you provide one?")
        if not start_cell or not end_cell:
            raise Exception("Start or end cell not found !")
        return start_cell, end_cell

    def heuristic(self, cell: Cell, target: Cell) -> None:
        """
        Calculates the heuristic costs of a cell using the Manhattan Distance formula defined
        as sum of absolute differences of x and y between current and target cell
        """
        return abs(cell.x_coord - target.x_coord) + abs(cell.y_coord - target.y_coord)

    def get_neighbors(self, cell: Cell) -> list[Cell, ...]:
        """Returns a list of immediately adjacent cells relative to the current cell"""
        neighbors = []
        if cell.x_coord > 0:  # left
            neighbors.append(self.grid[cell.x_coord - 1][cell.y_coord])
        if cell.x_coord < len(self.grid) - 1:  # right
            neighbors.append(self.grid[cell.x_coord + 1][cell.y_coord])
        if cell.y_coord > 0:  # top
            neighbors.append(self.grid[cell.x_coord][cell.y_coord - 1])
        if cell.y_coord < len(self.grid[0]) - 1:  # bottom
            neighbors.append(self.grid[cell.x_coord][cell.y_coord + 1])
        return neighbors

    def reached_end(self, current_cell) -> list[tuple, ...]:
        """
        Creates the path to the current cell by retracing the parent cells.
        Assumes current cell is target cell.
        """
        path = []
        while current_cell.parent:
            path.append((current_cell.x_coord, current_cell.y_coord))
            current_cell = current_cell.parent
        path.append((current_cell.x_coord, current_cell.y_coord))
        path.reverse()
        return path

    def evaluate_neighbors(
        self,
        current_cell: Cell,
        end_cell: Cell,
        open_set: list[Cell, ...],
        closed_set: list[Cell, ...],
    ) -> None:
        """Evaluates the neighbors by updating the heuristics and costs of a chosen, valid move."""
        # Check neighbors of current cell for validity (i.e., obstacle or already explored).
        # If valid, calculate tentative movement cost to inform decision on parent cell.
        for neighbor in self.get_neighbors(current_cell):
            if neighbor.symbol in self.unwalkables or neighbor in closed_set:
                continue
            tentative_cost_path = current_cell.g_shortest_distance + 1
            # If neighbor cell is still not fully explored (in open set) or if tentative_cost_path
            # are lower than g_shortest_distance score of the current cell, make it a parent cell
            # and add it to the open set, if isn't already.
            if (neighbor not in open_set) or (tentative_cost_path < neighbor.g_shortest_distance):
                neighbor.g_shortest_distance = tentative_cost_path
                neighbor.h_best_guess_heuristic = self.heuristic(cell=neighbor, target=end_cell)
                neighbor.f_added_g_h = (
                    neighbor.g_shortest_distance + neighbor.h_best_guess_heuristic
                )
                neighbor.parent = current_cell
                if neighbor not in open_set:
                    heapq.heappush(open_set, neighbor)


def main(
    grid: str | list[list[str, ...]],
    unwalkables: list[str, ...],
    start_symbol: str,
    end_symbol: str,
    store_locations: dict,
    is_efficient: bool = True,
) -> list[tuple[int, int], ...]:
    """Initializes heapq and runs a A* search from a starting to an end cell."""
    instance_pathfinder = PathFinder(
        grid=grid,
        unwalkables=unwalkables,
        start_symbol=start_symbol,
        end_symbol=end_symbol,
        store_locations=store_locations,
        is_efficient=is_efficient,
    )
    open_set, closed_set = [], []
    heapq.heappush(open_set, instance_pathfinder.start_cell)
    while open_set:
        # Pop the cell with lowest f_added_g_h score from open set and add it to closed_set
        current_cell = heapq.heappop(open_set)
        closed_set.append(current_cell)
        if current_cell == instance_pathfinder.end_cell:
            return instance_pathfinder.reached_end(current_cell=current_cell)
        instance_pathfinder.evaluate_neighbors(
            current_cell=current_cell,
            end_cell=instance_pathfinder.end_cell,
            open_set=open_set,
            closed_set=closed_set,
        )


if __name__ == "__main__":
    main(
        grid=MARKET,
        unwalkables=UNWALKABLES,
        start_symbol=Locations.ENTRANCE.value,
        end_symbol=Locations.SPICES.value,
        is_efficient=False,
        store_locations=STORE_LOCATIONS
    )
