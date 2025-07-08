# DFS_solver.py
from modelCar import Car

BOARD_SIZE = 6


def print_board(board):
    for row in board:
        print(' '.join(row))
    print()


def get_cars(board):
    cars = []
    visited = set()
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            cell = board[r][c]
            if cell == '.' or (r, c) in visited:
                continue
            # determine orientation and length
            length = 1
            if c + 1 < BOARD_SIZE and board[r][c + 1] == cell:
                # horizontal
                length = 2
                if c + 2 < BOARD_SIZE and board[r][c + 2] == cell:
                    length = 3
                for i in range(length):
                    visited.add((r, c + i))
                cars.append(Car(cell, r, c, length, True, None))
            elif r + 1 < BOARD_SIZE and board[r + 1][c] == cell:
                # vertical
                length = 2
                if r + 2 < BOARD_SIZE and board[r + 2][c] == cell:
                    length = 3
                for i in range(length):
                    visited.add((r + i, c))
                cars.append(Car(cell, r, c, length, False, None))
    return cars


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
    base = place_cars(cars)
    for idx, car in enumerate(cars):
        # horizontal moves
        if car.horizontal:
            # move left
            if car.col > 0 and base[car.row][car.col - 1] == '.':
                new = clone_cars(cars)
                new[idx].col -= 1
                moves.append((car.name, 'Left', new))
            # move right
            if car.col + car.length < BOARD_SIZE and base[car.row][car.col + car.length] == '.':
                new = clone_cars(cars)
                new[idx].col += 1
                moves.append((car.name, 'Right', new))
        else:
            # vertical moves
            if car.row > 0 and base[car.row - 1][car.col] == '.':
                new = clone_cars(cars)
                new[idx].row -= 1
                moves.append((car.name, 'Up', new))
            if car.row + car.length < BOARD_SIZE and base[car.row + car.length][car.col] == '.':
                new = clone_cars(cars)
                new[idx].row += 1
                moves.append((car.name, 'Down', new))
    return moves


def is_goal(cars):
    # check if the red car (name 'r' or 'R') has exited the board on the right
    for car in cars:
        if car.name.lower() == 'r' and car.col + car.length == BOARD_SIZE:
            return True
    return False


def serialize(cars):
    # unique representation for visited checking
    return tuple((c.name, c.row, c.col) for c in sorted(cars, key=lambda x: x.name))


def dfs_solver(cars, max_depth=10000):
    stack = [(cars, [])]
    visited = set()

    while stack:
        state, path = stack.pop()
        key = serialize(state)
        if key in visited or len(path) > max_depth:
            continue
        visited.add(key)

        if is_goal(state):
            return path

        for name, direction, next_cars in get_possible_moves(state):
            stack.append((next_cars, path + [(name, direction)]))
    return None


def show_solution(moves, initial_board):
    cars = get_cars(initial_board)
    board = place_cars(cars)
    print_board(board)
    for i, (name, direction) in enumerate(moves, 1):
        print(f"Step {i}: Move {name} {direction}")
        # update cars
        for car in cars:
            if car.name == name:
                if direction == 'Left':
                    car.col -= 1
                elif direction == 'Right':
                    car.col += 1
                elif direction == 'Up':
                    car.row -= 1
                elif direction == 'Down':
                    car.row += 1
                break
        board = place_cars(cars)
        print_board(board)

