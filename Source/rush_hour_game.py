import pygame
from map_loader import load_all_maps
from BFS_solver import bfs_solver
from DFS_solver import dfs_solver
from UCS_solver import ucs
from aStarSolver import A_Star_solver
import cv2
import copy
import time 

# Constants
CELL_SIZE = 80
GRID_SIZE = 6
GRID_WIDTH = CELL_SIZE * GRID_SIZE
GRID_HEIGHT = CELL_SIZE * GRID_SIZE
MENU_WIDTH = 180

WIDTH = GRID_WIDTH + MENU_WIDTH
HEIGHT = GRID_HEIGHT
FPS = 60

# Colors
GRAY = (180, 180, 180)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
RED = (200, 0, 0)
GREEN = (0, 150, 0)
BLUE = (30, 100, 150)

solution_path = []
solution_index = 0
solution_timer = 0
solution_delay = 500  # 500 ms giữa mỗi bước

solution_steps = 0
solution_time_ms = 0

is_playing = False
show_controls = False
no_solution_msg_time = None

def check_win(cars):
    red_car = next((car for car in cars if car.name.lower() == 'r'), None)
    return red_car and red_car.row == 2 and red_car.col + red_car.length == GRID_SIZE


def run_game():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Rush Hour Puzzle")
    clock = pygame.time.Clock()

    font = pygame.font.SysFont("Arial", 24, bold=True)
    big_font = pygame.font.SysFont("Arial", 36, bold=True)

    global no_solution_msg_time
    global show_controls

    # Game state variables
    state = "start"
    input_text = ""
    running = True
    fade_alpha = 0
    blink_timer = 0
    blink_on = True

    # Game data
    all_maps = load_all_maps()
    cars = []
    selected_car = None
    offset_x = 0
    offset_y = 0
    won = False
    auto_mode = False
    auto_algorithm = None
    auto_selecting = False
    current_level = None

    # Rects
    start_rect = None
    instructions_rect = None
    back_rect = None
    restart_rect = None
    menu_rect = None
    auto_rect = None
    continue_rect = None
    win_menu_rect = None
    completed_menu_rect = None
    bfs_rect = None
    dfs_rect = None
    ucs_rect = None
    astar_rect = None
    cancel_rect = None
    play_rect = None
    pause_rect = None

    # Load videos
    video_path = "Images/background.mp4"
    video_cap = cv2.VideoCapture(video_path)
    video_fps = video_cap.get(cv2.CAP_PROP_FPS) or 30
    video_frame_interval = int(1000 / video_fps)
    video_timer = 0
    video_surface = None

    # Load background image for grid area
    bg_image = pygame.image.load("Images/Sidewalk.png").convert()
    bg_image = pygame.transform.scale(bg_image, (GRID_WIDTH, GRID_HEIGHT))

    # Utility functions
    def draw_grid():
        for i in range(GRID_SIZE + 1):
            pygame.draw.line(screen, GRAY, (0, i * CELL_SIZE), (GRID_WIDTH, i * CELL_SIZE))
            pygame.draw.line(screen, GRAY, (i * CELL_SIZE, 0), (i * CELL_SIZE, GRID_HEIGHT))
        pygame.draw.rect(screen, (230, 230, 230), (GRID_WIDTH - 5, 2 * CELL_SIZE + 10, 20, CELL_SIZE - 20))

    def draw_cars():
        for car in cars:
            if car is None:
                continue
            x = car.col * CELL_SIZE
            y = car.row * CELL_SIZE
            w = car.length * CELL_SIZE if car.horizontal else CELL_SIZE
            h = CELL_SIZE if car.horizontal else car.length * CELL_SIZE

            img = car_images.get(car.name.upper())
            if img:
                img_scaled = pygame.transform.scale(img, (w, h))
                screen.blit(img_scaled, (x, y))
            else:
                rect = pygame.Rect(x + 5, y + 5, w - 10, h - 10)
                pygame.draw.rect(screen, pygame.Color(car.color), rect)
                label = font.render(car.name, True, WHITE)
                screen.blit(label, label.get_rect(center=rect.center))

    def is_blocked(moving_car, target_row, target_col):
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

    car_images = {}
    for car_name in ["R", "A", "B", "C", "D", "E", "F"]:
        try:
            img = pygame.image.load(f"Images/{car_name}.png").convert_alpha()
            car_images[car_name] = img
        except:
            car_images[car_name] = None

    while running:
        dt = clock.tick(FPS)

        # Update video frame        
        if state == "start":
            video_timer += dt
            if video_timer >= video_frame_interval:
                ret, frame = video_cap.read()
                if not ret:
                    video_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    ret, frame = video_cap.read()
                video_timer = 0
                if ret:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame_resized = cv2.resize(frame_rgb, (WIDTH, HEIGHT))
                    video_surface = pygame.surfarray.make_surface(frame_resized.swapaxes(0, 1))

        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if state == "start":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if start_rect and start_rect.collidepoint(event.pos):
                        state = "level_select"
                        input_text = ""
                    elif instructions_rect and instructions_rect.collidepoint(event.pos):
                        state = "instructions"

            elif state == "instructions":
                if event.type == pygame.MOUSEBUTTONDOWN and back_rect and back_rect.collidepoint(event.pos):
                    state = "start"

            elif state == "level_select":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if input_text.isdigit():
                            level = int(input_text)
                            if 0 <= level < len(all_maps):
                                cars = all_maps[level]
                                current_level = level
                                won = False
                                auto_mode = False
                                auto_algorithm = None
                                state = "playing"
                        input_text = ""
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    elif event.unicode.isdigit() and len(input_text) < 3:
                        input_text += event.unicode

            elif state == "playing":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if show_controls:
                        if play_rect and play_rect.collidepoint(event.pos):
                            is_playing = True
                        elif pause_rect and pause_rect.collidepoint(event.pos):
                            is_playing = False

                if auto_selecting:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        selected_solver = None
                        algo_name = ""

                        if bfs_rect and bfs_rect.collidepoint(event.pos):
                            selected_solver = bfs_solver
                            algo_name = "BFS"
                        elif dfs_rect and dfs_rect.collidepoint(event.pos):
                            selected_solver = dfs_solver
                            algo_name = "DFS"
                        elif ucs_rect and ucs_rect.collidepoint(event.pos):
                            selected_solver = ucs_solver
                            algo_name = "UCS"
                        elif astar_rect and astar_rect.collidepoint(event.pos):
                            selected_solver = A_Star_solver
                            algo_name = "A*"
                        elif cancel_rect and cancel_rect.collidepoint(event.pos):
                            auto_selecting = False
                            continue

                        if selected_solver:
                            auto_mode = True
                            auto_algorithm = algo_name
                            auto_selecting = False
                            start_time = time.time()
                            solution_path = selected_solver(cars)
                            end_time = time.time()

                            if not solution_path or len(solution_path) <= 1:
                                auto_mode = False
                                show_controls = False
                                is_playing = False
                                no_solution_msg_time = pygame.time.get_ticks()
                            else:
                                solution_time_ms = int((end_time - start_time) * 1000)
                                solution_steps = len(solution_path) - 1
                                solution_index = 0
                                solution_timer = pygame.time.get_ticks()
                                is_playing = True
                                show_controls = True
                    continue

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if won:
                        if continue_rect and continue_rect.collidepoint(event.pos):
                            if current_level + 1 < len(all_maps):
                                current_level += 1
                                cars = load_all_maps()[current_level]
                                won = False
                            else:
                                state = "game_completed"
                                fade_alpha = 0
                                blink_timer = 0
                        elif win_menu_rect and win_menu_rect.collidepoint(event.pos):
                            state = "start"
                            won = False
                        continue

                    if restart_rect and restart_rect.collidepoint(event.pos):
                        cars = load_all_maps()[current_level]
                        won = False
                    elif menu_rect and menu_rect.collidepoint(event.pos):
                        state = "start"
                        won = False
                    elif auto_rect and auto_rect.collidepoint(event.pos):
                        auto_selecting = True
                    else:
                        x, y = event.pos
                        if x < GRID_WIDTH:
                            col = x // CELL_SIZE
                            row = y // CELL_SIZE
                            for car in cars:
                                if car.horizontal and row == car.row and car.col <= col < car.col + car.length:
                                    selected_car = car
                                    offset_x = x - car.col * CELL_SIZE
                                    break
                                if not car.horizontal and col == car.col and car.row <= row < car.row + car.length:
                                    selected_car = car
                                    offset_y = y - car.row * CELL_SIZE
                                    break

                elif event.type == pygame.MOUSEBUTTONUP and selected_car:
                    red_car = next((c for c in cars if c.name.lower() == "r"), None)
                    if red_car and red_car.row == 2 and red_car.col + red_car.length == GRID_SIZE:
                        won = True
                    selected_car = None

                elif event.type == pygame.MOUSEMOTION and selected_car and not won:
                    x, y = event.pos
                    car = selected_car
                    if car.horizontal:
                        new_col = (x - offset_x + CELL_SIZE // 2) // CELL_SIZE
                        new_col = max(0, min(GRID_SIZE - car.length, new_col))
                        if not is_blocked(car, car.row, new_col):
                            car.col = new_col
                    else:
                        new_row = (y - offset_y + CELL_SIZE // 2) // CELL_SIZE
                        new_row = max(0, min(GRID_SIZE - car.length, new_row))
                        if not is_blocked(car, new_row, car.col):
                            car.row = new_row

            elif state == "game_completed":
                if event.type == pygame.MOUSEBUTTONDOWN and completed_menu_rect and completed_menu_rect.collidepoint(event.pos):
                    state = "start"

        # Update blinking
        if state == "game_completed":
            if fade_alpha < 255:
                fade_alpha = min(fade_alpha + 5, 255)
            blink_timer += dt
            if blink_timer >= 500:
                blink_on = not blink_on
                blink_timer = 0

        # Draw everything
        screen.fill(BLACK)

        if state == "start":
            if video_surface:
                screen.blit(video_surface, (0, 0))
            else:
                screen.fill(BLUE)
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 100))
            screen.blit(overlay, (0, 0))

            title = big_font.render("Rush Hour Puzzle", True, WHITE)
            screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80)))
            start = big_font.render("START", True, WHITE)
            start_rect = start.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(start, start_rect)
            instructions = font.render("INSTRUCTIONS", True, WHITE)
            instructions_rect = instructions.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60))
            screen.blit(instructions, instructions_rect)

        elif state == "instructions":
            screen.fill(BLUE)
            lines = [
                "How to play:",
                "- Objective: Move the red car to the exit.",
                "- Drag cars to move them.",
                "- Cars cannot overlap."
            ]
            for i, line in enumerate(lines):
                text = font.render(line, True, WHITE)
                screen.blit(text, (60, 80 + i * 40))
            back = font.render("BACK", True, WHITE)
            back_rect = back.get_rect(center=(WIDTH // 2, HEIGHT - 50))
            screen.blit(back, back_rect)

        elif state == "level_select":
            screen.fill((60, 120, 180))
            prompt = font.render(f"Enter level: {input_text}", True, WHITE)
            screen.blit(prompt, prompt.get_rect(center=(WIDTH // 2, HEIGHT // 2)))

        elif state == "playing":
            # Background and grid
            screen.blit(bg_image, (0, 0))
            draw_grid()
            draw_cars()
            # Auto Mode
            if auto_mode and solution_path and is_playing:
                current_time = pygame.time.get_ticks()
                if solution_index < len(solution_path):
                    if current_time - solution_timer >= solution_delay:
                        cars = copy.deepcopy(solution_path[solution_index])
                        solution_index += 1
                        solution_timer = current_time
                        if solution_index == len(solution_path):
                            is_playing = False
                            if check_win(cars):
                                won = True
                else:
                    is_playing = False
                    auto_mode = False



            # Menu
            pygame.draw.rect(screen, (230, 230, 230), (GRID_WIDTH, 0, MENU_WIDTH, HEIGHT))
            restart = font.render("Restart", True, BLACK)
            restart_rect = restart.get_rect(topleft=(GRID_WIDTH + 10, 50))
            screen.blit(restart, restart_rect)
            menu = font.render("Menu", True, BLACK) 
            menu_rect = menu.get_rect(topleft=(GRID_WIDTH + 10, 100))
            screen.blit(menu, menu_rect)
            auto = font.render("Auto", True, BLACK)
            auto_rect = auto.get_rect(topleft=(GRID_WIDTH + 10, 150))
            screen.blit(auto, auto_rect)

            if auto_mode:
                if show_controls:
                    play_pause_y = HEIGHT - 70
                    # Vẽ nút Play
                    play_text = font.render("Play", True, BLACK)
                    play_rect = play_text.get_rect(topleft=(GRID_WIDTH + 10, play_pause_y))
                    screen.blit(play_text, play_rect)

                    # Vẽ nút Pause
                    pause_text = font.render("Pause", True, BLACK)
                    pause_rect = pause_text.get_rect(topleft=(GRID_WIDTH + 100, play_pause_y))
                    screen.blit(pause_text, pause_rect)

                auto_msg = font.render(f"Auto mode: {auto_algorithm}", True, RED)
                if auto_mode and solution_path:
                    steps_text = font.render(f"Steps: {solution_steps}", True, BLACK)
                    time_text = font.render(f"Time: {solution_time_ms} ms", True, BLACK)
                    screen.blit(steps_text, (GRID_WIDTH + 10, HEIGHT - 140))
                    screen.blit(time_text, (GRID_WIDTH + 10, HEIGHT - 110))

                screen.blit(auto_msg, auto_msg.get_rect(center=(GRID_WIDTH + MENU_WIDTH // 2, HEIGHT - 30)))

            if auto_selecting:
                popup_height = 250
                popup_width = 200
                popup_x = (WIDTH - popup_width) // 2
                popup_y = (HEIGHT - popup_height) // 2
                pygame.draw.rect(screen, (240, 240, 240), (popup_x, popup_y, popup_width, popup_height))
                pygame.draw.rect(screen, BLACK, (popup_x, popup_y, popup_width, popup_height), 2)

                title = font.render("Select Algorithm:", True, BLACK)
                screen.blit(title, (popup_x + 20, popup_y + 10))

                bfs = font.render("BFS", True, BLACK)
                bfs_rect = bfs.get_rect(center=(popup_x + popup_width // 2, popup_y + 50))
                screen.blit(bfs, bfs_rect)

                dfs = font.render("DFS", True, BLACK)
                dfs_rect = dfs.get_rect(center=(popup_x + popup_width // 2, popup_y + 90))
                screen.blit(dfs, dfs_rect)

                ucs = font.render("UCS", True, BLACK)
                ucs_rect = ucs.get_rect(center=(popup_x + popup_width // 2, popup_y + 130))
                screen.blit(ucs, ucs_rect)

                astar = font.render("A*", True, BLACK)
                astar_rect = astar.get_rect(center=(popup_x + popup_width // 2, popup_y + 170))
                screen.blit(astar, astar_rect)

                cancel = font.render("Cancel", True, RED)
                cancel_rect = cancel.get_rect(center=(popup_x + popup_width // 2, popup_y + 210))
                screen.blit(cancel, cancel_rect)

            if won:
                win = big_font.render("YOU WIN!", True, GREEN)
                screen.blit(win, win.get_rect(center=(GRID_WIDTH // 2, HEIGHT // 2 - 40)))
                cont = font.render("Continue", True, BLACK)
                continue_rect = cont.get_rect(center=(GRID_WIDTH // 2, HEIGHT // 2 + 10))
                screen.blit(cont, continue_rect)
                back = font.render("Back to Menu", True, BLACK)
                win_menu_rect = back.get_rect(center=(GRID_WIDTH // 2, HEIGHT // 2 + 60))
                screen.blit(back, win_menu_rect)

        elif state == "game_completed":
            screen.fill((80, 180, 80))
            completed = big_font.render("Completed all levels!", True, WHITE)
            completed.set_alpha(fade_alpha)
            screen.blit(completed, completed.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40)))
            color = YELLOW if blink_on else WHITE
            back = font.render("Back to Menu", True, color)
            completed_menu_rect = back.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
            screen.blit(back, completed_menu_rect)

        if no_solution_msg_time:
            current_time = pygame.time.get_ticks()
            if current_time - no_solution_msg_time < 2000:
                message = font.render("No solution found!", True, BLACK)
                screen.blit(message, message.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
            else:
                no_solution_msg_time = None

        pygame.display.flip()

    pygame.quit()
    video_cap.release()
