import heapq
import copy
from itertools import count

def serialize_state(cars):
    """
    Chuyển trạng thái danh sách xe thành dạng tuple duy nhất có thể hash được.
    """
    return tuple(sorted((car.name, car.row, car.col) for car in cars))

def is_goal_state(cars):
    for car in cars:
        if car.name.lower() == 'r':
            return car.row == 2 and car.col + car.length == 6
    return False

def get_successors(state):
    successors = []

    for i, car in enumerate(state):
        if car.horizontal:
            new_col = car.col - 1
            if new_col >= 0:
                blocked = any(
                    other.row == car.row and not (
                        other.col + other.length <= new_col or other.col >= new_col + car.length
                    )
                    for j, other in enumerate(state) if j != i
                )
                if not blocked:
                    new_state = copy.deepcopy(state)
                    new_state[i].col = new_col
                    successors.append((new_state, 1))

            new_col = car.col + 1
            if new_col + car.length <= 6:
                blocked = any(
                    other.row == car.row and not (
                        other.col + other.length <= new_col or other.col >= new_col + car.length
                    )
                    for j, other in enumerate(state) if j != i
                )
                if not blocked:
                    new_state = copy.deepcopy(state)
                    new_state[i].col = new_col
                    successors.append((new_state, 1))

        else:
            new_row = car.row - 1
            if new_row >= 0:
                blocked = any(
                    other.col == car.col and not (
                        other.row + other.length <= new_row or other.row >= new_row + car.length
                    )
                    for j, other in enumerate(state) if j != i
                )
                if not blocked:
                    new_state = copy.deepcopy(state)
                    new_state[i].row = new_row
                    successors.append((new_state, 1))

            # Xuống 1 ô
            new_row = car.row + 1
            if new_row + car.length <= 6:
                blocked = any(
                    other.col == car.col and not (
                        other.row + other.length <= new_row or other.row >= new_row + car.length
                    )
                    for j, other in enumerate(state) if j != i
                )
                if not blocked:
                    new_state = copy.deepcopy(state)
                    new_state[i].row = new_row
                    successors.append((new_state, 1))

    return successors


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

    return None
