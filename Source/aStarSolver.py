import heapq
# import modelCar as Car # Đảm bảo file modelCar.py chứa class Car nằm cùng thư mục
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
        if r_idx == 2: # Hàng 2 là hàng thoát cho xe 'r'
            print(" <--- EXIT")
        else:
            print()
    print("-" * (len(board[0]) * 2 + 1))

def is_GState(state, target_car='r', exit_col=5):
    """Kiểm tra xem trạng thái hiện tại có phải là trạng thái mục tiêu không."""
    for car in state:
        if car.name == target_car:
            # Xe mục tiêu nằm ngang và phần cuối của nó đã ở cột thoát
            if car.horizontal and car.col + car.length - 1 == exit_col:
                return True
    return False

def SStateList(state):
    """Tạo danh sách các trạng thái kế tiếp từ trạng thái hiện tại."""
    SState = []
    board = stateToBoard(state)
    r, c = len(board), len(board[0])

    for i, car in enumerate(state):
        # Tạo một bản sao của trạng thái để sửa đổi
        current_state_list = list(state)

        # Di chuyển xe ngang (horizontal)
        if car.horizontal:
            # Di chuyển sang phải
            for move in range(1, c - (car.col + car.length) + 1):
                # Kiểm tra ô kế tiếp có trống không
                if car.col + car.length + move - 1 < c and board[car.row][car.col + car.length + move - 1] == '.':
                    Ncar = Car(car.name, car.row, car.col + move, car.length, car.horizontal, car.color)
                    Nstate = list(current_state_list)
                    Nstate[i] = Ncar
                    SState.append(tuple(car_to_tuple(c_obj) for c_obj in Nstate))
                else:
                    break # Không thể di chuyển tiếp vì bị chặn

            # Di chuyển sang trái
            for move in range(1, car.col + 1):
                # Kiểm tra ô kế tiếp có trống không
                if car.col - move >= 0 and board[car.row][car.col - move] == '.':
                    Ncar = Car(car.name, car.row, car.col - move, car.length, car.horizontal, car.color)
                    Nstate = list(current_state_list)
                    Nstate[i] = Ncar
                    SState.append(tuple(car_to_tuple(c_obj) for c_obj in Nstate))
                else:
                    break # Không thể di chuyển tiếp vì bị chặn

        # Di chuyển xe dọc (vertical)
        else:
            # Di chuyển xuống dưới
            for move in range(1, r - (car.row + car.length) + 1):
                # Kiểm tra ô kế tiếp có trống không
                if car.row + car.length + move - 1 < r and board[car.row + car.length + move - 1][car.col] == '.':
                    Ncar = Car(car.name, car.row + move, car.col, car.length, car.horizontal, car.color)
                    Nstate = list(current_state_list)
                    Nstate[i] = Ncar
                    SState.append(tuple(car_to_tuple(c_obj) for c_obj in Nstate))
                else:
                    break # Không thể di chuyển tiếp vì bị chặn

            # Di chuyển lên trên
            for move in range(1, car.row + 1):
                # Kiểm tra ô kế tiếp có trống không
                if car.row - move >= 0 and board[car.row - move][car.col] == '.':
                    Ncar = Car(car.name, car.row - move, car.col, car.length, car.horizontal, car.color)
                    Nstate = list(current_state_list)
                    Nstate[i] = Ncar
                    SState.append(tuple(car_to_tuple(c_obj) for c_obj in Nstate))
                else:
                    break # Không thể di chuyển tiếp vì bị chặn
    return list(set(SState)) # Trả về danh sách các tuple trạng thái duy nhất

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
    prior = [] # Priority queue: (f_score, g_score, state_tuple, path)
    gList = {} # gList[state_tuple] = g_score

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
    # Bỏ qua bước 0 vì đó là trạng thái ban đầu, không phải một hành động
    for i, (action, state_tuple) in enumerate(solution_path_with_states):
        if action is None: # Đây là trạng thái ban đầu
            # print(f"Bước {i}: Trạng thái ban đầu") # Có thể bỏ qua dòng này hoặc chỉ in một lần
            continue # Bỏ qua để chỉ in các bước di chuyển

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


# --- Ví dụ sử dụng ---
def main():
    initial_board = [
        ['A', 'D', 'B', '.', 'C', 'C'],
        ['A', 'D', 'E', '.', 'F', 'G'],
        ['r', 'r', 'J', '.', 'F', 'G'],
        ['H', 'I', 'J', '.', 'K', 'K'],
        ['H', 'I', 'J', '.', 'L', 'L'],
        ['.', '.', 'M', 'M', '.', '.']
    ]
    print("Initial board: ")
    print_board(initial_board)

    initial_cars = get_cars(initial_board)

    solution = None
    method = 'a_star'
    if method == 'a_star':
        solution = A_Star(initial_cars)

    if solution:
        print("Solution found using", method.upper())
        show_solution(solution)
    else:
        print("No solution found.")

if __name__ == '__main__':
    main()
