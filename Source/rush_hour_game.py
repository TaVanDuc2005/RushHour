import pygame
from map_loader import load_all_maps

CELL_SIZE = 80
GRID_SIZE = 6
GRID_WIDTH = CELL_SIZE * GRID_SIZE
GRID_HEIGHT = CELL_SIZE * GRID_SIZE
MENU_WIDTH = 180

WIDTH = GRID_WIDTH + MENU_WIDTH
HEIGHT = GRID_HEIGHT
FPS = 60

# Màu sắc
GRAY = (180, 180, 180)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)

def run_game():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Rush Hour Puzzle")
    clock = pygame.time.Clock()

    font = pygame.font.SysFont("Arial", 24, bold=True)
    big_font = pygame.font.SysFont("Arial", 36, bold=True)

    running = True
    state = "start"
    input_text = ""

    start_rect = None
    instructions_rect = None
    back_rect = None

    restart_rect = None
    back_menu_rect = None
    auto_rect = None

    continue_rect = None
    win_back_rect = None
    completed_back_rect = None

    fade_alpha = 0
    blink_timer = 0
    blink_on = True

    cars = []
    selected_car = None
    offset_x = 0
    offset_y = 0
    won = False
    auto_mode = False
    current_level_index = None

    all_maps = load_all_maps()

    def draw_grid():
        for i in range(GRID_SIZE + 1):
            pygame.draw.line(screen, GRAY, (0, i * CELL_SIZE), (GRID_WIDTH, i * CELL_SIZE))
            pygame.draw.line(screen, GRAY, (i * CELL_SIZE, 0), (i * CELL_SIZE, GRID_HEIGHT))
        pygame.draw.rect(screen, (230, 230, 230), (GRID_WIDTH - 5, 2 * CELL_SIZE + 10, 20, CELL_SIZE - 20))

    def draw_cars():
        for car in cars:
            x1 = car.col * CELL_SIZE
            y1 = car.row * CELL_SIZE
            w = car.length * CELL_SIZE if car.horizontal else CELL_SIZE
            h = CELL_SIZE if car.horizontal else car.length * CELL_SIZE
            rect = pygame.Rect(x1 + 5, y1 + 5, w - 10, h - 10)
            color = pygame.Color(car.color)
            pygame.draw.rect(screen, color, rect)
            text = font.render(car.name, True, WHITE)
            text_rect = text.get_rect(center=rect.center)
            screen.blit(text, text_rect)

    def is_blocked(moving_car, target_row, target_col):
        for car in cars:
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

    while running:
        dt = clock.tick(FPS)
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
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if back_rect and back_rect.collidepoint(event.pos):
                        state = "start"

            elif state == "level_select":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if input_text.isdigit():
                            level_index = int(input_text)
                            if 0 <= level_index < len(all_maps):
                                cars = all_maps[level_index]
                                state = "playing"
                                selected_car = None
                                won = False
                                auto_mode = False
                                current_level_index = level_index
                            else:
                                input_text = ""
                        else:
                            input_text = ""
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    elif event.unicode.isdigit():
                        if len(input_text) < 3:
                            input_text += event.unicode

            elif state == "playing":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if won:
                        if continue_rect and continue_rect.collidepoint(event.pos):
                            if current_level_index is not None and current_level_index + 1 < len(all_maps):
                                current_level_index += 1
                                cars = load_all_maps()[current_level_index]
                                won = False
                                auto_mode = False
                                selected_car = None
                            else:
                                state = "game_completed"
                                fade_alpha = 0
                                blink_timer = 0
                                blink_on = True
                            continue
                        if win_back_rect and win_back_rect.collidepoint(event.pos):
                            state = "start"
                            won = False
                            auto_mode = False
                            selected_car = None
                            continue

                    if restart_rect and restart_rect.collidepoint(event.pos):
                        if current_level_index is not None:
                            cars = load_all_maps()[current_level_index]
                            won = False
                            auto_mode = False
                            selected_car = None
                        continue
                    if back_menu_rect and back_menu_rect.collidepoint(event.pos):
                        state = "start"
                        won = False
                        auto_mode = False
                        selected_car = None
                        continue
                    if auto_rect and auto_rect.collidepoint(event.pos):
                        auto_mode = True
                        continue

                    if not won:
                        x, y = event.pos
                        if x >= GRID_WIDTH:
                            continue
                        col = x // CELL_SIZE
                        row = y // CELL_SIZE
                        for car in cars:
                            if car.horizontal:
                                if row == car.row and car.col <= col < car.col + car.length:
                                    selected_car = car
                                    offset_x = x - car.col * CELL_SIZE
                                    break
                            else:
                                if col == car.col and car.row <= row < car.row + car.length:
                                    selected_car = car
                                    offset_y = y - car.row * CELL_SIZE
                                    break

                elif event.type == pygame.MOUSEBUTTONUP:
                    if selected_car:
                        red_car = next((c for c in cars if c.name.lower() == "r"), None)
                        if red_car and red_car.col + red_car.length == GRID_SIZE and red_car.row == 2:
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
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if completed_back_rect and completed_back_rect.collidepoint(event.pos):
                        state = "start"

        if state == "game_completed":
            # Update fade alpha
            if fade_alpha < 255:
                fade_alpha = min(fade_alpha + 5, 255)
            # Blink text every 500ms
            blink_timer += dt
            if blink_timer >= 500:
                blink_on = not blink_on
                blink_timer = 0

        screen.fill(WHITE)

        if state == "start":
            screen.fill((50, 150, 200))
            title_text = big_font.render("Rush Hour Puzzle", True, WHITE)
            title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80))
            screen.blit(title_text, title_rect)

            start_text = big_font.render("START", True, WHITE)
            start_rect = start_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(start_text, start_rect)

            instructions_text = font.render("INSTRUCTIONS", True, WHITE)
            instructions_rect = instructions_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60))
            screen.blit(instructions_text, instructions_rect)

        elif state == "instructions":
            screen.fill((30, 100, 150))
            lines = [
                "How to play:",
                "- Objective: Move the red car to the right exit.",
                "- Drag the car horizontally or vertically to move.",
                "- Cars cannot pass each other."
            ]
            for idx, line in enumerate(lines):
                line_text = font.render(line, True, WHITE)
                line_rect = line_text.get_rect(center=(WIDTH // 2, 100 + idx * 40))
                screen.blit(line_text, line_rect)

            back_text = font.render("BACK", True, WHITE)
            back_rect = back_text.get_rect(center=(WIDTH // 2, HEIGHT - 50))
            screen.blit(back_text, back_rect)

        elif state == "level_select":
            screen.fill((60, 120, 180))
            prompt = "Enter level: " + input_text
            prompt_text = font.render(prompt, True, WHITE)
            prompt_rect = prompt_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(prompt_text, prompt_rect)

        elif state == "playing":
            draw_grid()
            draw_cars()

            pygame.draw.rect(screen, (230, 230, 230), (GRID_WIDTH, 0, MENU_WIDTH, HEIGHT))

            restart_text = font.render("Restart", True, BLACK)
            restart_rect = restart_text.get_rect(topleft=(GRID_WIDTH + 10, 50))
            screen.blit(restart_text, restart_rect)

            back_menu_text = font.render("Back to Menu", True, BLACK)
            back_menu_rect = back_menu_text.get_rect(topleft=(GRID_WIDTH + 10, 100))
            screen.blit(back_menu_text, back_menu_rect)

            auto_text = font.render("Auto", True, BLACK)
            auto_rect = auto_text.get_rect(topleft=(GRID_WIDTH + 10, 150))
            screen.blit(auto_text, auto_rect)

            if auto_mode:
                auto_mode_text = font.render("Auto mode active!", True, (200, 0, 0))
                auto_mode_rect = auto_mode_text.get_rect(center=(GRID_WIDTH + MENU_WIDTH // 2, HEIGHT - 30))
                screen.blit(auto_mode_text, auto_mode_rect)

            if won:
                win_text = big_font.render("YOU WIN!", True, (0, 150, 0))
                win_rect = win_text.get_rect(center=(GRID_WIDTH // 2, HEIGHT // 2 - 40))
                screen.blit(win_text, win_rect)

                continue_text = font.render("Continue", True, BLACK)
                continue_rect = continue_text.get_rect(center=(GRID_WIDTH // 2, HEIGHT // 2 + 10))
                screen.blit(continue_text, continue_rect)

                win_back_text = font.render("Back to Menu", True, BLACK)
                win_back_rect = win_back_text.get_rect(center=(GRID_WIDTH // 2, HEIGHT // 2 + 60))
                screen.blit(win_back_text, win_back_rect)

        elif state == "game_completed":
            screen.fill((80, 180, 80))
            text_surface = big_font.render("Completed all levels!", True, WHITE)
            text_surface.set_alpha(fade_alpha)
            completed_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
            screen.blit(text_surface, completed_rect)

            color = YELLOW if blink_on else WHITE
            back_text = font.render("Back to Menu", True, color)
            completed_back_rect = back_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
            screen.blit(back_text, completed_back_rect)

        pygame.display.flip()

    pygame.quit()
