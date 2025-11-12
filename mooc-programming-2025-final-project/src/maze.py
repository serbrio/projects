from __future__ import annotations
#from typing import Self  # available from Python 3.11
from random import choice


class Maze:
    """
    Maze(width, height) -> new Maze object containing the height-by-width matrix.
    
    Maze is a randomly structured labyrinth containing paths and walls, 
    outer walls are obligatory.
    
    Maze object provides public attributes and methods, which can be used to
    utilize and change the maze.

    Public attributes: 
    randomly placed start_cell and finish_cell,
    width, height, 
    maze - actual matrix filled with marks, 
    marks - dictionary of (mark name, mark value) as (key, value) pairs,
    marks can be accessed by name as properties of the Maze object.

    Public methods:
    pick_random_cell(mark), get_nearest(cell), is_outer_wall(cell), 
    is_dead_end(cell), find_cells_by_mark(mark), dead_ends(), 
    mark_cell(cell, mark), check_mark(cell, mark), get_mark(cell),
    (cell is a tuple of coordinates (x, y) in maze matrix).

    Maze object is iterable, returning mark and coordinates (x, y) of a cell.
    Optional argument walls_factor increases amount of walls inside labyrinth.
    Width and height are expected to be odd numbers, if not, 1 is subtracted from the even one.
    """
    def __init__(self, width: int, height: int, walls_factor=0) -> None:
        # Check width and height are not equal numbers, else subtract 1.
        if width%2 == 0:
            width -= 1
        if height%2 == 0:
            height -= 1
        self.width = width
        self.height = height

        if walls_factor > 1 or walls_factor < 0:
            raise ValueError(f"walls_factor must be 0 <= float <= 1, given: {walls_factor}")
        self.walls_factor = walls_factor
        
        self.__set_marks()
        self.__generate_maze_blueprint()
        self.__add_more_walls()
        self.start_cell = self.pick_random_cell(self.unvisited)
        self.finish_cell = None
        self.__track_maze(self.start_cell)

    @property
    def unvisited(self) -> int:
        return self.marks['unvisited']
    
    @property
    def wall(self) -> int:
        return self.marks['wall']
    
    @property
    def path(self) -> int:
        return self.marks['path']
    
    @property
    def coin(self) -> int:
        return self.marks['coin']

    @property
    def door(self) -> int:
        return self.marks['door']
    
    @property
    def monster(self) -> int:
        return self.marks['monster']

    @property
    def robot(self) -> int:
        return self.marks['robot']
        
    def __str__(self) -> str:
        result = ''
        for row in self.maze:
            strings = [str(c) for c in row]
            result += ''.join(strings) + '\n'
        return result
    
    def __iter__(self) -> Maze:
        self.__n = 0
        return self
    
    def __next__(self) -> tuple:
        if self.__n < self.width * self.height:
            x, y = (self.__n % self.width, self.__n // self.width)
            mark = self.maze[y][x]
            self.__n += 1
            return mark, (x, y)
        else:
            raise StopIteration

    def __set_marks(self) -> None:
        self.marks = {}
        i = 0
        for name in ['unvisited', 'wall', 'path', 'coin', 'door', 'monster', 'robot']:
            self.marks[name] = i
            i += 1

    def __generate_maze_blueprint(self) -> None:
        """Generates the maze blueprint as two-dimensional massive. 
        It has outer walls and walls between every cell, vertically and horizontally.
        Walls and cells have their own places in the massive, i.e. 
        they all have their own coordinates (x, y).
        """
        self.maze = []
        # Make a horizontal wall, e.g. [0, 0, 0, 0, 0]
        horizontal_wall = [self.wall for _ in range(self.width)]
        # Every row which contains path cells starts and ends with a wall, 
        # plus between cells there should be walls as well, e.g. [0, 1, 0, 1, 0]
        # Row has length = (width//2)*2 + 1 = width, because width is not even number.
        row = [self.wall] + [self.unvisited, self.wall]*(self.width//2)
        # Add the first row
        self.maze.append(horizontal_wall[:]) # add list[:], a copy of list, not a reference
        # Add the rest rows, which altogether with the previously added row equal to the height
        for _ in range(self.height//2):
            self.maze.append(row[:])
            self.maze.append(horizontal_wall[:])

    def __add_more_walls(self) -> None:
        """Add additional walls instead of unvisited cells into the maze, placed randomly.
        The amount of walls added is directly proportional to walls_factor.
        """
        amount = round(self.width * self.height * self.walls_factor)
        if amount <= 0:
            return
        cells = self.find_cells_by_mark(self.unvisited)
        for _ in range(amount):
            if len(cells) <= 1: # At least 1 place for the start cell should remain
                break
            cell = choice(cells)
            cells.remove(cell)
            self.mark_cell(cell, self.wall)

    def pick_random_cell(self, mark: int) -> tuple:
        """Pick one random cell, which contains the given mark.
        If found, returns a tuple of cell coordinates (x, y), (y corresponds to the row, x - to the column),
        else None.
        """
        cell = None
        cells = self.find_cells_by_mark(mark)
        if cells:
            cell = choice(cells)
        return cell

    def __get_unvisited_neighbours(self, cell: tuple) -> list:
        """Get and return a list of neighbour unvisited cells for the given cell.
        Assume, neighbors are those cells, which are to the left/right, below/above
        of the given cell.
        """
        neighbours = []
        x, y = cell
        # Check neighbour of the given cell to the left: 
        # 1) is not the outer left wall of the maze (i.e. has index > 0)
        # 2) is unvisited
        # NB! Between the cells there are vertical and horizontal walls, which take their own coordinates/indexes.
        if x-2 > 0 and self.maze[y][x-2] == self.unvisited:
            # add found unvisited neighbour to neighbours list
            neighbours.append((x-2, y))
        if x+2 < len(self.maze[0])-1 and self.maze[y][x+2] == self.unvisited:
            neighbours.append((x+2, y))
        if y-2 > 0 and self.maze[y-2][x] == self.unvisited:
            neighbours.append((x, y-2))
        if y+2 < len(self.maze)-1 and self.maze[y+2][x] == self.unvisited:
            neighbours.append((x, y+2))
        return neighbours

    def __remove_wall(self, cell1: tuple, cell2: tuple, mark: int) -> None:
        """Remove wall between the two given cells.
        Place mark instead of wall.
        """
        x1, y1 = cell1
        x2, y2 = cell2

        # If cells are in the same column (have the same x coordinate)
        if x1 == x2:
            # If cell2 is above cell1, the wall is above the cell1
            if y1 > y2:
                y_w = y1-1
            else:
                # Else the wall is beneath the cell1
                y_w = y1+1
            x_w = x1
        # If cells are in the same row (have the same y coordinate)
        if y1 == y2:
            # If cell 2 is to the left of cell1, the wall is to the left
            if x1 > x2:
                x_w = x1-1
            else:
                # Else: the wall is to the right
                x_w = x1+1
            y_w = y1
        self.maze[y_w][x_w] = mark

    def __track_maze(self, cell: tuple) -> None:
        """Create a random maze in self.maze, the previously created blueprint.
        self.start_cell is used as the start point; the finish point is stored in self.finish_cell.
        The used labyrinth creation algorithm can be found here:
        https://en.wikipedia.org/wiki/Maze_generation_algorithm#Recursive_implementation
        """
        # Mark the current cell as path.
        self.mark_cell(cell, self.path)
        # Find all unvisited neighbour cells.
        # Walls between the actual cells have their coordinates, but are not considered as cells.
        neighbours = self.__get_unvisited_neighbours(cell)
        # While the current cell has neighbours
        while len(neighbours) > 0:
                # Choose a random neighbour
                chosen = choice(neighbours)
                # If that chosen is unvisited
                if self.check_mark(chosen, self.unvisited):
                    # Save the chosen in the instance attribute self.finish_cell
                    self.finish_cell = chosen
                    # Remove the wall between the chosen and the current cell, mark it as path
                    self.__remove_wall(cell, chosen, self.path)
                    # Initiate recursively the whole procedure for the chosen 
                    self.__track_maze(chosen)
                # Remove the chosen from the list of unvisited neighbour cells 
                neighbours.remove(chosen)
        return
    
    def __parse_cell(self, cell: tuple) -> tuple:
        """Check cell is in correct format: tuple with two integers. 
        Return (x, y) or raise ValueError.
        """
        try:
            x, y = cell
            x, y = int(x), int(y)
        except (TypeError, ValueError):
            raise ValueError(f"cell must be a tuple of two integers (x, y), given: {cell}")
        return x, y
    
    def get_nearest(self, cell: tuple) -> list:
        """Get and return a list of the four nearest cells' coordinates, 
        surrounding the given cell (left, right, above, below).
        """
        x, y = self.__parse_cell(cell)
        if x <= 0 or x >= self.width-1 or y <=0 or y >= self.height-1:
            raise ValueError(f"Not supported. Cell {cell} seems to be a brick in the outer wall.")
        return [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
    
    def is_outer_wall(self, cell: tuple) -> bool:
        """Return True, if the cell is outer wall or is out of the maze, else False."""
        x, y = self.__parse_cell(cell)
        if x <= 0 or x >= self.width-1:
            return True
        if y <= 0 or y >= self.height-1:
            return True
        return False
    
    def is_dead_end(self, cell: tuple) -> bool:
        """Return boolean: if the cell is a dead end i.e.
        it has walls to its three sides.
        """
        nearest = [self.maze[y][x] for x, y in self.get_nearest(cell)]
        return nearest.count(self.wall) == 3
    
    def find_cells_by_mark(self, mark: int) -> list:
        """Find all cells containing mark and return their coordinates in a list of tuples (x, y).
        """
        found = []
        # Iterate over self, the maze cell by cell
        for m, cell in self:
            if m == mark:
                found.append(cell)
        return found

    def dead_ends(self) -> list:
        """Find all path cells, which are 'dead ends'.
        Return their coodrinates in a list of tuples (x, y).
        """
        paths = self.find_cells_by_mark(self.path)
        return [cell for cell in paths if self.is_dead_end(cell)]

    def mark_cell(self, cell: tuple, mark: int) -> None:
        """Place mark in the given cell of the maze."""
        x, y = self.__parse_cell(cell)
        self.maze[y][x] = mark

    def check_mark(self, cell: tuple, mark: int) -> bool:
        """Check the given cell contains the given mark. Return True or False."""
        x, y = self.__parse_cell(cell)
        return self.maze[y][x] == mark
    
    def get_mark(self, cell: tuple) -> int:
        """Return the mark of the given cell (x, y)."""
        x, y = self.__parse_cell(cell)
        return self.maze[y][x]


if __name__ == "__main__":
    maze = Maze(30, 20)
    maze.mark_cell(maze.start_cell, maze.robot)
    maze.mark_cell(maze.finish_cell, maze.door)
    print(maze)