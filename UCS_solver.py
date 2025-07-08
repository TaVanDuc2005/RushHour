import heapq

class State:
    def __init__(self, vehicles, board, path=[], cost=0):
        self.vehicles = vehicles  # {'X': (x, y, dir, len), ...}
        self.board = board  # 6x6 list
        self.path = path
        self.cost = cost

    def __lt__(self, other): return self.cost < other.cost

    def is_goal(self):
        x, y, d, l = self.vehicles['X']
        return d == 'H' and y + l - 1 == 5

    def signature(self):
        return tuple(sorted(self.vehicles.items()))

    def move(self, vid, direction, steps):
        x, y, d, l = self.vehicles[vid]
        new_x, new_y = x, y
        dx, dy = (0, direction) if d == 'H' else (direction, 0)
        for i in range(l):  # Clear old
            self.board[x + i * (d == 'V')][y + i * (d == 'H')] = '.'
        new_x += dx * steps
        new_y += dy * steps
        for i in range(l):  # Draw new
            self.board[new_x + i * (d == 'V')][new_y + i * (d == 'H')] = vid
        self.vehicles[vid] = (new_x, new_y, d, l)

    def can_move(self, vid, direction, steps):
        x, y, d, l = self.vehicles[vid]
        dx, dy = (0, direction) if d == 'H' else (direction, 0)
        for i in range(1, steps + 1):
            nx = x + dx * i if direction == 1 else x + dx * (i - 1)
            ny = y + dy * i if direction == 1 else y + dy * (i - 1)
            tx = nx + (l - 1) * (d == 'V')
            ty = ny + (l - 1) * (d == 'H')
            if not (0 <= nx <= 5 and 0 <= ny <= 5 and 0 <= tx <= 5 and 0 <= ty <= 5):
                return False
            for j in range(l):
                cx = nx + j * (d == 'V')
                cy = ny + j * (d == 'H')
                if self.board[cx][cy] != '.':
                    return False
        return True

    def successors(self):
        result = []
        for vid, (x, y, d, l) in self.vehicles.items():
            for dir in [-1, 1]:
                step = 1
                while self.can_move(vid, dir, step):
                    new_state = State(
                        vehicles=self.vehicles.copy(),
                        board=[row[:] for row in self.board],
                        path=self.path + [(vid, dir, step)],
                        cost=self.cost + l
                    )
                    new_state.move(vid, dir, step)
                    result.append(new_state)
                    step += 1
        return result

def ucs(start):
    heap = []
    visited = set()
    heapq.heappush(heap, start)
    while heap:
        state = heapq.heappop(heap)
        sig = state.signature()
        if sig in visited: continue
        visited.add(sig)
        if state.is_goal():
            return state.path, state.cost
        for s in state.successors():
            heapq.heappush(heap, s)
    return None, -1

def init_board():
    board = [['.' for _ in range(6)] for _ in range(6)]
    vehicles = {
        'X': (2, 0, 'H', 2),
        'A': (0, 0, 'V', 3),
        'B': (0, 3, 'V', 2),
        'C': (0, 5, 'V', 3),
        'D': (3, 0, 'H', 2),
        'E': (4, 3, 'H', 2)
    }
    for vid, (x, y, d, l) in vehicles.items():
        for i in range(l):
            if d == 'H': board[x][y + i] = vid
            else: board[x + i][y] = vid
    return State(vehicles, board)

if __name__ == "__main__":
    init = init_board()
    path, cost = ucs(init)
    if path:
        print(f"✅ Found in {len(path)} steps, cost = {cost}")
        for move in path:
            print(f"Move {move[0]} {'←↑' if move[1]==-1 else '→↓'} {move[2]}")
    else:
        print("❌ No solution found")
