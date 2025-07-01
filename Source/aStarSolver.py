import heapq
def stateToBoard(state,r=6,c=6):
    board=[['.' for _ in range(c)] for _ in range(r)]
    for name, row, col, length, horizontal, color in state:
        if horizontal:
            for i in range(length):
                board[row][col+i]=name
        else:
            for i in range(length):
                board[row+i][col]=name
    return board

def is_GState(state, target_car='r', exit=5):
    for name, row, col, length, horizontal, color in state:
        if name == target_car:
            if horizontal and col + length -1 == exit:
                return True    
    return False

def SStateList(state):
    SState=[]
    board= stateToBoard(state)
    r,c=len(board),len(board[0])

    for i,(name, row, col, length, horizontal, color) in enumerate(state):
        curCar=list(list(list(car) for car in state))
        if horizontal:
            for move in range(1, c - (col + length) + 1 ):
                if row + length + move - 1 < c and board[row][col + length + move -1] == '.':
                    Npos=list(curCar[i])
                    Npos[3]=col + move
                    Ncar=list(curCar)
                    Ncar[i]=tuple(Npos)
                    SState.append(tuple(Ncar))
                else:
                    break
            
            for move in range(1,col + 1):
                if col - move >=0 and board[row][col - move] == '.':
                    Npos= list(curCar[i])
                    Npos[3]= col - move
                    Ncar= list(curCar)
                    Ncar[i]=tuple(Npos)
                    SState.append(tuple(Ncar))
                else:
                    break

        else:
            for move in range(1, r - (row + length) +1):
                if row + length + move -1 < r and board[row + length + move - 1][col]=='.':
                    Npos = list(curCar[i])
                    Npos[2] = row + move
                    Ncar = list(curCar)
                    Ncar[i]=tuple(Npos)
                    SState.append(tuple(Ncar))
                else:
                    break

            for move in range(1, row + 1):
                if row - move >= 0 and board[row - move][col] == '.':
                    Npos= list(curCar[i])
                    Npos[2]= row - move
                    Ncar = list(curCar)
                    Ncar[i]= tuple(Npos)
                    SState.append(tuple(Ncar))
                else: 
                    break
    return list(set(SState))


def get_h(state, exit_col):
    target_car= None
    for car in state:
        if car[0] == 'r':
            target_car = car
            break
    if target_car is None:
        return float('inf')
    
    _, length, horizontal, row, col = target_car

    if horizontal and col + length - 1 == exit_col:
        return 0
    
    board = stateToBoard(state)
    block_cars = 0

    for c in range(col + length, exit_col + 1):
        if c < len(board[0]):
            if board[row][c] != '.' and board[row][c] != 'r':
                block_cars += 1

    blockSeenList = set()
    for c in range(col + length, exit_col + 1):
        if c < len(board[0]):
            blocker=board[row][c]
            if blocker != '.' and blocker != 'r' and blocker not in blockSeenList:
                block_cars += 1
                blockSeenList.add(blocker)

    return block_cars

def A_Star(init_state):
    prior=[]

    gList={}

    h = get_h(init_state)
    heapq.heappush(prior, (h, 0, init_state, []))
    gList[init_state] = 0

    while prior:
        f_score, g_score, state, path= heapq.heappop(prior)
        if g_score > gList.get(state,float('inf')):
            continue
        if is_GState(state):
            return path
        
        for next_state in SStateList(state):
            cost=1
            new_g= g_score + cost
            if new_g < gList.get(next_state, float('inf')):
                gList[next_state]=new_g
                new_h=get_h(next_state)
                new_f=new_g+new_h

                action=None
                for i in range(len(state)):
                    if state[i]!= next_state[i]:
                        moved_car=state[i][0]
                        prev_row, prev_col= state[i][2], state[i][3]
                        new_row, new_col = next_state[i][2], next_state[i][3]
                        action = (moved_car, prev_row, prev_col, new_row, new_col)

                heapq.heappush(prior, (new_f,new_g,next_state,path + [action]))

    return None