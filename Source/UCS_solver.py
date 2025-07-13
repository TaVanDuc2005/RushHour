import heapq
import copy
from itertools import count

def serialize_state(cars):
    return tuple(sorted((car.name, car.row, car.col) for car in cars))

def is_goal_state(cars):
    for car in cars:
        if car.name.lower() == 'r':
            return car.row == 2 and car.col + car.length == 6
    return False

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


def get_successors(state):
    successors = []

    for i, car in enumerate(state):
        if car.horizontal:
            new_col = car.col - 1
            if new_col >= 0 and not is_blocked(car, car.row, new_col, state):
                new_state = copy.deepcopy(state)
                new_state[i].col = new_col
                successors.append((new_state, car.length))

            new_col = car.col + 1
            if new_col + car.length <= 6 and not is_blocked(car, car.row, new_col, state):
                new_state = copy.deepcopy(state)
                new_state[i].col = new_col
                successors.append((new_state, car.length))
        else:
            new_row = car.row - 1
            if new_row >= 0 and not is_blocked(car, new_row, car.col, state):
                new_state = copy.deepcopy(state)
                new_state[i].row = new_row
                successors.append((new_state, car.length))

            new_row = car.row + 1
            if new_row + car.length <= 6 and not is_blocked(car, new_row, car.col, state):
                new_state = copy.deepcopy(state)
                new_state[i].row = new_row
                successors.append((new_state, car.length))

    return successors


# Uniform-Cost Search solver
def ucs_solver(initial_state):
    frontier = []
    visited = set()
    counter = count()

    heapq.heappush(frontier, (0, next(counter), initial_state, [copy.deepcopy(initial_state)]))

    while frontier:
        cost, _, current_state, path = heapq.heappop(frontier)
        state_id = serialize_state(current_state)

        if state_id in visited:
            continue
        visited.add(state_id)

        if is_goal_state(current_state):
            print("Goal reached!")
            print("Steps:", len(path) - 1)
            print("Total cost:", cost)
            return path

        for next_state, step_cost in get_successors(current_state):
            next_id = serialize_state(next_state)
            if next_id not in visited:
                heapq.heappush(frontier, (
                    cost + step_cost,
                    next(counter),
                    next_state,
                    path + [copy.deepcopy(next_state)]
                ))

    print("No solution found.")
    return None
