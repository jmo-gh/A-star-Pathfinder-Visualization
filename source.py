import pygame
import math
import random
from queue import PriorityQueue

# setup display
WIDTH = 800
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("A* Pathfinding Algorithm")

# colors
# RED - processed node
# WHITE - unprocessed node
# BLACK - barrier
# ORANGE - start node
# PURPLE - best path

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)

class Node:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.width = width
        self.total_rows = total_rows

    def get_pos(self):
        return self.row, self.col

    def is_closed(self):
        return self.color == RED

    def is_open(self):
        return self.color == GREEN

    def is_barrier(self):
        return self.color == BLACK

    def is_start(self):
        return self.color == ORANGE

    def is_end(self):
        return self.color == TURQUOISE

    def reset(self):
        self.color = WHITE

    def make_closed(self):
        self.color = RED

    def make_open(self):
        self.color = GREEN

    def make_barrier(self):
        self.color = BLACK

    def make_start(self):
        self.color = ORANGE

    def make_end(self):
        self.color = TURQUOISE

    def make_path(self):
        self.color = PURPLE

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        self.neighbors = []
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier(): # DOWN
            self.neighbors.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier(): # UP
            self.neighbors.append(grid[self.row - 1][self.col])

        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier(): # RIGHT
            self.neighbors.append(grid[self.row][self.col + 1])

        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier(): # LEFT
            self.neighbors.append(grid[self.row][self.col - 1])

    def __lt__(self, other):
        return False


def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)


def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()


def algorithm(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))

    # dictionary to keep track of previous steps
    came_from = {}

    # initialize g_scores of every node to infinity
    g_score = {node: float("inf") for row in grid for node in row}

    # g_score of start node = 0
    g_score[start] = 0

    # initialize f_scores of every node to infinity
    f_score = {node: float("inf") for row in grid for node in row}

    # f_score of start node is the heuristic
    f_score[start] = h(start.get_pos(), end.get_pos())

    # keep track of items in/out of priority queue
    open_set_hash = {start}

    # run until open_set is empty
    while not open_set.empty():
        for event in pygame.event.get():    # exit loop, just in case
            if event.type == pygame.QUIT:
                pygame.quit()

        # pop the lowest value f_score in queue
        current = open_set.get()[2]

        # remove from hash, no duplicates
        open_set_hash.remove(current)

        # if we reached the end node, reconstruct path
        if current == end:
            reconstruct_path(came_from, end, draw)
            end.make_end()
            start.make_start()
            return True

        for neighbor in current.neighbors:
            # moving one node over can only increase g_score by 1
            temp_g_score = g_score[current] + 1

            # if we found a better way to the end node, update values
            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score

                # f_score is sum of g_score and heuristic
                f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())

                # if neighbor is not in the queue
                if neighbor not in open_set_hash:
                    count += 1

                    # put neighbor in to consider for path
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)

                    # change color of neighbor to green, in open set
                    neighbor.make_open()

        draw()

        if current != start:
            # change color of current node to red, remove from open set
            current.make_closed()

    return False


def make_grid(rows, width):
    grid = []
    gap = width // rows

    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i, j, gap, rows)
            grid[i].append(node)

    return grid


def ran_maze(grid, rows, width):

    for row in grid:
        for node in row:
            num = random.randint(1,10)
            if num < 4 and not node.is_start() and not node.is_end():
                node.make_barrier()

    pygame.display.update()


def draw_grid(win, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0,i * gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))


def draw(win, grid, rows, width):
    win.fill(WHITE)

    for row in grid:
        for node in row:
            node.draw(win)

    draw_grid(win, rows, width)
    pygame.display.update()


def get_clicked_pos(pos, rows, width):
    gap = width // rows
    y, x = pos

    row = y // gap
    col = x // gap
    return row, col


def main(win, width):
    ROWS = 50
    grid = make_grid(ROWS, width)

    start = None
    end = None

    run = True
    started = False

    while run:
        draw(win, grid, ROWS, width)
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                run = False

            if started:
                continue

            # draw barriers
            if pygame.mouse.get_pressed()[0]:  # 'LMB'
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                node = grid[row][col]

                if not start and node != end:
                    start = node
                    start.make_start()

                elif not end and node != start:
                    end = node
                    node.make_end()

                elif node != end and node != start:
                    node.make_barrier()

            # reset node
            elif pygame.mouse.get_pressed()[2]:  # 'RMB'
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                node = grid[row][col]
                node.reset()

                if node == start:
                    start = None

                if node == end:
                    end = None

            # start A* algorithm
            if event.type == pygame.KEYDOWN:  # 'space'
                if event.key == pygame.K_SPACE and not started:
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)

                    algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)

                if event.key == pygame.K_c: # 'space' then 'c'
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)

            # generate random barrier
            if event.type == pygame.KEYDOWN:  # 'r'
                if event.key == pygame.K_r:
                    ran_maze(grid, ROWS, width)

    pygame.quit()


main(WIN, WIDTH)

