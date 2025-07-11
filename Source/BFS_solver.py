# bfs_solver.py
from collections import deque
import copy

def is_goal(cars):
    red_car = next((car for car in cars if car.name.lower() == 'r'), None)
    return red_car is not None and red_car.row == 2 and red_car.col + red_car.length == 6

def get_state_key(cars):
    return tuple((car.name, car.row, car.col) for car in sorted(cars, key=lambda c: c.name))

def is_blocked(moving_car, target_row, target_col, cars):
    for other in cars:
        if other == moving_car:
            continue
        if moving_car.horizontal:
            if other.horizontal:
                if other.row != moving_car.row:
                    continue
                if not (target_col + moving_car.length <= other.col or target_col >= other.col + other.length):
                    return True
            else:
                for i in range(moving_car.length):
                    if (other.col == target_col + i and
                        other.row <= moving_car.row < other.row + other.length):
                        return True
        else:
            if not other.horizontal:
                if other.col != moving_car.col:
                    continue
                if not (target_row + moving_car.length <= other.row or target_row >= other.row + other.length):
                    return True
            else:
                for i in range(moving_car.length):
                    if (other.row == target_row + i and
                        other.col <= moving_car.col < other.col + other.length):
                        return True
    return False

def generate_moves(state):
    moves = []
    for idx, car in enumerate(state):
        if car.horizontal:
            new_col = car.col - 1
            if new_col >= 0 and not is_blocked(car, car.row, new_col, state):
                new_state = copy.deepcopy(state)
                new_state[idx].col = new_col
                moves.append(new_state)
            new_col = car.col + 1
            if new_col + car.length <= 6 and not is_blocked(car, car.row, new_col, state):
                new_state = copy.deepcopy(state)
                new_state[idx].col = new_col
                moves.append(new_state)
        else:
            
            new_row = car.row - 1
            if new_row >= 0 and not is_blocked(car, new_row, car.col, state):
                new_state = copy.deepcopy(state)
                new_state[idx].row = new_row
                moves.append(new_state)
            new_row = car.row + 1
            if new_row + car.length <= 6 and not is_blocked(car, new_row, car.col, state):
                new_state = copy.deepcopy(state)
                new_state[idx].row = new_row
                moves.append(new_state)
    return moves


def bfs_solver(initial_cars):
    visited = set()
    queue = deque()
    queue.append((copy.deepcopy(initial_cars), []))
    visited.add(get_state_key(initial_cars))

    steps = 0

    while queue:
        current_state, path = queue.popleft()
        steps += 1


        if is_goal(current_state):
            print(f"BFS found solution in {steps} steps.")
            return path + [copy.deepcopy(current_state)]

        for next_state in generate_moves(current_state):
            key = get_state_key(next_state)
            if key not in visited:
                visited.add(key)
                queue.append((next_state, path + [copy.deepcopy(current_state)]))
    print(f"BFS completed in {steps} steps. No solution found.")
    return []
