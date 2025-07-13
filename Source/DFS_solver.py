# DFS_solver.py
from collections import deque
import copy

def is_goal(cars):
    red_car = next((car for car in cars if car.name.lower() == 'r'), None)
    return red_car is not None and red_car.row == 2 and red_car.col + red_car.length == 6

def get_state_key(cars):
    return tuple((car.name, car.row, car.col) for car in cars)

def is_blocked(moving_car, target_row, target_col, cars):
    for other in cars:
        if other == moving_car:
            continue
        if moving_car.horizontal:
            if other.horizontal:
                if other.row != moving_car.row:
                    continue
                if not (target_col + moving_car.length <= other.col or
                        target_col >= other.col + other.length):
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
                if not (target_row + moving_car.length <= other.row or
                        target_row >= other.row + other.length):
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
            # move left by 1 using for loop
            for step in range(1, car.col + 1):
                new_col = car.col - step
                if is_blocked(car, car.row, new_col, state):
                    break
                new_state = copy.deepcopy(state)
                new_state[idx].col = new_col
                moves.append(new_state)
                break  # only 1 square per move
            # move right by 1 using for loop
            for step in range(1, 6 - car.col - car.length + 1):
                new_col = car.col + step
                if is_blocked(car, car.row, new_col, state):
                    break
                new_state = copy.deepcopy(state)
                new_state[idx].col = new_col
                moves.append(new_state)
                break
        else:
            # move up by 1
            for step in range(1, car.row + 1):
                new_row = car.row - step
                if is_blocked(car, new_row, car.col, state):
                    break
                new_state = copy.deepcopy(state)
                new_state[idx].row = new_row
                moves.append(new_state)
                break
            # move down by 1
            for step in range(1, 6 - car.row - car.length + 1):
                new_row = car.row + step
                if is_blocked(car, new_row, car.col, state):
                    break
                new_state = copy.deepcopy(state)
                new_state[idx].row = new_row
                moves.append(new_state)
                break
    return moves


def dfs_solver(initial_cars):
    visited = set()
    stack = deque()
    stack.append((copy.deepcopy(initial_cars), []))
    visited.add(get_state_key(initial_cars))

    nodes = 0

    while stack:
        current_state, path = stack.pop()
        nodes += 1

        if is_goal(current_state):
            print(f"DFS has expanded {nodes} nodes.")
            return path + [copy.deepcopy(current_state)]

        for next_state in generate_moves(current_state):
            key = get_state_key(next_state)
            if key not in visited:
                visited.add(key)
                stack.append((next_state, path + [copy.deepcopy(current_state)]))

    return []
