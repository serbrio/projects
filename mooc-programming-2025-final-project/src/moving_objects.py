import pygame
from random import choice
from maze import Maze


class Robot:
    """
    Robot(Maze, cell) -> new Robot object with rams=0 and coins=0.
    Robot(Maze, cell, rams=N, coins=K) -> new Robot object with rams=N and coins=K.

    Robot represents the object, which can be moved through the maze by user via the keyboard.
    Robot object provides public attributes and methods.
    
    Attributes:
    coins (amount of coins collected),
    rams (rams left),
    game_status (None, "passed", "gameover").

    Methods:
    process_event(event), move_robot(), set_keys(left, right, up, down, break_wall).
    """
    def __init__(self, maze: Maze, cell: tuple, rams=0, coins=0):
        self.__x = cell[0]
        self.__y = cell[1]
        self.__left = False
        self.__right = False
        self.__up = False
        self.__down = False
        self.__rams = rams
        self.__maze = maze
        self.coins = coins
        self.game_status = None
        self.set_keys(pygame.K_j, pygame.K_l, pygame.K_i, pygame.K_k, pygame.K_SPACE)

    @property
    def rams(self):
        return self.__rams

    def decrease_rams(self):
        """Decrease rams by one. Rams can not be less than 0."""
        if self.__rams - 1 >= 0:
            self.__rams -= 1

    def set_keys(self, left_k, right_k, up_k, down_k, break_wall_k):
        self.__left_k = left_k
        self.__right_k = right_k
        self.__up_k = up_k
        self.__down_k = down_k
        self.__break_wall_k = break_wall_k

    def __break_wall(self, x, y):
        """Break (remove) the wall in front of the robot (the wall hindering robot's movement).
        Outer walls can not be removed. One ram is used for removing one wall.
        """
        # If no rams left, impossible to break the wall
        if self.__rams == 0:
            return

        wall_cell = None

        if self.__left and not self.__maze.is_outer_wall((x-1, y)):
            wall_cell = (x-1, y)
            self.__left = False
        elif self.__right and not self.__maze.is_outer_wall((x+1, y)):
            wall_cell = (x+1, y)
            self.__right = False
        elif self.__up and not self.__maze.is_outer_wall((x, y-1)):
            wall_cell = (x, y-1)
            self.__up = False
        elif self.__down and not self.__maze.is_outer_wall((x, y+1)):
            wall_cell = (x, y+1)
            self.__down = False
        
        if wall_cell:
            self.__maze.mark_cell(wall_cell, self.__maze.path)
            self.decrease_rams()
        else:
            return

    def process_event(self, event: pygame.event.Event) -> None:
        """Process event: do corresponding action when a known key pressed."""
        if event.type == pygame.KEYDOWN:
            if event.key == self.__left_k:
                self.__left = True
            if event.key == self.__right_k:
                self.__right = True
            if event.key == self.__up_k:
                self.__up = True
            if event.key == self.__down_k:
                self.__down = True
            if event.key == self.__break_wall_k:
                self.__break_wall(self.__x, self.__y)

        if event.type == pygame.KEYUP:
            if event.key == self.__left_k:
                self.__left = False
            if event.key == self.__right_k:
                self.__right = False
            if event.key == self.__up_k:
                self.__up = False
            if event.key == self.__down_k:
                self.__down = False
        self.move_robot()

    def move_robot(self) -> None:
        """Move robot in the maze according to the key pressed.
        If robot hits the wall, do not move.
        If robot hits a monster, change self.game_status to "gameover".
        If robot hits a coin, collect it.
        If robot hits the door, change self.game_status to "passed".
        """
        # Do not move, if game_status is "gameover" or "passed"
        if self.game_status in ["gameover", "passed"]:
            return

        step = 0.5 
        # TODO: why step=1 does not work as expected

        # Save current coords
        target_x = self.__x
        target_y = self.__y

        # Change target coords by step according to the movement direction
        if self.__left:
            target_x -= step
        if self.__right:
            target_x += step
        if self.__up:
            target_y -= step
        if self.__down:
            target_y += step
        
        # If coords unchanged, return
        if (self.__x, self.__y) == (target_x, target_y):
            return
        
        target_mark = self.__maze.get_mark((target_x, target_y))
        # If target cell is a wall, do not move -> return
        if target_mark == self.__maze.wall:
            return
        # If target cell is a monster, do not move -> return
        if target_mark == self.__maze.monster:
            self.game_status == "gameover"
            return 
        # If target cell is a coin
        if target_mark == self.__maze.coin:
            self.coins += 1
        # If target cell is a door
        if target_mark == self.__maze.door:
            self.game_status = "passed"
            pass

        # Update the state of the maze:
        # 1) mark the old cell as path (robot left the cell)
        self.__maze.mark_cell((self.__x, self.__y), self.__maze.path)
        # 2) mark the new cell as robot (robot arrived in the cell)
        self.__maze.mark_cell((target_x, target_y), self.__maze.robot)

        # Update the coordinates (x, y) of the instance with the new ones.
        self.__x = target_x
        self.__y = target_y
        return
    

class Monster:
    """
    Monster(Maze, cell) -> new Monster object.

    Monster represents the object moving intelligently on its own through the maze.
    Monster object provides public attributes and methods.

    Attributes:
    game_status (None, "passed", "gameover"),
    overlapped (a dictionary with (cell, mark) as key, value pair), 
    which is used to process cells which have been moved over by monster.

    Methods:
    move_monster().
    """
    def __init__(self, maze: Maze, cell: tuple, speed: int=1) -> None:
        self.__x = cell[0]
        self.__y = cell[1]
        self.__speed = speed # TODO: currently not used
        self.__cycles = 0
        self.__maze = maze
        self.__closed_cells = set()
        self.__visited_cells = set()
        self.game_status = None
        self.overlapped = {}
    
    def __get_available_paths(self, cell: tuple) -> list:
        """Get and return the list of the nearest paths (cells), where monster can move to.
        The cells with walls and other monsters and the cells from self.__closed_cells
        are considered as not available for movement.
        (A cell gets into self.__closed_cells, if it is considered as closed end by the
        self.__is_closed_end() method. See also __track() method.)
        """
        # Get all the nearest cells
        nearest_cells = self.__maze.get_nearest(cell)
        excluded_marks = [self.__maze.wall, self.__maze.monster]
        # Exclude
        nearest_paths = [cell for cell in nearest_cells if self.__maze.get_mark(cell) not in excluded_marks]
        # Subtract the closed cells
        available_paths = set(nearest_paths).difference(self.__closed_cells)
        return list(available_paths)
    
    def __is_closed_end(self, cell: tuple) -> bool:
        """Return True, if monster is in the dead end of the maze or
        if there is 1 or less paths considered available.
        Else return False."""
        if self.__maze.is_dead_end(cell):
            return True
        
        available_paths = self.__get_available_paths(cell)
        if len(available_paths) <= 1:
            return True
        return False

    def __track(self, cell: tuple) -> tuple:
        """Track the maze: find the way through the maze choosing randomly on crossings 
        but avoiding going to the already visited places.        
        """
        current_cell = cell
       
       # If current cell is considred closed end
        if self.__is_closed_end(current_cell):
            # Remember current cell as closed_cell
            self.__closed_cells.add(current_cell)
            # Find the available for movement paths 
            # (excluding walls, other monsters and currently known closed_cells)
            available_paths = self.__get_available_paths(current_cell)
            # If there are no available paths
            if len(available_paths) == 0:
                # Forget all known closed_cells and visited_cells
                self.__closed_cells.clear()
                self.__visited_cells.clear()
                return current_cell
            # If it is a closed end and still a path exists, there is only one path.
            # Move to this path.
            current_cell = available_paths[0]
            return current_cell
        
        # If current cell is not closed end,
        # Remember current cell as visited_cell
        self.__visited_cells.add(current_cell)
        
        # Find the available for movements paths
        # (excluding walls, other monsters and currently known closed_cells)
        paths = self.__get_available_paths(current_cell)
        
        # If there are no paths left (it is dead end because of the closed cells),
        # clear the closed cells list, find paths again
        if len(paths) == 0:
            self.__closed_cells.clear()
            paths = self.__get_available_paths(current_cell)
        
        # From the available paths exclude visited_cells
        paths_visited_excluded = set(paths).difference(self.__visited_cells)
        # If there are paths left, choose one randomly
        if len(paths_visited_excluded) > 0:
            next_cell = choice(list(paths_visited_excluded))
        else:
            # If there are no paths left because of the visited cell, 
            # clear the list of visited cells
            self.__visited_cells.clear()
            # Choose from paths (including the visited)
            next_cell = choice(list(paths))
            
        return next_cell

    def __process_overlapped(self) -> None:
        """Process cells wich has been overlapped by monster:
        if cell has been overlapped and is not occupied by monster any more,
        it should regain its original mark.
        """
        if self.overlapped:
            for cell in list(self.overlapped):
                if cell != (self.__x, self.__y):
                    self.__maze.mark_cell(cell, self.overlapped[cell])
                    self.overlapped.pop(cell)
        return
    
    def __remember_overlapped(self, mark, cell: tuple) -> None:
        """Save the overlapped cell as key and its mark as value in self.overlapped dictionary."""
        self.overlapped[cell] = mark

    def move_monster(self) -> None:
        """Move monster in the maze randomly but intelligently using __track() method.
        If monster hits robot, change self.game_status to "gameover".
        If monster hits another monster, do not move.
        If monster hits a coin or a door, skip it (leave it on place). 
        """
        # Do not move, if game_status is "gameover" or "passed"
        if self.game_status in ["gameover", "passed"]:
            return 

        # Make monster move only every 30th iteration
        self.__cycles += 1
        if self.__cycles > 30:
            self.__cycles = 0
        if self.__cycles < 30:
            return
        
        while True:
            # Get target coords for the current location 
            # from the intelligent self.__track() method.
            target_x, target_y = self.__track((self.__x, self.__y))
            target_mark = self.__maze.get_mark((target_x, target_y))

            # If target cell is a robot, game is over
            if target_mark == self.__maze.robot:
                self.game_status = "gameover"
                return
            # If target mark is a monster, do not move
            if target_mark == self.__maze.monster:
                return
            # If target cell is a coin, move on, remember the overlapped coin
            if target_mark == self.__maze.coin:
                self.__remember_overlapped(target_mark, (target_x, target_y))
                break
            # If target cell is a door, move on, remember the overlapped door
            if target_mark == self.__maze.door:
                self.__remember_overlapped(target_mark, (target_x, target_y))
                break
            # If target cell is a path, exit loop
            if target_mark == self.__maze.path:
                break

        # Update the state of the maze:
        # 1) mark the old cell as path (robot left the cell)
        self.__maze.mark_cell((self.__x, self.__y), self.__maze.path)
        # 2) mark the new cell as robot (robot arrived in the cell)
        self.__maze.mark_cell((target_x, target_y), self.__maze.monster)

        # Update the coordinates (x, y) of the instance with the new ones.
        self.__x = target_x
        self.__y = target_y
        # After robot has moved to a new place, process overlapped cells
        self.__process_overlapped()

        return