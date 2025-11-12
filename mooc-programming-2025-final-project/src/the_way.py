import pygame
from maze import Maze
from moving_objects import Robot, Monster
from levels import Levels


class TheWay:
    """
    TheWay() -> new TheWay game with 1 level.
    TheWay(levels_amount=N) -> new TheWay game with N levels.

    TheWay is an arcade game, which idea is to find the exit in 
    the maze using the keyboard to control the robot movements.
    The exit is shown after all the coins are collected.
    There are monsters moving through the maze. 
    The game is considered over when robot contacts the monster.
    Robot has superpower, limited quantity of rams, to break the wall.

    The game has only fullscreen mode.
    """
    def __init__(self, levels_amount: int = 1) -> None:
        pygame.init()
        self.levels_amount = levels_amount
        self.window = pygame.display.set_mode(flags=pygame.FULLSCREEN)
        self.game_font = pygame.font.SysFont("Arial", 24)
        self.game_font_big = pygame.font.SysFont("Arial", 48)
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("The Way")
        self.main_loop()

    def __set_sizes(self) -> None:
        """Count and set sizes: fullscreen width and height and 
        maximum sizes of the maze, i.e. number of columns and rows in the maze.
        """
        # Game is fullscreen
        # Get and save sizes of the screen
        video_info = pygame.display.Info()
        self.width = video_info.current_w
        self.height = video_info.current_h  
        # On the window, there should be left place for the game instructions,
        # so make maze height smaller by 1 square height.
        self.maze_columns = self.width//self.square_size
        self.maze_rows = self.height//self.square_size - 1

    def __create_wall_image(self, color: pygame.color.Color) -> pygame.surface.Surface:
        """Draw the square image of a wall brick. Return pygame object.
        """
        size = self.square_size
        wall = pygame.Surface((size, size))
        wall.fill(color)
        brick_points = [(8, 6), (4, 18), (4, size-16), (6, size-8), (size-6, size-4),
                        (size-4, size-6), (size-4, 6), (size-6, 4)]
        pygame.draw.polygon(wall, (100, 30, 30), brick_points)
        return wall

    def __load_images(self, image_names: list) -> None:
        """Load images from the given list. 
        (Images should exist in the workind dir with .png extension.)
        Save them to self.images dictionary, use image name as key.
        Set the size of the square building block based on the robot image.
        """
        self.images = {}
        for name in image_names:
            self.images[name] = pygame.image.load(name + '.png')

        # Set the size of the square building block
        self.square_size = self.images["robot"].get_height() + 4

        # Add image of wall brick
        self.images["wall"] = self.__create_wall_image(pygame.Color("black"))

    def __set_margins(self) -> None:
        """After the Maze() is initialized, the dimensions of the maze might be changed
        according to the Maze's internal logic.
        Using actual dimensions of the Maze, set margins to place the maze in the window.
        x_margin - to place the maze horizontally in the center.
        y_margin - to indent from top of the window.
        Set y coordinate for instructions line.
        """
        self.x_margin = (self.width - (self.maze.width * self.square_size))/2
        self.y_margin = 6
        # Set y coordinate for instructions line
        self.instructions_y_coord = self.height-(self.square_size/2)-self.y_margin

    def new_maze(self, robots: int = 1, doors: int = 1, monsters: int = 2, coins: int = 10) -> None:
        """Create a Maze object with the dimensions self.maze_columns and self.maze_rows.
        Put robot(s), door(s), monster(s) and coin(s) into the maze.
        """
        self.maze = Maze(self.maze_columns, self.maze_rows)

        # At least one robot is put into the maze.
        # The first one robot is put into the start_cell of the maze.
        self.maze.mark_cell(self.maze.start_cell, self.maze.robot)
        # Put more robots into the maze onto the random places, if there are more than one robot.
        for _ in range(robots-1):
            self.maze.mark_cell(self.maze.pick_random_cell(self.maze.path), self.maze.robot)
        
        # At least one door(exit) is put into the maze.
        # The first one door is put into the finish_cell of the maze.
        self.maze.mark_cell(self.maze.finish_cell, self.maze.door)
        # Put more doors into the maze randomly, if there are more than one door.
        for _ in range(doors-1):
            self.maze.mark_cell(self.maze.pick_random_cell(self.maze.path), self.maze.door)

        # Put monsters into the maze onto the random places.
        for _ in range(monsters):
            self.maze.mark_cell(self.maze.pick_random_cell(self.maze.path), self.maze.monster)
        # Put coins into the maze onto the random places.
        for _ in range(coins):
            self.maze.mark_cell(self.maze.pick_random_cell(self.maze.path), self.maze.coin)

    def map_maze_marks_to_images(self) -> None:
        """Map image objects in self.images to the marks of the self.maze.
        Save mark value (0, 1, 2 etc) as key and image object as value in self.marked_images dictionary.
        """
        self.marked_images = {value: self.images[name] for name, value in self.maze.marks.items() if name in self.images}
    
    def new_game(self, level: dict) -> None:
        """Prepare for a new game according to the given level.
        """
        self.__load_images(["door", "coin", "robot", "monster"])
        self.__set_sizes()
        self.new_maze(monsters=level['monsters'], coins=level['coins'])
        self.__set_margins()
        self.map_maze_marks_to_images()
        self.hide_doors()

        self.robot = Robot(self.maze, self.maze.start_cell, rams=level['rams'])
        monster_cells = self.maze.find_cells_by_mark(self.maze.monster)
        self.monsters = [Monster(self.maze, monster_cell) for monster_cell in monster_cells]
    
    def update_objects_game_status(self, status: str) -> None:
        """Update game status in all moving objects.
        """
        objects = self.monsters + [self.robot]
        for object in objects:
            object.game_status = status
    
    def game_over(self) -> bool:
        """If game is over, update game status in all moving objects to "gameover" 
        and return True, else return False.
        Game is over if at least one of the monsters or robot have game_status "gameover".
        """
        for monster in self.monsters:
            if monster.game_status == "gameover":
                # Update game statuses of all moving objects for consistency
                # (objects do not move, if game is passed or over)
                self.update_objects_game_status("gameover")
                return True
        if self.robot.game_status == "gameover":
            self.update_objects_game_status("gameover")
            return True
        return False
    
    def level_passed(self) -> bool:
        """If level passed, update game status in all moving objects to "passed"
        and return True, else return False.
        Level is passed if robot has game_status "passed".
        """
        if self.robot.game_status == "passed":
            # Update game statuses of all moving objects for consistency
            # (objects do not move, if game is passed or over)
            self.update_objects_game_status("passed")
            return True
        return False
    
    def game_passed(self) -> bool:
        """If game is passed, return True, else False.
        Game is passed if the last level is passed.
        """
        if self.level_passed() and self.level["level"] == self.levels_amount:
            return True
        return False

    def hide_doors(self) -> None:
        """Save the coordinates of cells containing doors into self.hidden_doors,
        remove the doors from the maze (mark cells with doors as paths).
        """
        self.hidden_doors = self.maze.find_cells_by_mark(self.maze.door)
        for cell in self.hidden_doors:
            self.maze.mark_cell(cell, self.maze.path)

    def unhide_doors(self) -> None:
        """Put the doors into the maze (mark cells in maze by coordinates from self.hidden_doors as doors), 
        remove from self.hidden_doors accordingly.
        """
        for cell in self.hidden_doors:
            # If cell is occupied by monster, do nothing
            if self.maze.check_mark(cell, self.maze.monster):
                return
            self.maze.mark_cell(cell, self.maze.door)
            self.hidden_doors.remove(cell)

    def process_doors(self) -> None:
        """If all coins collected by robot, unhide the doors.
        """
        # Count coins left in maze
        coins_left = len(self.maze.find_cells_by_mark(self.maze.coin))
        # If any coins left, do nothing
        if coins_left > 0:
            return
   
        # If at least one coin is overlapped by any monster, do nothing
        for monster in self.monsters:
            found = [cell for (cell, mark) in monster.overlapped.items() if mark == self.maze.coin]
            if len(found) > 0:
                return
            
        self.unhide_doors()

    def instructions_loop(self) -> None:
        """Draw window with instructions and wait until user pushes button to start.
        """
        while True:
            self.draw_instructions_window()
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        exit()
                    if event.key == pygame.K_F2:
                        return

    def main_loop(self) -> None:
        """Before the main loop:
        create Levels object, prepare the new game for the given level,
        show instructions and wait until user decides to start.
        In main loop:
        process doors (hide/unhide), move monsters, draw the window,
        check events.
        """
        levels = Levels(amount=self.levels_amount)
        # Get iterator from the Levels object,
        # to be able further to get the next value from it one by one
        self.iter_levels = iter(levels)
        self.level = next(self.iter_levels)
        self.new_game(self.level)
        self.instructions_loop()
        
        while True:
            self.process_doors()
            for monster in self.monsters:
                monster.move_monster()
            self.draw_window()
            self.check_events()
            self.clock.tick(60)

    def check_events(self) -> None:
        """Check events received by pygame.
        Escape button for exit.
        F2 button for restart the current level.
        F3 button for next level.
        """
        for event in pygame.event.get():
            self.robot.process_event(event)
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    exit()
                # If F2 pushed: restart the game on the same level
                if event.key == pygame.K_F2:
                    self.new_game(self.level)
                # If level passed, game not passed and F3 pushed: go to the next level
                if self.level_passed() and not self.game_passed() and event.key == pygame.K_F3:
                    # Set game status to None
                    self.update_objects_game_status(None)
                    # Get the next level
                    self.level = next(self.iter_levels)
                    self.new_game(self.level)

    def draw_maze_background(self, color: pygame.color.Color) -> None:
        """Create image of maze background inside the horizontal and vertical outer walls.
        Draw the image onto the game window.
        """
        width = self.square_size * (self.maze.width - 2)
        height = self.square_size * (self.maze.height - 2)
        maze_background = pygame.Surface((width, height))
        maze_background.fill(color)
        # Find coordinates where to draw the image: upper left corner inside the maze walls.
        # To not forget the margins.
        x = self.x_margin + self.square_size
        y = self.y_margin + self.square_size
        self.window.blit(maze_background, (x, y))
            
    def draw_window(self) -> None:
        """Draw the game window according to the game status.
        """
        self.window.fill(pygame.Color("black"))
        
        if self.game_over():
            self.draw_gameover_text()
            pygame.display.flip()
            return
        
        if self.game_passed():
            self.draw_gamepassed_text()
            pygame.display.flip()
            return
        
        if self.level_passed():
            self.draw_levelpassed_text()
            pygame.display.flip()
            return
        
        self.draw_maze_background(pygame.Color("gray40"))
        
        for mark, cell in self.maze:
            self.draw_cell(cell, mark)
        self.draw_info_text()
        pygame.display.flip()

    def draw_instructions_window(self) -> None:
        """Draw the window with instructions on how to play the game.
        """
        self.window.fill(pygame.Color("black"))
        instructions = ["Collect all coins to find the exit!",
                        "Avoid monsters.", "", 
                        "Use rams to break the wall:", 
                        "while moving press SPACE button to break the wall.", "",
                        "GOOD LUCK!", "", "",
                        "Press F2 to start."]

        for line_number, instruction in enumerate(instructions):
            text = self.game_font.render(instruction, True, (0, 0, 255))
            
            line_height = self.game_font.get_height()
            x = self.width/2 - text.get_width()/2
            y = self.height/2 - line_height*len(instructions)/2

            self.window.blit(text, (x, y + line_height*line_number))

        self.draw_escape_text()
        self.draw_controls_text()
        pygame.display.flip()

    def draw_cell(self, cell: tuple, mark: int) -> None:
        """Draw appropriate image in the center of the cell,
        if its mark is mapped to the loaded images, else skip.
        """
        if mark in self.marked_images:
            image = self.marked_images[mark]
            x = cell[0] * self.square_size + self.x_margin
            y = cell[1] * self.square_size + self.y_margin
            # Put image in the center of the square
            x_centered = self.square_size/2 - image.get_width()/2
            y_centered = self.square_size/2 - image.get_height()/2
            x += x_centered
            y += y_centered
            self.window.blit(image, (x, y))

    def draw_info_text(self) -> None:
        """Draw info and control texts.
        (pygame.display.flip() must be executed subsequently).
        """
        self.draw_escape_text()
        self.draw_restart_text()
        self.draw_controls_text()
        self.draw_rams_text()
        self.draw_coins_text()

    def draw_gameover_text(self) -> None:
        """Draw texts when game is over.
        (pygame.display.flip() must be executed subsequently).
        """
        game_over_text = self.game_font_big.render("Game over...", True, (255, 0, 0))
        self.window.blit(game_over_text, (self.width/2-game_over_text.get_width()/2, self.height/2))
        self.draw_escape_text()
        self.draw_restart_text()
        self.draw_rams_text()
        self.draw_coins_text()

    def draw_levelpassed_text(self) -> None:
        """Draw texts when level passed.
        (pygame.display.flip() must be executed subsequently).
        """
        level_passed_text = self.game_font_big.render(f"Level {self.level['level']} passed!", True, (0, 255, 0))
        self.window.blit(level_passed_text, (self.width/2-level_passed_text.get_width()/2, self.height/2))
        self.draw_escape_text()
        self.draw_nextlevel_text()
        self.draw_rams_text()
        self.draw_coins_text()

    def draw_gamepassed_text(self) -> None:
        """Draw texts when game is passed (finished).
        (pygame.display.flip() must be executed subsequently).
        """
        game_passed_text = self.game_font_big.render(f"Game passed. Congratulations!", True, (0, 255, 0))
        self.window.blit(game_passed_text, (self.width/2-game_passed_text.get_width()/2, self.height/2))
        self.draw_escape_text()
        self.draw_restart_text()
        self.draw_rams_text()
        self.draw_coins_text()
        
    def draw_escape_text(self) -> None:
        """Draw text about how to exit.
        """
        escape_text = self.game_font.render("Esc: exit", True, (0, 0, 255))
        self.window.blit(escape_text, (self.x_margin, self.instructions_y_coord))

    def draw_restart_text(self) -> None:
        """Draw text about how to restart the game on the current level.
        """
        restart_text = self.game_font.render("F2: restart", True, (0, 0, 255))
        self.window.blit(restart_text, (self.x_margin + 150, self.instructions_y_coord))

    def draw_nextlevel_text(self) -> None:
        """Draw text about how to start next level.
        """
        nextlevel_text = self.game_font.render("F3: next level", True, (0, 0, 255))
        self.window.blit(nextlevel_text, (self.x_margin + 350, self.instructions_y_coord))

    def draw_controls_text(self) -> None:
        """Draw text about how to control robot.
        """
        controls_str = f"Left:  j{' '*5}Right:  l{' '*5}Up:  i{' '*5}Down:  k{' '*5}Break wall: Space"
        controls_text = self.game_font.render(controls_str, True, (0, 255, 0))
        self.window.blit(controls_text, (self.x_margin + 600, self.instructions_y_coord))

    def draw_coins_text(self) -> None:
        """Draw text about the coins status.
        """
        coins_text = self.game_font.render(f"Coins collected: {self.robot.coins}({self.level['coins']})", True, (255, 0, 0))
        self.window.blit(coins_text, (self.width - self.x_margin - coins_text.get_width(), self.instructions_y_coord))

    def draw_rams_text(self) -> None:
        """Draw text about the rams status.
        """
        rams_text = self.game_font.render(f"Rams left: {self.robot.rams}", True, (255, 0, 0))
        self.window.blit(rams_text, (self.width - self.x_margin - 250 - rams_text.get_width(), self.instructions_y_coord)) 

            
if __name__ == "__main__":
    TheWay(1)