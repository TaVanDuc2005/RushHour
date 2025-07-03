from modelCar import Car

BOARD_SIZE = 6

def print_board(board):
    for row in board:
        print(' '.join(row))
    print()

def get_cars(board):
    cars = []
    visited = []
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            cell = board[r][c]
            if cell == '.' or [r, c] in visited:
                continue
            if c + 1 < BOARD_SIZE and board[r][c + 1] == cell:
                length = 2
                if c + 2 < BOARD_SIZE and board[r][c + 2] == cell:
                        length = 3
                for i in range(length):
                    visited.append([r, c + 1])
                cars.append(Car(cell, r, c, length, True, None))
            elif r + 1 < BOARD_SIZE and board[r + 1][c] == cell:
                length = 2
                if r + 2 < BOARD_SIZE and board[r + 2][c] == cell:
                    length = 3
                for i in range(length):
                    visited.append([r + i, c])
                cars.append(Car(cell, r, c, length, False, None))
    return cars

def clone_board(board):
    return [row[:] for row in board]

def clone_cars(cars):
    return [Car(c.name, c.row, c.col, c.length, c.horizontal, c.color) for c in cars]

def place_cars(cars):
    board = [['.' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    for car in cars:
        for i in range(car.length):
            if car.horizontal:
                board[car.row][car.col + i] = car.name
            else:
                board[car.row + i][car.col] = car.name
    return board

def get_possible_moves(cars):
    moves = []
    for idx in range(len(cars)):
        car = cars[idx]
        if car.horizontal:
            if car.col > 0:
                board = place_cars(cars)
                if board[car.row][car.col - 1] == '.':
                    new_cars = clone_cars(cars)
                    new_cars[idx].col -= 1
                    moves.append((car.name, ' Left', new_cars))
            if car.col + car.length < BOARD_SIZE:
                board = place_cars(cars)
                if board[car.row][car.col + car.length] == '.':
                    new_cars = clone_cars(cars)
                    new_cars[idx].col += 1
                    moves.append((car.name, 'Right', new_cars))
        else:
            if car.row > 0:
                board = place_cars(cars)
                if board[car.row - 1][car.col] == '.':
                    new_cars = clone_cars(cars)
                    new_cars[idx].row -= 1
                    moves.append((car.name, ' Up', new_cars))
            if car.row + car.length < BOARD_SIZE:
                board = place_cars(cars)
                if board[car.row + car.length][car.col] == '.':
                    new_cars = clone_cars(cars)
                    new_cars[idx].row += 1
                    moves.append((car.name, ' Down', new_cars))
    return moves

def is_goal(cars):
    for car in cars:
        if car.name == 'X' and car.col + car.length == BOARD_SIZE:
            return True
    return False

def serialize(cars):
    return [(c.name, c.row, c.col) for c in cars]

def dfs_solver(cars):
    stack = [(cars, [])]
    visited = []
    while stack:
        state, path = stack.pop()
        key = serialize(state)
        if key in visited:
            continue
        visited.append(key)

        if is_goal(state):
            return path + [(None, None, state)]

        for name, dirc, next_cars in get_possible_moves(state):
            move = (name, dirc, next_cars)
            stack.append((next_cars, path + [move]))
    return None

def show_solution(solution):
    for i in range(len(solution)):
        name, dirc, cars = solution[i]
        print("Step", i, end=": ")
        if name is None:
            print("Final state")
        else:
            print("Move", name, dirc)
        print_board(place_cars(cars))

'''
def main():
    initial_board = [
        ['.', '.', '.', '.', 'B', 'F'],
        ['A', 'A', 'I', 'E', 'B', 'F'],
        ['X', 'X', 'I', 'E', 'B', 'H'],
        ['.', '.', 'C', 'E', '.', 'H'],
        ['.', '.', 'C', 'D', 'D', 'H'],
        ['.', '.', '.', '.', '.', '.']
    ]
    print("Initial board: ")
    print_board(initial_board)

    initial_cars = get_cars(initial_board)

    solution = None
    method = 'dfs'
    if method == 'dfs':
        solution = dfs_solver(initial_cars)

    if solution:
        print("Solution found using", method.upper())
        show_solution(solution)
    else:
        print("No solution found.")

if __name__ == '__main__':
    main()
'''

