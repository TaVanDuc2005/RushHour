import heapq
from modelCar import Car

BOARD_SIZE = 6
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

def car_to_tuple(car):
    """Chuyển đổi đối tượng Car thành một tuple để dễ dàng hash và lưu trữ."""
    return (car.name, car.row, car.col, car.length, car.horizontal, car.color)

def tuple_to_cars(state_tuple):
    """Chuyển đổi một tuple trạng thái (chứa dữ liệu xe dưới dạng tuple) thành danh sách các đối tượng Car."""
    return [Car(*car_data) for car_data in state_tuple]

def stateToBoard(state, r=6, c=6):
    """Chuyển đổi danh sách các đối tượng Car thành biểu diễn bảng 2D."""
    board = [['.' for _ in range(c)] for _ in range(r)]
    for car in state:
        if car.horizontal:
            for i in range(car.length):
                if 0 <= car.col + i < c and 0 <= car.row < r:
                    board[car.row][car.col + i] = car.name
        else:
            for i in range(car.length):
                if 0 <= car.row + i < r and 0 <= car.col < c:
                    board[car.row + i][car.col] = car.name
    return board

def print_board(board):
    """In trạng thái bảng một cách trực quan. (Giữ lại hàm này nhưng không gọi trong show_solution)"""
    print("-" * (len(board[0]) * 2 + 1))
    for r_idx, row in enumerate(board):
        print("|", end="")
        for c_idx, cell in enumerate(row):
            print(cell, end="|")
        if r_idx == 2:
            print(" <--- EXIT")
        else:
            print()
    print("-" * (len(board[0]) * 2 + 1))

def is_GState(state, target_car='r', exit_col=5):
    """Kiểm tra xem trạng thái hiện tại có phải là trạng thái mục tiêu không."""
    for car in state:
        if car.name == target_car:
            if car.horizontal and car.col + car.length - 1 == exit_col:
                return True
    return False

def SStateList(state):
    """Tạo danh sách các trạng thái kế tiếp từ trạng thái hiện tại (mỗi lần di chuyển 1 ô)."""
    SState = []
    r, c = BOARD_SIZE, BOARD_SIZE  

    for i, car in enumerate(state):
        current_state_list = list(state)

        if car.horizontal and car.col + car.length < c:
            board = stateToBoard(state)
            if board[car.row][car.col + car.length] == '.':
                Ncar = Car(car.name, car.row, car.col + 1, car.length, car.horizontal, car.color)
                Nstate = list(current_state_list)
                Nstate[i] = Ncar
                SState.append(tuple(car_to_tuple(c_obj) for c_obj in Nstate))

        if car.horizontal and car.col - 1 >= 0:
            board = stateToBoard(state)
            if board[car.row][car.col - 1] == '.':
                Ncar = Car(car.name, car.row, car.col - 1, car.length, car.horizontal, car.color)
                Nstate = list(current_state_list)
                Nstate[i] = Ncar
                SState.append(tuple(car_to_tuple(c_obj) for c_obj in Nstate))

        if not car.horizontal and car.row + car.length < r:
            board = stateToBoard(state)
            if board[car.row + car.length][car.col] == '.':
                Ncar = Car(car.name, car.row + 1, car.col, car.length, car.horizontal, car.color)
                Nstate = list(current_state_list)
                Nstate[i] = Ncar
                SState.append(tuple(car_to_tuple(c_obj) for c_obj in Nstate))

        if not car.horizontal and car.row - 1 >= 0:
            board = stateToBoard(state)
            if board[car.row - 1][car.col] == '.':
                Ncar = Car(car.name, car.row - 1, car.col, car.length, car.horizontal, car.color)
                Nstate = list(current_state_list)
                Nstate[i] = Ncar
                SState.append(tuple(car_to_tuple(c_obj) for c_obj in Nstate))

    return list(set(SState))


def get_h(state_tuple, exit_col=5):
    """Tính toán hàm heuristic (số xe chặn đường + khoảng trống đến lối thoát)."""
    curStateCar = tuple_to_cars(state_tuple)

    target_car = None
    for car in curStateCar:
        if car.name == 'r':
            target_car = car
            break

    if target_car is None:
        return float('inf')

    exit_space = (exit_col + 1) - (target_car.col + target_car.length)
    if exit_space < 0:
        exit_space = 0

    board = stateToBoard(curStateCar)
    block_cars = 0
    blockSeenList = set()

    for c_idx in range(target_car.col + target_car.length, exit_col + 1):
        if c_idx < len(board[0]):
            blocker = board[target_car.row][c_idx]
            if blocker != '.' and blocker != 'r' and blocker not in blockSeenList:
                block_cars += 1
                blockSeenList.add(blocker)

    return exit_space + block_cars

def A_Star(init_state_list):
    """Thực hiện thuật toán tìm kiếm A* để giải bài toán Rush Hour."""
    prior = [] 
    gList = {} 

    init_state_tuple = tuple(car_to_tuple(car) for car in init_state_list)

    h = get_h(init_state_tuple)
    heapq.heappush(prior, (h, 0, init_state_tuple, [(None, init_state_tuple)]))
    gList[init_state_tuple] = 0

    while prior:
        f_score, g_score, state_tuple, path = heapq.heappop(prior)
        curStateCar = tuple_to_cars(state_tuple)

        if g_score > gList.get(state_tuple, float('inf')):
            continue

        if is_GState(curStateCar):
            return path

        for next_state_tuple in SStateList(curStateCar):
            cost = 1
            new_g = g_score + cost

            if new_g < gList.get(next_state_tuple, float('inf')):
                gList[next_state_tuple] = new_g
                new_h = get_h(next_state_tuple)
                new_f = new_g + new_h

                action = None
                prev_comp_state = tuple_to_cars(state_tuple)
                next_comp_state = tuple_to_cars(next_state_tuple)

                for i in range(len(prev_comp_state)):
                    prev_car = prev_comp_state[i]
                    next_car = next_comp_state[i]

                    if not (prev_car.name == next_car.name and
                            prev_car.row == next_car.row and
                            prev_car.col == next_car.col and
                            prev_car.length == next_car.length and
                            prev_car.horizontal == next_car.horizontal and
                            prev_car.color == next_car.color):

                        moved_car_name = prev_car.name
                        prev_row, prev_col = prev_car.row, prev_car.col
                        new_row, new_col = next_car.row, next_car.col

                        direction = ""
                        if new_row > prev_row:
                            direction = 'xuống'
                        elif new_row < prev_row:
                            direction = 'lên'
                        elif new_col > prev_col:
                            direction = 'sang phải'
                        elif new_col < prev_col:
                            direction = 'sang trái'
                        
                        action = (moved_car_name, direction, prev_row, prev_col, new_row, new_col)
                        break

                heapq.heappush(prior, (new_f, new_g, next_state_tuple, path + [(action, next_state_tuple)]))

    return None

def show_solution(solution_path_with_states):
    """Hiển thị các bước giải pháp dưới dạng hướng dẫn, không in bảng."""
    if not solution_path_with_states:
        print("Không có lời giải để hiển thị.")
        return

    print("--- Lời giải đã tìm thấy ---")
    for i, (action, state_tuple) in enumerate(solution_path_with_states):
        if action is None: 
            continue 

        name, dirc, prev_r, prev_c, new_r, new_c = action
        print(f"Bước {i}: Di chuyển xe '{name}' {dirc} từ ({prev_r}, {prev_c}) đến ({new_r}, {new_c})")
    
    print("\n--- Hoàn thành lời giải ---")

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
                    visited.append([r, c + i])
                cars.append(Car(cell, r, c, length, True, None))

            elif r + 1 < BOARD_SIZE and board[r + 1][c] == cell:
                length = 2
                if r + 2 < BOARD_SIZE and board[r + 2][c] == cell:
                    length = 3
                for i in range(length):
                    visited.append([r + i, c])
                cars.append(Car(cell, r, c, length, False, None))

            else:
                visited.append([r, c])
                cars.append(Car(cell, r, c, 1, True, None))  
    return cars
def A_Star_solver(board):
    # print("Initial board: ")
    # print_board(board)
    initial_car=get_cars(board)
    solution = None
    method = 'a_star'
    if method == 'a_star':
        solution = A_Star(initial_car)

    if solution:
        print("Solution found using", method.upper())
        print("\n Total step: ", len(solution)-1)

        show_solution(solution)
    else:
        print("No solution found.")

# # --- Ví dụ sử dụng ---
# def main():
#     initial_board = [
#     ['.', '.', 'A', 'A', 'B', 'B'],
#     ['.', '.', '.', '.', 'C', '.'],
#     ['r', 'r', 'D', 'D', 'C', '.'],
#     ['E', 'E', 'F', 'F', '.', '.'],
#     ['G', 'G', '.', '.', '.', '.'],
#     ['H', 'H', '.', '.', '.', '.']
# ]



#     print("Initial board: ")
#     print_board(initial_board)

#     initial_cars = get_cars(initial_board)
#     for element in initial_cars :
#         print(element.name)
#     solution = None
#     method = 'a_star'
#     if method == 'a_star':
#         solution = A_Star(initial_cars)

#     if solution:
#         print("Solution found using", method.upper())
#         print("\n Total step: ", len(solution)-1)

#         show_solution(solution)
#     else:
#         print("No solution found.")

# if __name__ == '__main__':
#     main()



