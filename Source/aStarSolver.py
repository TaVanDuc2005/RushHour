import heapq
from modelCar import Car

BOARD_SIZE = 6

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


def is_GState(state, target_car='r', exit_col=5):
    """Kiểm tra xem trạng thái hiện tại có phải là trạng thái mục tiêu không."""
    for car in state:
        if car.name.lower() == target_car: 
            if car.horizontal and car.col + car.length - 1 == exit_col:
                return True
    return False

def SStateList(state):
    """Tạo danh sách các trạng thái kế tiếp từ trạng thái hiện tại (mỗi lần di chuyển 1 ô)."""
    SState = []
    r, c = BOARD_SIZE, BOARD_SIZE 

    # Chuyển trạng thái hiện tại sang dạng bảng để kiểm tra va chạm
    current_board = stateToBoard(state)

    for i, car in enumerate(state):
        # Tạo bản sao của danh sách xe để sửa đổi cho trạng thái kế tiếp
        current_state_list_copy = list(state) 

        # Di chuyển ngang
        if car.horizontal:
            # Di chuyển sang phải
            next_col_right = car.col + car.length
            if next_col_right < c and current_board[car.row][next_col_right] == '.':
                Ncar = Car(car.name, car.row, car.col + 1, car.length, car.horizontal, car.color)
                Nstate = list(current_state_list_copy)
                Nstate[i] = Ncar
                SState.append(tuple(car_to_tuple(c_obj) for c_obj in Nstate))

            # Di chuyển sang trái
            next_col_left = car.col - 1
            if next_col_left >= 0 and current_board[car.row][next_col_left] == '.':
                Ncar = Car(car.name, car.row, car.col - 1, car.length, car.horizontal, car.color)
                Nstate = list(current_state_list_copy)
                Nstate[i] = Ncar
                SState.append(tuple(car_to_tuple(c_obj) for c_obj in Nstate))
        # Di chuyển dọc
        else:
            # Di chuyển xuống
            next_row_down = car.row + car.length
            if next_row_down < r and current_board[next_row_down][car.col] == '.':
                Ncar = Car(car.name, car.row + 1, car.col, car.length, car.horizontal, car.color)
                Nstate = list(current_state_list_copy)
                Nstate[i] = Ncar
                SState.append(tuple(car_to_tuple(c_obj) for c_obj in Nstate))

            # Di chuyển lên
            next_row_up = car.row - 1
            if next_row_up >= 0 and current_board[next_row_up][car.col] == '.':
                Ncar = Car(car.name, car.row - 1, car.col, car.length, car.horizontal, car.color)
                Nstate = list(current_state_list_copy)
                Nstate[i] = Ncar
                SState.append(tuple(car_to_tuple(c_obj) for c_obj in Nstate))

    return list(set(SState))


def get_h(state_tuple, exit_col=5):
    """Tính toán hàm heuristic (số xe chặn đường + khoảng trống đến lối thoát)."""
    curStateCar = tuple_to_cars(state_tuple)

    target_car = None
    for car in curStateCar:
        if car.name.lower() == 'r': 
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
            if blocker != '.' and blocker.lower() != 'r' and blocker not in blockSeenList:
                block_cars += 1
                blockSeenList.add(blocker)

    return exit_space + block_cars
def A_Star(init_state_list):
    prior = []  
    gList = {}  

    steps_processed = 0
    
    init_state_tuple = tuple(car_to_tuple(car) for car in init_state_list)

    h = get_h(init_state_tuple)
    
    heapq.heappush(prior, (h, 0, init_state_tuple, [init_state_list])) 

    gList[init_state_tuple] = 0 

    while prior:
        f_score, g_score, state_tuple, path = heapq.heappop(prior)
        steps_processed += 1
        curStateCar = tuple_to_cars(state_tuple) 

        if g_score > gList.get(state_tuple, float('inf')):
            continue

        if is_GState(curStateCar):
            return path, steps_processed

        for next_state_tuple in SStateList(curStateCar):
            cost = 1 
            new_g = g_score + cost 
            steps_processed += 1

            if new_g < gList.get(next_state_tuple, float('inf')):
                gList[next_state_tuple] = new_g 
                new_h = get_h(next_state_tuple) 
                new_f = new_g + new_h 
                next_state_list = tuple_to_cars(next_state_tuple)
                
                heapq.heappush(prior, (new_f, new_g, next_state_tuple, path + [next_state_list]))
            


    return [], steps_processed


def A_Star_solver(initial_cars_list):
    solution, steps = A_Star(initial_cars_list)
    print(f"BFS completed in {steps} steps.")


    return solution






