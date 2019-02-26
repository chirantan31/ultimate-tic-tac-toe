import numpy as np
import itertools
import queue as q


class Shape():
    def __init__(self, figure):

        self.figure = figure
        self.height = len(self.figure)
        self.width = len(self.figure[0])
        #finds first index
        self.offset = next((i for i, x in enumerate(self.figure[0]) if x), None)
        self.zeros = sum(e.count(0) for e in self.figure)
        self.dictionary = self.generate_hashes()
        self.coords = self.generate_coords()


    #generates the possible coordinates that the pent will span 
    def generate_coords(self):
        coords = []
        for i in range(self.height):
            for j in range(self.width):
                if self.figure[i][j]:
                    coords.append((i, j))

        return(tuple(coords))

    #reflects the pent
    def reflection(self):
        new_figure = self.figure[::-1]
        return Shape(new_figure)


    #rotates the pent
    def rot90(self):
        new_figure = []
        for j in range(self.width):
            new_row = []
            for i in range(self.height - 1, -1, -1):
                new_row.append(self.figure[i][j])
            new_figure.append(new_row)

        return Shape(new_figure)

    #generates the dictionary that stores all the possible arrangements of the pents
    def generate_hashes(self):
        rows = []
        for row in self.figure:
            rows.append(','.join(map(str, row)))
        return ' '.join(rows)

    #tried using with np array but its too slow so used lists instead

    # def rot90(self):
    #     return Shape(np.rot90(self.figure))

    # def generate_hashes(self):
    #     rows = np.array([])
    #     for row in self.figure:
    #         np.append(row, rows)
    #     return rows


def solve(board, pents, app=None):
    print(board)

    width = len(board[0])
    height = len(board)

    print('height', height)
    print('width', width)


    #CREATE EMPTY BOARD

    blank_board = np.zeros((height,width))

    for i in range(height):
        for j in range(width):
            if board[i][j] == 1.0:
                blank_board[i][j] = 0
            else:
                blank_board[i][j] = -1

    pents_list = []
    for pent in pents:
        pents_list.append(pent.tolist())

    figures_dict = generate_dict(pents_list)
    final_shape_dict = {}
    result_board = solution_executor(blank_board, figures_dict, final_shape_dict)
    final_board = np.array(result_board)
    
    my_set = calc_coordinates(final_board)
    solve_list = []
    i = 1

    for pent in pents:
        solve_list.append((np.array(final_shape_dict[i]), my_set[i]))
        i+=1

    if app is not None:
        app.draw_solution_and_sleep(blank_board, 1)
    return solve_list

def calc_coordinates(board):
    my_set = {}
    for y in range(0, len(board[0])):
        for x in range(0, len(board)):
            if  board[x,y] not in my_set:
                my_set[board[x,y]] = (x,y)
            else:
                (oldx,oldy) = my_set[board[x,y]]
                if (oldx > x):
                    my_set[board[x,y]] = (x,oldy)
                if (oldy > y):
                     my_set[board[x,y]] = (oldx, y)
    return my_set

def solution_executor(board, my_dict, final_shape_dict):
    if not my_dict:
        return board

    x, y = get_next_spot(board)
    for pent_id, pent_list in my_dict.items():
        #sorted_pent_list = sort_pent_list(pent_list)
        for pent in pent_list:
            placed_board = place_pent(board, pent, pent_id, final_shape_dict, x=x-pent.offset, y=y)

            if placed_board is None:
                continue
            if not forward_check(np.array(placed_board), np.count_nonzero(pent.figure)):
                continue
            remaining_pents = dict(my_dict)
            del remaining_pents[pent_id]
            new_board = solution_executor(placed_board, remaining_pents, final_shape_dict)
            if new_board:
                return new_board

#sorts for most constraining value
def sort_pent_list(pent_list):
    sorted_list = []
    queue = q.PriorityQueue()
    for pent in pent_list:
        queue.put(pent.zeros, pent)

    while not queue.empty():
        item = queue.get()
        sorted_list.append(item)
    return sorted_list

def get_most_constraining(pent_list):
    most_constraining = None
    most_zeros = -1
    for pent in pent_list:
        cur_zero = sum(e.count(0) for e in pent.figure)
        if cur_zero > most_zeros:
            most_zeros = cur_zero
            most_constraining = pent
    return most_constraining

def forward_check(b, spaces):
    """
    Check if empty board areas are multiples of 5.
    Returns False if A % (# of ominos) != for any empty area A,
    otherwise True.
    """
    for i in range(0, b.shape[0]):
        for j in range(0, b.shape[1]):
            c = board_crawl(b, i, j, c=0)
            if (c % spaces) != 0:
                b[np.where(b == -1)] = 0
                return False
    return True


def board_crawl(b, i, j, c):
    """
    Counts squares in empty (0) areas using
    a recursive algorithm.
    """
    if i >= b.shape[0] or j >= b.shape[1]:
        return c
    if b[i, j] != 0:
        return c
    c += 1
    b[i, j] = -1
    c = board_crawl(b, i+1,   j, c)
    c = board_crawl(b, i, j+1, c)
    c = board_crawl(b, i-1,   j, c)
    c = board_crawl(b, i,   j-1, c)
    return c


def place_pent(board, shape, pent_id, final_shape_dict, x=0, y=0):
    width = len(board[0])
    height = len(board) 
    new_board = list(map(list, board))
    if x < 0 or y < 0 or x + shape.width > width or y + shape.height > height:
        return

    for i, j in shape.coords:
        if new_board[y+i][x+j] != 0:
            return
        new_board[y+i][x+j] = pent_id
    final_shape_dict[pent_id] = shape.figure

    return new_board

def get_next_spot(board):
    width = len(board[0])
    height = len(board)
    for i in range(height):
        for j in range(width):
            if board[i][j] == 0:
                return j, i

def generate_arrangements(shape):
    """
    Generates arrangements of the reflections and rotations and adds them to the dict
    """
    pent = Shape(shape)
    result, dicts = [pent], [pent.dictionary]

    reflected_pent = pent.reflection()
    if reflected_pent.dictionary not in dicts:
        result.append(reflected_pent)
        dicts.append(reflected_pent.dictionary)

    for i in range(3):
        #pent
        pent = pent.rot90()
        reflected_pent = reflected_pent.rot90()

        for figure in [pent, reflected_pent]:
            if figure.dictionary not in dicts:
                result.append(figure)
                dicts.append(figure.dictionary)


    return result

def generate_dict(figures_raw_list):
    result_dict = {}
    for index, figure_raw in enumerate(figures_raw_list):
        result_dict[index + 1] = generate_arrangements(figure_raw)

    return result_dict


"""

code when trying the exactr cover problem

def all_orientations(A, i):
    if i == 0:
        yield A
        return
        
    seen = set()
    for A in (A, A.T):
        for A in (A, np.fliplr(A)):
            for A in (A, np.flipud(A)):
                s = str(A)
                if not s in seen:
                    yield A
                    seen.add(s)


def all_positions(A, i):
    for A in all_orientations(A, i):
        rows, cols = A.shape
        for i in range(9 - rows):
            for j in range(9 - cols):
                M = np.zeros((8, 8), dtype='int')
                M[i:i+rows, j:j+cols] = A
                if M[0,0] == M[0,7] == M[7,0] == M[7,7] == 0:
                    yield np.delete(M.reshape(64), [0, 7, 56, 63])

def exact_cover(A):
    if A.shape[1] == 0:
        yield []                                    
    else:
        c = A.sum(axis=0).argmin()
        for r in A.index[A[c] == 1]:                
            B = A

            for j in A.columns[A.loc[r] == 1]:
                B = B[B[j] == 0]
                del B[j]              
              
            for partial_solution in exact_cover(B):
                yield [r] + partial_solution      


"""
