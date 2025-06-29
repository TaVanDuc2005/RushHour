# map_loader.py
from modelCar import Car

def parse_map(map_data):
    car_positions = {}
    for row in range(len(map_data)):
        for col in range(len(map_data[row])):
            ch = map_data[row][col]
            if ch == '.' or ch == ' ':
                continue
            if ch not in car_positions:
                car_positions[ch] = [(row, col)]
            else:
                car_positions[ch].append((row, col))

    color_map = {
        'r': 'red', 'A': 'blue', 'B': 'green',
        'C': 'yellow', 'D': 'orange', 'E': 'purple',
        'F': 'cyan', 'G': 'pink'
    }

    cars = []
    for name, positions in car_positions.items():
        if len(positions) < 2:
            continue
        
        positions.sort()
        (r1, c1), (r2, c2) = positions[0], positions[1]
        if r1 == r2:
            horizontal = True
        elif c1 == c2:
            horizontal = False
        else:
            raise ValueError(f"Invalid car positions: {positions}")

        length = len(positions)
        color = color_map.get(name, 'gray')
        cars.append(Car(name, r1, c1, length, horizontal, color))
    return cars

def load_all_maps(filename="maps.txt"):
    with open(filename, "r") as file:
        lines = [line.strip() for line in file if line.strip() and not line.startswith('#')]

    maps = []
    for i in range(0, len(lines), 6):
        map_data = lines[i:i+6]
        if len(map_data) == 6:
            maps.append(parse_map(map_data))
    return maps
