import tkinter as tk
from modelCar import Car

CELL_SIZE = 60
GRID_SIZE = 6

class RushHourGame:
    def __init__(self, master):
        self.master = master
        master.title("Rush Hour Puzzle")

        self.canvas = tk.Canvas(master, width=CELL_SIZE * GRID_SIZE, height=CELL_SIZE * GRID_SIZE, bg="white")
        self.canvas.pack()

        self.cars = [
            Car('red', 2, 0, 2, True, 'red'),  # The main car
            Car('A', 0, 0, 2, False, 'blue'),
            Car('B', 0, 3, 3, True, 'green'),
            Car('C', 4, 2, 2, False, 'yellow'),
            Car('D', 5, 0, 3, True, 'orange'),
        ]

        self.selected_car = None
        self.offset_x = 0
        self.offset_y = 0

        self.draw_grid()
        self.draw_cars()

        self.canvas.bind("<Button-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)

    def draw_grid(self):
        for i in range(GRID_SIZE + 1):
            self.canvas.create_line(0, i * CELL_SIZE, CELL_SIZE * GRID_SIZE, i * CELL_SIZE, fill="gray")
            self.canvas.create_line(i * CELL_SIZE, 0, i * CELL_SIZE, CELL_SIZE * GRID_SIZE, fill="gray")
        # Draw exit
        self.canvas.create_rectangle(GRID_SIZE * CELL_SIZE - 5, 2 * CELL_SIZE + 10, GRID_SIZE * CELL_SIZE + 15, 3 * CELL_SIZE - 10, fill="gray90", outline="gray90")

    def draw_cars(self):
        self.canvas.delete("car")
        for car in self.cars:
            x1 = car.col * CELL_SIZE
            y1 = car.row * CELL_SIZE
            if car.horizontal:
                x2 = x1 + car.length * CELL_SIZE
                y2 = y1 + CELL_SIZE
            else:
                x2 = x1 + CELL_SIZE
                y2 = y1 + car.length * CELL_SIZE
            self.canvas.create_rectangle(x1 + 5, y1 + 5, x2 - 5, y2 - 5, fill=car.color, tags="car")
            self.canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2, text=car.name, tags="car", fill="white", font=("Arial", 16, "bold"))

    def on_mouse_down(self, event):
        col = event.x // CELL_SIZE
        row = event.y // CELL_SIZE
        for car in self.cars:
            if car.horizontal:
                if row == car.row and car.col <= col < car.col + car.length:
                    self.selected_car = car
                    self.offset_x = event.x - car.col * CELL_SIZE
                    self.offset_y = event.y - car.row * CELL_SIZE
                    break
            else:
                if col == car.col and car.row <= row < car.row + car.length:
                    self.selected_car = car
                    self.offset_x = event.x - car.col * CELL_SIZE
                    self.offset_y = event.y - car.row * CELL_SIZE
                    break

    def on_mouse_drag(self, event):
        if not self.selected_car:
            return
        car = self.selected_car
        if car.horizontal:
            new_col = (event.x - self.offset_x + CELL_SIZE // 2) // CELL_SIZE
            new_col = max(0, min(GRID_SIZE - car.length, new_col))
            if not self.is_blocked(car, car.row, new_col):
                car.col = new_col
        else:
            new_row = (event.y - self.offset_y + CELL_SIZE // 2) // CELL_SIZE
            new_row = max(0, min(GRID_SIZE - car.length, new_row))
            if not self.is_blocked(car, new_row, car.col):
                car.row = new_row
        self.draw_grid()
        self.draw_cars()

    def on_mouse_up(self, event):
        if not self.selected_car:
            return
        # Check win condition
        red_car = self.cars[0]
        if red_car.name == 'red' and red_car.col + red_car.length == GRID_SIZE and red_car.row == 2:
            self.canvas.create_text(CELL_SIZE * GRID_SIZE // 2, CELL_SIZE * GRID_SIZE // 2, text="YOU WIN!", fill="black", font=("Arial", 32, "bold"), tags="win")
        self.selected_car = None

    def is_blocked(self, moving_car, target_row, target_col):
        for car in self.cars:
            if car == moving_car:
                continue
            if moving_car.horizontal:
                if car.horizontal:
                    if car.row != moving_car.row:
                        continue
                    if not (target_col + moving_car.length <= car.col or target_col >= car.col + car.length):
                        return True
                else:
                    for i in range(moving_car.length):
                        if car.col == target_col + i and car.row <= moving_car.row < car.row + car.length:
                            return True
            else:
                if not car.horizontal:
                    if car.col != moving_car.col:
                        continue
                    if not (target_row + moving_car.length <= car.row or target_row >= car.row + car.length):
                        return True
                else:
                    for i in range(moving_car.length):
                        if car.row == target_row + i and car.col <= moving_car.col < car.col + car.length:
                            return True
        return False