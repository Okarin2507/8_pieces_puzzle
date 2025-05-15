import pygame
import sys
import importlib
import os
from collections import deque
import time
import traceback
import subprocess

# --- Theme Colors: Blue Rose ---
GRADIENT_TOP_COLOR = (30, 30, 70)
GRADIENT_BOTTOM_COLOR = (50, 60, 100)
PRIMARY = (110, 130, 230)
PRIMARY_DARK = (80, 100, 200)
ACCENT_COLOR = (200, 140, 180)

SIDEBAR_BG = (40, 50, 80)
SIDEBAR_ITEM_BG = (60, 70, 110)
SIDEBAR_ITEM_HOVER_BG = (80, 90, 140)
SIDEBAR_ITEM_SELECTED_BG = PRIMARY

TEXT_PRIMARY = (225, 230, 245)
TEXT_SECONDARY = (180, 190, 215)
TEXT_PLACEHOLDER = (130, 140, 160)

BUTTON_SHADOW_COLOR = (20, 25, 45)

ERROR_COLOR = (230, 60, 70)
WARNING_COLOR = (255, 190, 0)

NUMBER_TILE_COLORS = {
    1: (66, 133, 244), 2: (219, 68, 55), 3: (244, 180, 0), 4: (15, 157, 88),
    5: (171, 71, 188), 6: (255, 112, 67), 7: (0, 172, 193), 8: (255, 160, 0)
}
SOLVED_BORDER_COLOR = (250, 250, 250)
SOLVED_BORDER_WIDTH = 3
TILE_BG_DEFAULT = (70, 80, 120)

# --- Algorithm Import ---
try:
    from algorithms import ALGORITHM_LIST
except ImportError:
    ALGORITHM_LIST = [
        ("Greedy Search", "greedy"), ("Greedy Search (Double Moves)", "greedy_double"),
        ("A* Search (Manhattan)", "a_star_manhattan"), ("A* Search (Manhattan, Double)", "a_star_manhattan_double"),
        ("A* Search (Misplaced)", "a_star_misplaced"), ("A* Search (Misplaced, Double)", "a_star_misplaced_double"),
        ("BFS (Breadth-First Search)", "bfs"), ("BFS (Double Moves)", "bfs_double"),
        ("UCS (Uniform Cost Search)", "ucs"), ("UCS (Double Moves)", "ucs_double"),
        ("Hill Climbing", "hill_climbing"), ("Hill Climbing (Double)", "hill_climbing_double"),
        ("Stochastic Hill Climbing", "stochastic_hc"), ("Stochastic Hill Climbing (Double)", "stochastic_hc_double"),
        ("DFS (Depth-First Search)", "dfs"), ("DFS (Double Moves)", "dfs_double"),
        ("Steepest Ascent Hill Climbing", "steepest_hc"), ("Steepest Ascent Hill Climbing (Double)", "steepest_hc_double"),
        ("IDDFS (Iterative Deepening DFS)", "iddfs"), ("IDDFS (Double Moves)", "iddfs_double"),
        ("IDA* Search", "ida_star"), ("IDA* (Double Moves)", "ida_star_double"),
        ("Beam Search", "beam_search"), ("QLearning", "q_learning"),
    ]
    print("Cảnh báo: Không thể nhập ALGORITHM_LIST từ gói algorithms. Sử dụng danh sách mặc định.")
    if not os.path.exists('algorithms'): print("Lỗi: Không tìm thấy thư mục 'algorithms'.")


# --- Constants ---
SIDEBAR_WIDTH = 520
SIDEBAR_MARGIN = 25
SIDEBAR_ITEM_HEIGHT = 48; SIDEBAR_ITEM_PADDING = 6
PATH_DISPLAY_BOX_MARGIN_TOP = 25; PATH_DISPLAY_BOX_MARGIN_BOTTOM_FROM_BUTTONS = 30
PATH_DISPLAY_BOX_PADDING = 12; PATH_DISPLAY_MAX_VISIBLE_STEPS = 5
PATH_DISPLAY_LINE_SPACING = 6; MIN_PATH_BOX_HEIGHT = 90
SLIDER_TRACK_HEIGHT = 14; SLIDER_HANDLE_WIDTH = 32; SLIDER_HANDLE_HEIGHT = 26
SLIDER_PUZZLE_AREA_MARGIN_TOP = 35; SLIDER_WIDTH_PERCENTAGE = 0.50
MIN_ANIMATION_SPEED = 1; MAX_ANIMATION_SPEED = 1000; DEFAULT_ANIMATION_SPEED = 50

# --- Gradient Background Function ---
def draw_gradient_background(surface, top_color, bottom_color):
    height = surface.get_height(); width = surface.get_width()
    rect_strip = pygame.Rect(0, 0, width, 1)
    for y in range(height):
        r = top_color[0] + (bottom_color[0] - top_color[0]) * y / height
        g = top_color[1] + (bottom_color[1] - top_color[1]) * y / height
        b = top_color[2] + (bottom_color[2] - top_color[2]) * y / height
        rect_strip.top = y
        pygame.draw.rect(surface, (int(r), int(g), int(b)), rect_strip)

# --- Text Helper Functions ---
def truncate_text(text, font, max_width, ellipsis="..."):
    if not text or font.size(text)[0] <= max_width: return text
    truncated_text = ""
    avg_char_width = font.size("a")[0] if font.size("a")[0] > 0 else 10

    for char_idx, char in enumerate(text):
        if font.size(truncated_text + char + ellipsis)[0] > max_width:
            if char_idx == 0:
                if font.size(ellipsis)[0] > max_width:
                     return text[:max(0, max_width // avg_char_width)] if avg_char_width > 0 else ""
                possible_len = max(0, (max_width - font.size(ellipsis)[0]) // avg_char_width) if avg_char_width > 0 else 0
                return text[:possible_len] + ellipsis
            break
        truncated_text += char
    return truncated_text + ellipsis

def render_text_wrapped(text, font, color, max_width, surface_to_blit_on, start_x, start_y, line_spacing=5, center_x=False, rect_to_center_in=None):
    words = text.split(' '); lines = []; current_line_text = ""
    for word in words:
        test_line = current_line_text + word + " "
        if font.size(test_line)[0] <= max_width: current_line_text = test_line
        else:
            if current_line_text: lines.append(current_line_text.strip())
            current_line_text = word + " "
            if font.size(current_line_text)[0] > max_width:
                truncated_word = truncate_text(word, font, max_width)
                lines.append(truncated_word)
                current_line_text = ""
                continue
    if current_line_text: lines.append(current_line_text.strip())

    current_y_offset = 0
    total_height = 0
    for i, line_text_val in enumerate(lines):
        if not line_text_val: continue
        line_surf = font.render(line_text_val, True, color)
        if center_x and rect_to_center_in: line_rect = line_surf.get_rect(centerx=rect_to_center_in.centerx, top=start_y + current_y_offset)
        else: line_rect = line_surf.get_rect(left=start_x, top=start_y + current_y_offset)
        surface_to_blit_on.blit(line_surf, line_rect)
        line_h = font.get_height()
        current_y_offset += line_h
        total_height += line_h
        if i < len(lines) -1:
            current_y_offset += line_spacing
            total_height += line_spacing
    return total_height

# --- Helper Functions (Puzzle Logic) ---
def get_inversions(state): state_nb = [x for x in state if x != 9]; inv = 0; L = len(state_nb); [ (inv := inv + 1) for i in range(L) for j in range(i + 1, L) if state_nb[i] > state_nb[j] ]; return inv
def is_solvable(state): return (9 in state and len(state) == 9) and get_inversions(state) % 2 == 0
def is_valid_puzzle_state(state): return isinstance(state, (list, tuple)) and len(state) == 9 and sorted(state) == list(range(1, 10))

def get_neighbors(state):
    neighbors = []; s = list(state)
    try: blank_index = s.index(9)
    except ValueError: return []
    row, col = divmod(blank_index, 3)
    moves = [(-1, 0, "Up"), (1, 0, "Down"), (0, -1, "Left"), (0, 1, "Right")]
    for dr, dc, move_name in moves:
        new_row, new_col = row + dr, col + dc
        if 0 <= new_row < 3 and 0 <= new_col < 3:
            new_index = new_row * 3 + new_col
            new_s = s[:]
            new_s[blank_index], new_s[new_index] = new_s[new_index], new_s[blank_index]
            neighbors.append(tuple(new_s))
    return neighbors

# --- Class Definitions ---
class MessageBox:
    def __init__(self, width, height, title, message, button_text="OK"):
        self.rect = pygame.Rect((WIDTH - width) // 2, (HEIGHT - height) // 2, width, height)
        self.title = title; self.message = message; self.border_radius = 14; self.active = False
        button_width = 130; button_height = 48
        button_x = self.rect.x + (self.rect.width - button_width) // 2
        button_y = self.rect.bottom - button_height - 30
        self.ok_button = Button(button_x, button_y, button_width, button_height, button_text, col=PRIMARY, hcol=PRIMARY_DARK)
    def draw(self, screen_surf, title_font_s, font_s, button_font_s):
        if not self.active: return
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA); overlay.fill((0,0,0,180)); screen_surf.blit(overlay, (0,0))
        pygame.draw.rect(screen_surf, SIDEBAR_BG, self.rect, border_radius=self.border_radius)
        inner_rect_bg = (SIDEBAR_BG[0]-10, SIDEBAR_BG[1]-10, SIDEBAR_BG[2]-10)
        pygame.draw.rect(screen_surf, tuple(max(0,c) for c in inner_rect_bg) , self.rect.inflate(-8,-8), border_radius=self.border_radius-3)

        title_surface = title_font_s.render(self.title, True, ACCENT_COLOR if ACCENT_COLOR else PRIMARY); title_rect = title_surface.get_rect(centerx=self.rect.centerx, y=self.rect.y + 30); screen_surf.blit(title_surface, title_rect)
        msg_start_y = self.rect.y + title_rect.height + 55; msg_max_width = self.rect.width - 70
        render_text_wrapped(self.message, font_s, TEXT_PRIMARY, msg_max_width, screen_surf, self.rect.x + 35, msg_start_y, line_spacing=7, center_x=True, rect_to_center_in=self.rect)
        self.ok_button.draw(screen_surf, button_font_s)
    def check_hover(self, mouse_pos): return self.ok_button.check_hover(mouse_pos) if self.active else False
    def handle_event(self, event):
        if not self.active: return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.ok_button.is_clicked(event.pos, True):
            self.active = False; return True
        return False

class AnimatedTile:
    def __init__(self, value, x, y, size):
        self.value = value; self.size = size; self.inner_size = int(size * 0.90)
        self.rect = pygame.Rect(x,y,size,size); self.inner_rect = pygame.Rect(0,0,self.inner_size,self.inner_size); self.inner_rect.center = self.rect.center
        self.current_x = float(x); self.current_y = float(y); self.target_x = float(x); self.target_y = float(y)
        self.speed = 0.24; self.is_solved_position = False
        self.border_radius = max(7, int(self.inner_size * 0.13))

    def set_target(self, x, y): self.target_x = float(x); self.target_y = float(y)
    def update(self):
        dx = self.target_x - self.current_x; dy = self.target_y - self.current_y
        if abs(dx) < 0.5 and abs(dy) < 0.5: self.current_x = self.target_x; self.current_y = self.target_y
        else: self.current_x += dx*self.speed; self.current_y += dy*self.speed
        self.rect.topleft = (int(self.current_x), int(self.current_y)); self.inner_rect.center = self.rect.center
    def draw(self, screen_surf, font_s):
        if self.value == 9: return
        bg_color = NUMBER_TILE_COLORS.get(self.value, TILE_BG_DEFAULT)
        pygame.draw.rect(screen_surf, bg_color, self.inner_rect, border_radius=self.border_radius)
        text = font_s.render(str(self.value), True, TEXT_PRIMARY); text_rect = text.get_rect(center=self.inner_rect.center); screen_surf.blit(text, text_rect)
        if self.is_solved_position: pygame.draw.rect(screen_surf, SOLVED_BORDER_COLOR, self.inner_rect, border_radius=self.border_radius, width=SOLVED_BORDER_WIDTH)
    def is_at_target(self): return abs(self.current_x - self.target_x) < 0.5 and abs(self.current_y - self.target_y) < 0.5

class Button:
     def __init__(self, x, y, width, height, text, col=PRIMARY, hcol=PRIMARY_DARK, shcol=BUTTON_SHADOW_COLOR):
         self.rect=pygame.Rect(x,y,width,height);self.text=text;self.base_color=col;self.hover_color=hcol;self.shadow_color=shcol
         self.is_hovered=False;self.border_radius=12;self.shadow_offset=4;self.y_offset=0
     def draw(self, screen_surf, font_s):
         current_color = self.hover_color if self.is_hovered else self.base_color
         shadow_rect = self.rect.move(self.shadow_offset, self.shadow_offset + self.y_offset); pygame.draw.rect(screen_surf, self.shadow_color, shadow_rect, border_radius=self.border_radius)
         button_draw_rect = self.rect.move(0, self.y_offset); pygame.draw.rect(screen_surf, current_color, button_draw_rect, border_radius=self.border_radius)
         text_surface = font_s.render(self.text, True, TEXT_PRIMARY); screen_surf.blit(text_surface, text_surface.get_rect(center=button_draw_rect.center))
     def check_hover(self, mouse_pos): self.is_hovered = self.rect.collidepoint(mouse_pos); return self.is_hovered
     def is_clicked(self, mouse_pos, mouse_click_event):
        clicked = self.is_hovered and mouse_click_event;
        if clicked: self.y_offset = self.shadow_offset
        return clicked

class SpeedSlider:
    def __init__(self, h_width, h_height, track_c, handle_c, min_s, max_s, init_s):
        self.min_speed = min_s; self.max_speed = max_s; self.current_speed = init_s
        self.track_rect = pygame.Rect(0, 0, 0, 0); self.handle_rect = pygame.Rect(0, 0, h_width, h_height)
        self.slider_min_x = 0; self.slider_max_x = 0; self.slider_range_x = 0
        self.track_color = track_c; self.handle_color = handle_c
        self.is_dragging = False; self.active = False

    def update_layout(self, x_track_start, y_center, track_width):
        self.track_rect = pygame.Rect(x_track_start, y_center - SLIDER_TRACK_HEIGHT // 2, track_width, SLIDER_TRACK_HEIGHT)
        self.slider_min_x = self.track_rect.left + self.handle_rect.width // 2
        self.slider_max_x = self.track_rect.right - self.handle_rect.width // 2
        self.slider_range_x = self.slider_max_x - self.slider_min_x
        if self.slider_range_x <= 0: self.slider_range_x = 1
        self._update_handle_pos_from_speed()

    def _update_handle_pos_from_speed(self):
        if not self.track_rect.height: return
        if self.max_speed == self.min_speed: percentage = 0.5
        else: percentage = (self.current_speed - self.min_speed) / (self.max_speed - self.min_speed)
        percentage = max(0, min(1, percentage))
        handle_center_x = self.slider_min_x + percentage * self.slider_range_x
        self.handle_rect.center = (int(handle_center_x), self.track_rect.centery)

    def _update_speed_from_handle_pos(self):
        if self.slider_range_x == 0: percentage = 0
        else: percentage = (self.handle_rect.centerx - self.slider_min_x) / self.slider_range_x
        self.current_speed = self.min_speed + percentage * (self.max_speed - self.min_speed)
        self.current_speed = max(self.min_speed, min(self.max_speed, self.current_speed))

    def handle_event(self, event, mouse_pos):
        global switch_time
        if not self.active: return False
        changed = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.handle_rect.collidepoint(mouse_pos) or self.track_rect.collidepoint(mouse_pos):
                self.is_dragging = True
                if self.track_rect.collidepoint(mouse_pos) and not self.handle_rect.collidepoint(mouse_pos):
                    self.handle_rect.centerx = max(self.slider_min_x, min(mouse_pos[0], self.slider_max_x))
                self._update_speed_from_handle_pos()
                switch_time = int(self.current_speed)
                changed = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_dragging:
                self.is_dragging = False
                changed = True
        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging:
                self.handle_rect.centerx = max(self.slider_min_x, min(mouse_pos[0], self.slider_max_x))
                self._update_speed_from_handle_pos()
                switch_time = int(self.current_speed)
                changed = True
        return changed

    def draw(self, screen_surf, font_s):
        if not self.active or not self.track_rect.height: return
        pygame.draw.rect(screen_surf, self.track_color, self.track_rect, border_radius=SLIDER_TRACK_HEIGHT//2)
        pygame.draw.rect(screen_surf, self.handle_color, self.handle_rect, border_radius=7)
        speed_text = f"Tốc độ: {int(self.current_speed)}ms"; text_surf = font_s.render(speed_text,True,TEXT_SECONDARY)
        text_rect = text_surf.get_rect(midleft=(self.track_rect.right+25, self.track_rect.centery)); screen_surf.blit(text_surf,text_rect)
        fast_lbl = font_s.render("Nhanh",True,TEXT_SECONDARY); slow_lbl = font_s.render("Chậm",True,TEXT_SECONDARY)
        screen_surf.blit(fast_lbl, fast_lbl.get_rect(midright=(self.track_rect.left-20, self.track_rect.centery)))
        screen_surf.blit(slow_lbl, slow_lbl.get_rect(midleft=(text_rect.right+20, self.track_rect.centery)))

    def get_speed(self): return int(self.current_speed)

# --- GUI Drawing Functions ---
def draw_menu(screen_surf, title_font_s, font_s, button_font_s, solve_btn_obj, edit_btn_obj, blind_btn_obj, fill_btn_obj, start_state_val, sel_algo_idx, scroll_offset, hover_idx, sidebar_r, max_disp_items):
    pygame.draw.rect(screen_surf, SIDEBAR_BG, sidebar_r, border_radius=14)
    sidebar_title_surf = title_font_s.render("Thuật toán", True, ACCENT_COLOR if ACCENT_COLOR else PRIMARY)
    sidebar_title_r = sidebar_title_surf.get_rect(centerx=sidebar_r.centerx, y=sidebar_r.y+30); screen_surf.blit(sidebar_title_surf, sidebar_title_r)

    sidebar_title_h_approx = sidebar_title_r.height + 55
    start_item_y_pos = sidebar_r.y + sidebar_title_h_approx
    visible_area_h = sidebar_r.height - sidebar_title_h_approx - 30

    for i in range(len(ALGORITHM_LIST)):
        item_y = start_item_y_pos + (i - scroll_offset) * SIDEBAR_ITEM_HEIGHT
        if start_item_y_pos <= item_y < start_item_y_pos + visible_area_h - SIDEBAR_ITEM_PADDING:
            item_r = pygame.Rect(sidebar_r.x+SIDEBAR_ITEM_PADDING, item_y, sidebar_r.width-2*SIDEBAR_ITEM_PADDING, SIDEBAR_ITEM_HEIGHT-SIDEBAR_ITEM_PADDING)
            bg_c = SIDEBAR_ITEM_SELECTED_BG if i == sel_algo_idx else SIDEBAR_ITEM_HOVER_BG if i == hover_idx else SIDEBAR_ITEM_BG
            pygame.draw.rect(screen_surf, bg_c, item_r, border_radius=9)
            algo_name_disp = truncate_text(ALGORITHM_LIST[i][0], font_s, item_r.width-30)
            text_s = font_s.render(algo_name_disp, True, TEXT_PRIMARY); screen_surf.blit(text_s, text_s.get_rect(midleft=(item_r.x+15, item_r.centery)))

    content_x = sidebar_r.right + SIDEBAR_MARGIN; content_w = WIDTH - content_x - SIDEBAR_MARGIN
    content_cx = content_x + content_w // 2

    title_h = title_font_s.get_height()
    instr_lines_list = ["Chọn thuật toán từ danh sách bên trái.", "Nhấn nút 'Bắt đầu' để giải.", "Hoặc chọn các nút chức năng khác.", f"(Đích: {GOAL_STATE})"]

    instr_max_w = content_w * 0.9
    instr_max_w = max(200, instr_max_w)

    temp_surface_for_calc = pygame.Surface((1,1))
    instr_block_h_actual = 0
    for line_idx, text_val in enumerate(instr_lines_list):
        instr_block_h_actual += render_text_wrapped(text_val, font_s, (0,0,0), instr_max_w, temp_surface_for_calc, 0, 0, line_spacing=12)
        if line_idx < len(instr_lines_list) -1: instr_block_h_actual += 5


    btn_h_val = solve_btn_obj.rect.height; num_btns = 4; btn_spacing = 28
    btn_block_h = num_btns*btn_h_val + (num_btns-1)*btn_spacing

    preview_lbl_h = font_s.get_height(); mini_tile_s = 48; mini_pad_v = 5
    mini_grid_h = (mini_tile_s+mini_pad_v)*3 - mini_pad_v

    space_title_instr, space_instr_btn, space_btn_preview, space_preview_grid = 45, 55, 55, 28
    total_content_h = title_h + space_title_instr + instr_block_h_actual + space_instr_btn + btn_block_h + space_btn_preview + preview_lbl_h + space_preview_grid + mini_grid_h

    available_content_area_h = HEIGHT - 2*SIDEBAR_MARGIN
    content_start_y_pos = SIDEBAR_MARGIN + max(0, (available_content_area_h - total_content_h)//2)

    current_y_pos = content_start_y_pos

    title_render_s = title_font_s.render("8-Puzzle Solver", True, ACCENT_COLOR if ACCENT_COLOR else PRIMARY)
    screen_surf.blit(title_render_s, title_render_s.get_rect(centerx=content_cx, top=current_y_pos)); current_y_pos += title_h + space_title_instr

    instr_y_start_pos = current_y_pos
    actual_instr_rendered_height = 0
    for text_val_instr in instr_lines_list:
        actual_instr_rendered_height += render_text_wrapped(text_val_instr, font_s, TEXT_SECONDARY, instr_max_w, screen_surf, 0, instr_y_start_pos + actual_instr_rendered_height, line_spacing=12, center_x=True, rect_to_center_in=pygame.Rect(content_x,0,content_w,100))
    current_y_pos += actual_instr_rendered_height + space_instr_btn


    btn_x_pos = content_cx - solve_btn_obj.rect.width//2
    solve_btn_obj.rect.topleft=(btn_x_pos, current_y_pos); edit_btn_obj.rect.topleft=(btn_x_pos, solve_btn_obj.rect.bottom+btn_spacing)
    blind_btn_obj.rect.topleft=(btn_x_pos, edit_btn_obj.rect.bottom+btn_spacing); fill_btn_obj.rect.topleft=(btn_x_pos, blind_btn_obj.rect.bottom+btn_spacing)
    solve_btn_obj.draw(screen_surf,button_font_s); edit_btn_obj.draw(screen_surf,button_font_s); blind_btn_obj.draw(screen_surf,button_font_s); fill_btn_obj.draw(screen_surf,button_font_s)
    current_y_pos += btn_block_h + space_btn_preview

    label_s = font_s.render("Trạng thái ban đầu:", True, TEXT_PRIMARY)
    screen_surf.blit(label_s, label_s.get_rect(centerx=content_cx, top=current_y_pos)); current_y_pos += preview_lbl_h + space_preview_grid

    mini_w = (mini_tile_s+mini_pad_v)*3 - mini_pad_v
    mini_start_x_pos = content_cx - mini_w//2; mini_start_y_pos = current_y_pos
    for i, val_tile in enumerate(start_state_val):
        r,c = divmod(i,3); x_pos = mini_start_x_pos + c*(mini_tile_s+mini_pad_v); y_pos = mini_start_y_pos + r*(mini_tile_s+mini_pad_v)
        if val_tile == 9: continue
        tile_r = pygame.Rect(x_pos,y_pos,mini_tile_s,mini_tile_s)
        bg_c_tile = NUMBER_TILE_COLORS.get(val_tile, TILE_BG_DEFAULT)
        pygame.draw.rect(screen_surf, bg_c_tile, tile_r, border_radius=8)
        text_s_tile = button_font_s.render(str(val_tile), True, TEXT_PRIMARY); screen_surf.blit(text_s_tile, text_s_tile.get_rect(center=tile_r.center))

def init_tiles(state_val, puzzle_top_y_offset=150):
    info_box_w_est = min(WIDTH*0.35,420)+60; puzzle_area_max_w = WIDTH-info_box_w_est-SIDEBAR_MARGIN
    puzzle_area_w = min(WIDTH*0.58, puzzle_area_max_w)
    
    slider_total_h = SLIDER_PUZZLE_AREA_MARGIN_TOP + SLIDER_HANDLE_HEIGHT + 15
    actual_puzzle_top_y = puzzle_top_y_offset + slider_total_h
    
    bottom_controls_h_approx = 130
    puzzle_area_h = HEIGHT - actual_puzzle_top_y - bottom_controls_h_approx
    
    tile_s = min(puzzle_area_w/3, puzzle_area_h/3)*0.97
    tile_s = int(tile_s)
    puzzle_grid_w = tile_s*3
    
    puzzle_area_start_x_pos = SIDEBAR_MARGIN
    start_x_pos = puzzle_area_start_x_pos + (puzzle_area_w - puzzle_grid_w) / 2
    start_y_pos = actual_puzzle_top_y + (puzzle_area_h - puzzle_grid_w) / 2
    start_y_pos = max(actual_puzzle_top_y, start_y_pos)

    tiles_l = [AnimatedTile(val, start_x_pos+c*tile_s, start_y_pos+r*tile_s, tile_s) for i,val in enumerate(state_val) for r,c in [divmod(i,3)]]
    for t_obj in tiles_l:
        try:
            current_idx_in_state = list(state_val).index(t_obj.value) if t_obj.value in state_val else -1
            t_obj.is_solved_position = (t_obj.value!=9 and current_idx_in_state !=-1 and GOAL_STATE[current_idx_in_state] == t_obj.value)
        except (ValueError, IndexError):
            t_obj.is_solved_position = False

    return tiles_l, start_x_pos, start_y_pos, puzzle_grid_w, tile_s


def update_tiles(tiles_list, new_state, goal_state, puzzle_start_x, puzzle_start_y, tile_size_val):
    if not tiles_list: return
    value_pos_map = {val: i for i, val in enumerate(new_state)}
    for tile_obj in tiles_list:
        if tile_obj.value in value_pos_map:
            new_index = value_pos_map[tile_obj.value]; row, col = divmod(new_index, 3)
            tile_obj.set_target(puzzle_start_x + col*tile_size_val, puzzle_start_y + row*tile_size_val)
            tile_obj.is_solved_position = (tile_obj.value!=9 and new_index < len(goal_state) and tile_obj.value==goal_state[new_index])


def draw_info_box(screen_surf, title_render_font, content_font_s, steps, path_len, curr_step, total_steps_val, algo_name, el_time=None, box_r=None):
    info_box_r = box_r or pygame.Rect(WIDTH-min(WIDTH*0.35,420)-60, 130, min(WIDTH*0.35,420),360)
    pygame.draw.rect(screen_surf, SIDEBAR_BG, info_box_r, border_radius=14)
    inner_bg_c = (SIDEBAR_BG[0]-10, SIDEBAR_BG[1]-10, SIDEBAR_BG[2]-10)
    pygame.draw.rect(screen_surf, tuple(max(0,c) for c in inner_bg_c), info_box_r.inflate(-8,-8), border_radius=11)

    title_s_obj = title_render_font.render("Thông tin giải", True, ACCENT_COLOR if ACCENT_COLOR else PRIMARY)
    title_r_val = title_s_obj.get_rect(centerx=info_box_r.centerx, y=info_box_r.y+25); screen_surf.blit(title_s_obj, title_r_val)

    algo_name_disp = truncate_text(algo_name if algo_name else "N/A", content_font_s, info_box_r.width-60)
    info_lines_c = [f"Thuật toán: {algo_name_disp}", f"Node đã duyệt: {steps if steps is not None else 'N/A'}",
                    f"Độ dài đường đi: {path_len if path_len is not None else 'N/A'}",
                    f"Bước hiện tại: {curr_step}/{total_steps_val if total_steps_val is not None else 'N/A'}"]
    if el_time is not None: info_lines_c.append(f"Thời gian tìm: {el_time:.3f} giây")

    line_y_s = info_box_r.y + title_r_val.height + 45
    for txt_line in info_lines_c:
        line_s_obj = content_font_s.render(txt_line, True, TEXT_SECONDARY)
        screen_surf.blit(line_s_obj, (info_box_r.x+30, line_y_s)); line_y_s += content_font_s.get_height() + 9

    if total_steps_val is not None and total_steps_val > 0:
        prog_r_bg = pygame.Rect(info_box_r.x+30, info_box_r.bottom-80, info_box_r.width-60,28)
        pygame.draw.rect(screen_surf, tuple(max(0,c-15) for c in SIDEBAR_ITEM_BG), prog_r_bg, border_radius=14)
        prog_ratio = min(1.0, max(0.0, curr_step/total_steps_val if total_steps_val > 0 else 0))
        prog_w = int(prog_ratio * prog_r_bg.width)
        if prog_w > 0: pygame.draw.rect(screen_surf, PRIMARY, pygame.Rect(prog_r_bg.x,prog_r_bg.y,prog_w,prog_r_bg.height), border_radius=14)

def draw_path_display_box(screen_surf, title_render_font, text_font_s, path_list, curr_step_idx, box_r):
    if not path_list or not box_r or box_r.height < MIN_PATH_BOX_HEIGHT//2: return
    pygame.draw.rect(screen_surf, SIDEBAR_BG, box_r, border_radius=14)
    inner_bg_c = (SIDEBAR_BG[0]-10, SIDEBAR_BG[1]-10, SIDEBAR_BG[2]-10)
    pygame.draw.rect(screen_surf, tuple(max(0,c) for c in inner_bg_c), box_r.inflate(-8,-8), border_radius=11)

    box_title_s = title_render_font.render("Các bước giải", True, ACCENT_COLOR if ACCENT_COLOR else PRIMARY)
    box_title_r_val = box_title_s.get_rect(centerx=box_r.centerx, y=box_r.y+PATH_DISPLAY_BOX_PADDING+8); screen_surf.blit(box_title_s, box_title_r_val)
    line_y_pos = box_title_r_val.bottom + 20

    num_before = (PATH_DISPLAY_MAX_VISIBLE_STEPS-1)//2;
    start_idx = max(0, curr_step_idx-num_before);
    if curr_step_idx >= len(path_list) -1 and len(path_list) > 0 :
        start_idx = max(0, len(path_list) - PATH_DISPLAY_MAX_VISIBLE_STEPS)

    end_idx = min(len(path_list), start_idx+PATH_DISPLAY_MAX_VISIBLE_STEPS)
    if end_idx-start_idx < PATH_DISPLAY_MAX_VISIBLE_STEPS and start_idx > 0:
        start_idx = max(0, end_idx-PATH_DISPLAY_MAX_VISIBLE_STEPS)


    for step_idx_show in range(start_idx, end_idx):
        state_str_val = str(path_list[step_idx_show]); text_c = TEXT_SECONDARY; prefix_str = f"B{step_idx_show+1}: "
        item_bg_c = None
        if step_idx_show == curr_step_idx: prefix_str=f"Hiện tại ({step_idx_show+1}): "; text_c=TEXT_PRIMARY; item_bg_c=PRIMARY_DARK

        full_txt = f"{prefix_str}{state_str_val}"; available_w = box_r.width - 2*(PATH_DISPLAY_BOX_PADDING+10)
        disp_txt = truncate_text(full_txt, text_font_s, available_w)
        temp_s = text_font_s.render(disp_txt, True, text_c)

        text_draw_r = temp_s.get_rect(left=box_r.x+PATH_DISPLAY_BOX_PADDING+10, top=line_y_pos)
        if text_draw_r.bottom > box_r.bottom - PATH_DISPLAY_BOX_PADDING: break

        if item_bg_c:
            bg_r = pygame.Rect(box_r.x+PATH_DISPLAY_BOX_PADDING, line_y_pos-3, box_r.width-2*PATH_DISPLAY_BOX_PADDING, text_font_s.get_height()+6)
            pygame.draw.rect(screen_surf, item_bg_c, bg_r, border_radius=7)
        screen_surf.blit(temp_s, text_draw_r); line_y_pos += text_font_s.get_height() + PATH_DISPLAY_LINE_SPACING + 4

def init_editor_tiles(state_val, offset_x_val, offset_y_val, tile_s_val):
    return [AnimatedTile(val,offset_x_val+c*tile_s_val,offset_y_val+r*tile_s_val,tile_s_val) for i,val in enumerate(state_val) for r,c in [divmod(i,3)]]

def draw_editor(screen_surf, editor_tiles_l, editor_state_l, sel_idx, title_f, general_font, info_f_editor, puzzle_f_editor, button_f_editor):
    title_s = title_f.render("Chỉnh sửa trạng thái ban đầu", True, ACCENT_COLOR if ACCENT_COLOR else PRIMARY)
    title_r_val = title_s.get_rect(centerx=WIDTH//2, y=75); screen_surf.blit(title_s, title_r_val)

    instr_list = ["Click ô để chọn, nhập số (1-9).", "Số nhập sẽ đổi chỗ với số hiện tại.", "Phải đủ 1-9 và giải được.", "ENTER để lưu, ESC để hủy."]
    instr_y_s = title_r_val.bottom + 45; instr_max_w = WIDTH*0.8; current_instr_y_val = instr_y_s
    for txt_instr in instr_list: current_instr_y_val += render_text_wrapped(txt_instr, info_f_editor, TEXT_SECONDARY, instr_max_w, screen_surf, 0, current_instr_y_val, line_spacing=7, center_x=True, rect_to_center_in=screen_surf.get_rect())

    if not editor_tiles_l: return None, None
    tile_s = editor_tiles_l[0].size; puzzle_w = tile_s*3; puzzle_h = tile_s*3
    grid_x_pos = (WIDTH-puzzle_w)//2; grid_y_pos = current_instr_y_val + 35

    for i, tile_o in enumerate(editor_tiles_l):
         r,c = divmod(i,3); tile_o.rect.topleft=(grid_x_pos+c*tile_s, grid_y_pos+r*tile_s); tile_o.inner_rect.center = tile_o.rect.center
         if tile_o.value == 9: continue
         bg_c_tile = NUMBER_TILE_COLORS.get(tile_o.value, TILE_BG_DEFAULT); pygame.draw.rect(screen_surf, bg_c_tile, tile_o.inner_rect, border_radius=tile_o.border_radius)
         text_s_tile = puzzle_f_editor.render(str(tile_o.value), True, TEXT_PRIMARY); screen_surf.blit(text_s_tile, text_s_tile.get_rect(center=tile_o.inner_rect.center))
         if i == sel_idx: pygame.draw.rect(screen_surf, PRIMARY, tile_o.inner_rect.inflate(10,10), border_radius=tile_o.border_radius+3, width=5)

    is_val = is_valid_puzzle_state(editor_state_l); solvable_flag = is_solvable(tuple(editor_state_l)) if is_val else False
    status_txt = "Không hợp lệ (thiếu/trùng số)" if not is_val else f"Trạng thái {'GIẢI ĐƯỢC' if solvable_flag else 'KHÔNG GIẢI ĐƯỢC'}"
    status_c = ERROR_COLOR if not is_val or not solvable_flag else PRIMARY
    status_s = general_font.render(status_txt, True, status_c); status_r_val = status_s.get_rect(center=(WIDTH//2, grid_y_pos+puzzle_h+55)); screen_surf.blit(status_s, status_r_val)

    btn_w, btn_h = 190, 50; btn_y_pos = status_r_val.bottom + 45
    btn_y_pos = min(btn_y_pos, HEIGHT - btn_h - 30)

    save_btn_obj = Button(WIDTH//2-btn_w-20, btn_y_pos, btn_w,btn_h, "Lưu (Enter)")
    cancel_btn_obj = Button(WIDTH//2+20, btn_y_pos, btn_w,btn_h, "Hủy (Esc)")
    save_btn_obj.check_hover(pygame.mouse.get_pos()); cancel_btn_obj.check_hover(pygame.mouse.get_pos())
    save_btn_obj.draw(screen_surf,button_f_editor); cancel_btn_obj.draw(screen_surf,button_f_editor)
    return save_btn_obj, cancel_btn_obj

def draw_single_puzzle(screen_surf, state_list, x_pos, y_pos, tile_s_val, font_s_val):
    pad = max(2, int(tile_s_val*0.04)); inner_s = tile_s_val-2*pad; radius = max(4, int(inner_s*0.12))
    for i, val_tile in enumerate(state_list):
        r,c = divmod(i,3); tx,ty = x_pos+c*tile_s_val+pad, y_pos+r*tile_s_val+pad
        if val_tile == 9: continue
        tile_r = pygame.Rect(tx,ty,inner_s,inner_s); bg_c_tile = NUMBER_TILE_COLORS.get(val_tile, TILE_BG_DEFAULT)
        pygame.draw.rect(screen_surf, bg_c_tile, tile_r, border_radius=radius)
        text_s_tile = font_s_val.render(str(val_tile), True, TEXT_PRIMARY); screen_surf.blit(text_s_tile, text_s_tile.get_rect(center=tile_r.center))

def draw_blind_preview(screen_surf, title_f, general_font, info_f_preview, button_f_preview, puzzle_f_preview, state1_val, state2_val, start_btn_obj, back_btn_obj):
    title_s = title_f.render("Xem trước Tìm kiếm Mù", True, ACCENT_COLOR if ACCENT_COLOR else PRIMARY)
    title_r_val = title_s.get_rect(centerx=WIDTH//2, y=65); screen_surf.blit(title_s, title_r_val)

    expl_lines = ["Hai ví dụ về trạng thái ban đầu.", "Tìm kiếm thực tế sẽ tạo ngẫu nhiên.", "Nhấn 'Bắt đầu' để chạy tìm kiếm mù."]
    instr_y_s = title_r_val.bottom + 45; instr_max_w = WIDTH*0.85; current_instr_y_val = instr_y_s
    for txt_instr in expl_lines: current_instr_y_val += render_text_wrapped(txt_instr, info_f_preview, TEXT_SECONDARY, instr_max_w, screen_surf, 0, current_instr_y_val, line_spacing=7, center_x=True, rect_to_center_in=screen_surf.get_rect())

    max_ts = 170; preview_ts = min(WIDTH*0.18, HEIGHT*0.24, max_ts); preview_ts = int(preview_ts)
    puzzle_s_val = preview_ts*3
    total_w_need = puzzle_s_val*2 + 160; start_puzzles_x_pos = (WIDTH-total_w_need)//2
    p1_x = start_puzzles_x_pos; p2_x = start_puzzles_x_pos + puzzle_s_val + 160; puzzles_y_pos = current_instr_y_val + 45

    draw_single_puzzle(screen_surf,state1_val,p1_x,puzzles_y_pos,preview_ts,puzzle_f_preview); draw_single_puzzle(screen_surf,state2_val,p2_x,puzzles_y_pos,preview_ts,puzzle_f_preview)

    lbl1_s = general_font.render("Ví dụ 1",True,TEXT_PRIMARY); lbl2_s = general_font.render("Ví dụ 2",True,TEXT_PRIMARY)
    screen_surf.blit(lbl1_s, lbl1_s.get_rect(centerx=p1_x+puzzle_s_val//2, bottom=puzzles_y_pos-20)); screen_surf.blit(lbl2_s, lbl2_s.get_rect(centerx=p2_x+puzzle_s_val//2, bottom=puzzles_y_pos-20))

    btn_y_val = puzzles_y_pos + puzzle_s_val + 65
    btn_y_val = min(btn_y_val, HEIGHT - start_btn_obj.rect.height - 30)

    start_btn_obj.rect.centerx = WIDTH//2 - start_btn_obj.rect.width//2 - 25; start_btn_obj.rect.y = btn_y_val
    back_btn_obj.rect.centerx = WIDTH//2 + back_btn_obj.rect.width//2 + 25; back_btn_obj.rect.y = btn_y_val
    start_btn_obj.check_hover(pygame.mouse.get_pos()); back_btn_obj.check_hover(pygame.mouse.get_pos()); start_btn_obj.draw(screen_surf,button_f_preview); back_btn_obj.draw(screen_surf,button_f_preview)

def start_solving(sel_algo_idx, start_st, goal_st, msg_box_obj):
    global current_view, path, steps_found, elapsed_time, tiles, current_step, last_switch, puzzle_layout_info
    if not is_valid_puzzle_state(start_st): msg_box_obj.title="Lỗi"; msg_box_obj.message=f"Trạng thái đầu không hợp lệ:\n{start_st}"; msg_box_obj.active=True; return False
    if not is_solvable(start_st): msg_box_obj.title="Lỗi"; msg_box_obj.message=f"Trạng thái đầu không giải được:\n{start_st}"; msg_box_obj.active=True; return False

    if not ALGORITHM_LIST or not (0 <= sel_algo_idx < len(ALGORITHM_LIST)):
        msg_box_obj.title="Lỗi"; msg_box_obj.message="Lỗi danh sách thuật toán hoặc chỉ số không hợp lệ."; msg_box_obj.active=True; return False
    algo_name, mod_name = ALGORITHM_LIST[sel_algo_idx]; print(f"Giải bằng: {algo_name}, Trạng thái: {start_st}")

    try:
        mod = importlib.import_module(f"algorithms.{mod_name}"); start_t = time.time(); res = mod.solve(start_st,goal_st); elapsed_time = time.time()-start_t
        path, steps_found = (res[0], res[1] if len(res)>1 and isinstance(res[1],int) else None) if isinstance(res,tuple) and res else (res,None) if isinstance(res,list) else (None,None)
        if path and isinstance(path,list) and path:
            path_len = len(path)-1; print(f"Tìm thấy: {path_len} bước. Thời gian: {elapsed_time:.3f}s."); steps_found = steps_found or path_len
            current_view="solver";
            tiles,px,py,pw,pts = init_tiles(start_st, puzzle_top_y_offset = title_font.get_height() + SIDEBAR_MARGIN + 20)
            puzzle_layout_info={"x":px,"y":py,"tile_size":pts}; current_step=0; last_switch=pygame.time.get_ticks(); return True
        else: print(f"Không tìm thấy lời giải. Thời gian: {elapsed_time:.3f}s."); msg_box_obj.title="Không tìm thấy"; msg_box_obj.message=f"{algo_name} không tìm thấy đường đi."; msg_box_obj.active=True; return False
    except ImportError: msg_box_obj.title="Lỗi Import"; msg_box_obj.message=f"Không thể tải {mod_name}."; msg_box_obj.active=True; return False
    except AttributeError: msg_box_obj.title="Lỗi Thuật Toán"; msg_box_obj.message=f"{mod_name} thiếu hàm 'solve'."; msg_box_obj.active=True; return False
    except Exception as e: traceback.print_exc(); msg_box_obj.title="Lỗi Thực Thi"; msg_box_obj.message=f"Lỗi khi chạy {algo_name}:\n{str(e)}"; msg_box_obj.active=True; return False

# --- Main Function ---
def main():
    global START_STATE, screen, GOAL_STATE, WIDTH, HEIGHT, font, title_font, puzzle_font, button_font, info_font, current_view, path, steps_found, elapsed_time, tiles, current_step, last_switch, switch_time, puzzle_layout_info

    clock = pygame.time.Clock(); running = True; current_view = "menu"
    path = None; current_step = 0; auto_mode = True; last_switch = 0; switch_time = DEFAULT_ANIMATION_SPEED
    tiles = None; steps_found = None; elapsed_time = None; selected_algorithm_index = 0; puzzle_layout_info = {}
    sidebar_scroll_offset = 0; sidebar_hover_index = -1
    sidebar_rect = pygame.Rect(SIDEBAR_MARGIN, SIDEBAR_MARGIN, SIDEBAR_WIDTH, HEIGHT - 2*SIDEBAR_MARGIN)
    try: sidebar_title_h_approx = title_font.get_height() + 55
    except AttributeError:
        sidebar_title_h_approx = 95
    available_h_items = sidebar_rect.height - sidebar_title_h_approx - 30
    max_display_items = max(1, available_h_items // SIDEBAR_ITEM_HEIGHT)
    max_scroll_offset = max(0, len(ALGORITHM_LIST) - max_display_items)

    current_start_state_editor = list(START_STATE)
    editor_tile_s_val = min(WIDTH*0.45, HEIGHT*0.45)/3*0.9; editor_tile_s_val = int(editor_tile_s_val)
    editor_puzzle_w_val = editor_tile_s_val*3; editor_start_x = (WIDTH-editor_puzzle_w_val)//2; editor_start_y = 330
    editor_tiles = init_editor_tiles(current_start_state_editor, editor_start_x, editor_start_y, editor_tile_s_val)
    editor_selected_idx = -1; message_box_obj = MessageBox(580, 320, "Thông báo", "")

    speed_slider = SpeedSlider(SLIDER_HANDLE_WIDTH, SLIDER_HANDLE_HEIGHT, TEXT_PLACEHOLDER, PRIMARY, MIN_ANIMATION_SPEED, MAX_ANIMATION_SPEED, DEFAULT_ANIMATION_SPEED)

    solver_btn_w, solver_btn_h, solver_btn_spacing = 145, 50, 30
    btns_total_w = 4*solver_btn_w + 3*solver_btn_spacing

    solver_btns_y = HEIGHT - 95
    auto_btn = Button(0, solver_btns_y, solver_btn_w, solver_btn_h, "Tự động: Bật")
    next_btn = Button(0, solver_btns_y, solver_btn_w, solver_btn_h, "Tiếp theo")
    reset_btn = Button(0, solver_btns_y, solver_btn_w, solver_btn_h, "Làm lại")
    back_menu_btn = Button(0, solver_btns_y, solver_btn_w, solver_btn_h, "Về Menu")


    menu_btn_w, menu_btn_h = 320, 58
    solve_btn = Button(0,0,menu_btn_w,menu_btn_h,"Bắt đầu"); edit_btn = Button(0,0,menu_btn_w,menu_btn_h,"Chỉnh sửa")
    blind_search_btn = Button(0,0,menu_btn_w,menu_btn_h,"Tìm kiếm mù"); fill_anim_btn = Button(0,0,menu_btn_w,menu_btn_h,"Hoạt ảnh điền số")
    editor_save_btn, editor_cancel_btn = None,None
    BLIND_PREVIEW_ST1, BLIND_PREVIEW_ST2 = (1,2,3,4,5,6,7,9,8), (1,2,3,4,5,9,7,8,6)
    blind_prev_btn_w, blind_prev_btn_h = 270, 58
    start_blind_run_btn = Button(0,0,blind_prev_btn_w,blind_prev_btn_h,"Bắt đầu Tìm kiếm mù"); back_menu_preview_btn = Button(0,0,210,blind_prev_btn_h,"Về Menu")
    mouse_was_down_flag = False

    while running:
        mouse_pos_val = pygame.mouse.get_pos(); current_mouse_down_val = pygame.mouse.get_pressed()[0]; mouse_click_frame = False
        for event_item in pygame.event.get():
            if event_item.type == pygame.QUIT: running=False
            if event_item.type == pygame.MOUSEBUTTONDOWN and event_item.button == 1: mouse_click_frame=True
            if message_box_obj.active and message_box_obj.handle_event(event_item): continue
            if current_view == "solver": speed_slider.handle_event(event_item, mouse_pos_val)
            if current_view == "menu":
                if event_item.type == pygame.MOUSEWHEEL and sidebar_rect.collidepoint(mouse_pos_val):
                    sidebar_scroll_offset -= event_item.y * 2; sidebar_scroll_offset = max(0,min(sidebar_scroll_offset,max_scroll_offset))
                if event_item.type == pygame.KEYDOWN:
                    if ALGORITHM_LIST :
                        if event_item.key == pygame.K_DOWN: selected_algorithm_index = min(selected_algorithm_index+1, len(ALGORITHM_LIST)-1)
                        elif event_item.key == pygame.K_UP: selected_algorithm_index = max(selected_algorithm_index-1,0)

                        if selected_algorithm_index >= sidebar_scroll_offset+max_display_items: sidebar_scroll_offset = selected_algorithm_index-max_display_items+1
                        elif selected_algorithm_index < sidebar_scroll_offset: sidebar_scroll_offset = selected_algorithm_index
                        sidebar_scroll_offset = max(0,min(sidebar_scroll_offset,max_scroll_offset))
            if event_item.type == pygame.KEYDOWN:
                if event_item.key == pygame.K_ESCAPE:
                    if current_view=="editor" or current_view=="blind_preview": current_view="menu"
                    elif current_view=="solver": current_view="menu";path=None;tiles=None;speed_slider.active=False
                    else: running=False
                elif current_view=="editor":
                    if event_item.key in [pygame.K_RETURN, pygame.K_KP_ENTER]:
                        if is_valid_puzzle_state(current_start_state_editor) and is_solvable(tuple(current_start_state_editor)): START_STATE=tuple(current_start_state_editor); current_view="menu"
                        else: message_box_obj.title="Lỗi"; message_box_obj.message="Trạng thái không hợp lệ hoặc không giải được."; message_box_obj.active=True
                    elif editor_selected_idx!=-1 and pygame.K_1<=event_item.key<=pygame.K_9:
                        new_n=event_item.key-pygame.K_0; curr_n=current_start_state_editor[editor_selected_idx]
                        if new_n!=9 and new_n!=curr_n:
                            try:
                                 swap_i=current_start_state_editor.index(new_n); current_start_state_editor[swap_i]=curr_n; current_start_state_editor[editor_selected_idx]=new_n
                                 editor_tiles[swap_i].value=curr_n; editor_tiles[editor_selected_idx].value=new_n
                            except ValueError: pass
                        editor_selected_idx=-1

        if not current_mouse_down_val and mouse_was_down_flag:
            all_btns_list = [solve_btn,edit_btn,blind_search_btn,fill_anim_btn,auto_btn,next_btn,reset_btn,back_menu_btn,start_blind_run_btn,back_menu_preview_btn]
            if editor_save_btn: all_btns_list.append(editor_save_btn)
            if editor_cancel_btn: all_btns_list.append(editor_cancel_btn)
            if message_box_obj.active: all_btns_list.append(message_box_obj.ok_button)
            for btn_o in all_btns_list: btn_o.y_offset = 0
        mouse_was_down_flag = current_mouse_down_val

        sidebar_hover_index = -1
        if current_view == "menu":
            speed_slider.active=False
            if sidebar_rect.collidepoint(mouse_pos_val):
                rel_y = mouse_pos_val[1] - (sidebar_rect.y + sidebar_title_h_approx)
                if rel_y >= 0:
                    hover_calc_idx = (rel_y // SIDEBAR_ITEM_HEIGHT) + sidebar_scroll_offset
                    if 0 <= hover_calc_idx < len(ALGORITHM_LIST):
                        item_y_ch = sidebar_rect.y + sidebar_title_h_approx + (hover_calc_idx - sidebar_scroll_offset) * SIDEBAR_ITEM_HEIGHT
                        item_r_ch = pygame.Rect(sidebar_rect.x+SIDEBAR_ITEM_PADDING, item_y_ch, sidebar_rect.width-2*SIDEBAR_ITEM_PADDING, SIDEBAR_ITEM_HEIGHT-SIDEBAR_ITEM_PADDING)
                        if item_r_ch.collidepoint(mouse_pos_val): sidebar_hover_index = hover_calc_idx
        elif current_view == "solver": speed_slider.active=True

        if mouse_click_frame:
            if current_view=="editor":
                if editor_save_btn and editor_save_btn.is_clicked(mouse_pos_val,True):
                    if is_valid_puzzle_state(current_start_state_editor) and is_solvable(tuple(current_start_state_editor)): START_STATE=tuple(current_start_state_editor); current_view="menu"
                    else: message_box_obj.title="Lỗi"; message_box_obj.message="Trạng thái không hợp lệ hoặc không giải được."; message_box_obj.active=True
                elif editor_cancel_btn and editor_cancel_btn.is_clicked(mouse_pos_val,True): current_view="menu"
                else:
                    new_sel_idx_editor = -1
                    for i_editor, t_editor in enumerate(editor_tiles):
                        if t_editor.rect.collidepoint(mouse_pos_val):
                            new_sel_idx_editor = i_editor
                            break
                    editor_selected_idx = new_sel_idx_editor

            elif current_view=="menu":
                if sidebar_rect.collidepoint(mouse_pos_val) and sidebar_hover_index!=-1: selected_algorithm_index = sidebar_hover_index
                elif solve_btn.is_clicked(mouse_pos_val,True): start_solving(selected_algorithm_index, START_STATE, GOAL_STATE, message_box_obj)
                elif edit_btn.is_clicked(mouse_pos_val,True): current_start_state_editor=list(START_STATE); editor_tiles=init_editor_tiles(current_start_state_editor,editor_start_x,editor_start_y,editor_tile_s_val); editor_selected_idx=-1; current_view="editor"
                elif blind_search_btn.is_clicked(mouse_pos_val,True): current_view="blind_preview"
                elif fill_anim_btn.is_clicked(mouse_pos_val,True):
                    try:
                        fill_script_path = os.path.join(os.path.dirname(__file__), "fill.py")
                        if not os.path.exists(fill_script_path):
                             message_box_obj.title="Lỗi"; message_box_obj.message=f"Không tìm thấy fill.py."; message_box_obj.active=True
                        else:
                            subprocess.Popen([sys.executable, fill_script_path])
                    except Exception as e: message_box_obj.title="Lỗi"; message_box_obj.message=f"Lỗi chạy fill.py:\n{str(e)}"; message_box_obj.active=True
            elif current_view=="blind_preview":
                if start_blind_run_btn.is_clicked(mouse_pos_val,True):
                    try:
                        import blind
                        blind.WIDTH, blind.HEIGHT = WIDTH, HEIGHT
                        blind.run_blind_search()
                        pygame.display.set_caption("8-Puzzle Solver")
                        current_view="menu"
                    except Exception as e: traceback.print_exc(); message_box_obj.title="Lỗi Tìm kiếm Mù"; message_box_obj.message=f"Lỗi:\n{str(e)}"; message_box_obj.active=True
                elif back_menu_preview_btn.is_clicked(mouse_pos_val,True): current_view="menu"
            elif current_view=="solver":
                if auto_btn.is_clicked(mouse_pos_val,True): auto_mode = not auto_mode; auto_btn.text = "Tự động: Bật" if auto_mode else "Tự động: Tắt"; last_switch = pygame.time.get_ticks()
                elif next_btn.is_clicked(mouse_pos_val,True) and not auto_mode and path and current_step < len(path)-1:
                     all_tiles_ready_manual = all(t.is_at_target() for t in tiles) if tiles else False
                     if all_tiles_ready_manual:
                        current_step+=1; update_tiles(tiles,path[current_step],GOAL_STATE,puzzle_layout_info.get("x",0),puzzle_layout_info.get("y",0),puzzle_layout_info.get("tile_size",100)); last_switch = pygame.time.get_ticks()
                elif reset_btn.is_clicked(mouse_pos_val,True) and path: current_step=0; last_switch=pygame.time.get_ticks(); update_tiles(tiles,path[0],GOAL_STATE,puzzle_layout_info.get("x",0),puzzle_layout_info.get("y",0),puzzle_layout_info.get("tile_size",100))
                elif back_menu_btn.is_clicked(mouse_pos_val,True): current_view="menu";path=None;tiles=None;speed_slider.active=False

        draw_gradient_background(screen, GRADIENT_TOP_COLOR, GRADIENT_BOTTOM_COLOR)

        if current_view == "editor": editor_save_btn, editor_cancel_btn = draw_editor(screen, editor_tiles, current_start_state_editor, editor_selected_idx, title_font, font, info_font, puzzle_font, button_font)
        elif current_view == "menu":
            draw_menu(screen, title_font, font, button_font, solve_btn, edit_btn, blind_search_btn, fill_anim_btn, START_STATE, selected_algorithm_index, sidebar_scroll_offset, sidebar_hover_index, sidebar_rect, max_display_items)
            solve_btn.check_hover(mouse_pos_val); edit_btn.check_hover(mouse_pos_val); blind_search_btn.check_hover(mouse_pos_val); fill_anim_btn.check_hover(mouse_pos_val)
        elif current_view == "blind_preview": draw_blind_preview(screen, title_font, font, info_font, button_font, puzzle_font, BLIND_PREVIEW_ST1, BLIND_PREVIEW_ST2, start_blind_run_btn, back_menu_preview_btn)
        elif current_view == "solver":
            info_box_w = min(WIDTH*0.35,420); info_box_x_default = WIDTH-info_box_w-SIDEBAR_MARGIN; info_box_y_default = title_font.get_height() + SIDEBAR_MARGIN + 20
            info_box_h = 360
            current_info_r = pygame.Rect(info_box_x_default, info_box_y_default, info_box_w, info_box_h)

            if puzzle_layout_info and 'x' in puzzle_layout_info and 'tile_size' in puzzle_layout_info :
                puzzle_end_x_val = puzzle_layout_info["x"] + puzzle_layout_info["tile_size"]*3
                right_panel_start_x_val = puzzle_end_x_val + SIDEBAR_MARGIN
                right_panel_width_val = WIDTH - right_panel_start_x_val - SIDEBAR_MARGIN

                current_info_r.x = right_panel_start_x_val + max(0, (right_panel_width_val - info_box_w) / 2)
                current_info_r.x = max(puzzle_end_x_val + 20, current_info_r.x)
                current_info_r.y = puzzle_layout_info.get("y", info_box_y_default)
                current_info_r.height = min(info_box_h, HEIGHT - current_info_r.y - SIDEBAR_MARGIN)


                solver_btns_total_width = 4 * solver_btn_w + 3 * solver_btn_spacing
                solver_btns_start_x_new = right_panel_start_x_val + max(0, (right_panel_width_val - solver_btns_total_width) / 2)
                solver_btns_start_x_new = max(puzzle_end_x_val + 20, solver_btns_start_x_new)


                auto_btn.rect.left = solver_btns_start_x_new
                next_btn.rect.left = auto_btn.rect.right + solver_btn_spacing
                reset_btn.rect.left = next_btn.rect.right + solver_btn_spacing
                back_menu_btn.rect.left = reset_btn.rect.right + solver_btn_spacing


            path_disp_x = current_info_r.x
            path_disp_y = current_info_r.bottom + PATH_DISPLAY_BOX_MARGIN_TOP
            solver_btns_top_y_val = auto_btn.rect.top
            path_disp_bottom_limit = solver_btns_top_y_val - PATH_DISPLAY_BOX_MARGIN_BOTTOM_FROM_BUTTONS
            path_disp_calc_h = path_disp_bottom_limit - path_disp_y
            path_disp_h = max(MIN_PATH_BOX_HEIGHT, path_disp_calc_h)
            current_path_disp_r = pygame.Rect(path_disp_x,path_disp_y,info_box_w,path_disp_h) if path_disp_h >= MIN_PATH_BOX_HEIGHT else None


            if tiles and puzzle_layout_info and 'x' in puzzle_layout_info and 'y' in puzzle_layout_info and 'tile_size' in puzzle_layout_info :
                puzzle_actual_w = puzzle_layout_info["tile_size"]*3
                slider_track_w = puzzle_actual_w * SLIDER_WIDTH_PERCENTAGE
                slider_track_x = puzzle_layout_info["x"] + (puzzle_actual_w-slider_track_w)/2
                slider_center_y = puzzle_layout_info["y"] - SLIDER_HANDLE_HEIGHT//2 - SLIDER_PUZZLE_AREA_MARGIN_TOP
                speed_slider.update_layout(slider_track_x, slider_center_y, slider_track_w); speed_slider.draw(screen,button_font)

            if tiles: [t.update() for t in tiles]
            now_ticks = pygame.time.get_ticks()
            if path and tiles and puzzle_layout_info and 'x' in puzzle_layout_info and 'y' in puzzle_layout_info and 'tile_size' in puzzle_layout_info:
                all_target = all(t.is_at_target() for t in tiles)
                eff_switch_t = max(1,switch_time)
                if auto_mode and current_step < len(path)-1 and all_target and (now_ticks-last_switch >= eff_switch_t):
                    current_step+=1
                    update_tiles(tiles,path[current_step],GOAL_STATE,puzzle_layout_info["x"],puzzle_layout_info["y"],puzzle_layout_info["tile_size"]);
                    last_switch=now_ticks

                [t.draw(screen,puzzle_font) for t in tiles]

            for b_obj in [auto_btn, next_btn, reset_btn, back_menu_btn]:
                b_obj.check_hover(mouse_pos_val)
                b_obj.draw(screen, button_font)

            if path and ALGORITHM_LIST and 0 <= selected_algorithm_index < len(ALGORITHM_LIST):
                algo_name_to_draw = ALGORITHM_LIST[selected_algorithm_index][0]
                draw_info_box(screen,font,info_font,steps_found,len(path)-1,current_step,len(path)-1,algo_name_to_draw,elapsed_time,current_info_r)
                if current_path_disp_r: draw_path_display_box(screen,font,info_font,path,current_step,current_path_disp_r)

        if message_box_obj.active: message_box_obj.draw(screen, title_font, font, button_font); message_box_obj.check_hover(mouse_pos_val)
        pygame.display.flip(); clock.tick(60)
    pygame.quit(); sys.exit()

if __name__ == "__main__":
    pygame.init(); pygame.font.init()
    try: scr_info=pygame.display.Info(); WIDTH,HEIGHT=scr_info.current_w,scr_info.current_h; screen=pygame.display.set_mode((WIDTH,HEIGHT),pygame.FULLSCREEN|pygame.SRCALPHA)
    except pygame.error: WIDTH,HEIGHT=1280,720; screen=pygame.display.set_mode((WIDTH,HEIGHT))
    pygame.display.set_caption("8-Puzzle Solver")

    vn_fonts = ["Tahoma","Arial","Segoe UI","Calibri","Times New Roman","Verdana","Roboto"]
    font_name_sel = pygame.font.get_default_font(); sys_fonts_list = pygame.font.get_fonts()
    for f_n in vn_fonts:
        if f_n.lower().replace(" ","") in [s.lower().replace(" ","") for s in sys_fonts_list]: font_name_sel=f_n; break
    print(f"Sử dụng font: {font_name_sel}")
    try:
        font = pygame.font.SysFont(font_name_sel, 25, bold=False)
        title_font = pygame.font.SysFont(font_name_sel, 50, bold=True)
        puzzle_font = pygame.font.SysFont(font_name_sel, 66, bold=True)
        button_font = pygame.font.SysFont(font_name_sel, 23, bold=True)
        info_font = pygame.font.SysFont(font_name_sel, 23)
    except Exception as e:
        print(f"Lỗi font ({font_name_sel}): {e}. Dùng font Pygame mặc định.")
        font=pygame.font.Font(None,27);title_font=pygame.font.Font(None,50);puzzle_font=pygame.font.Font(None,66);button_font=pygame.font.Font(None,23);info_font=pygame.font.Font(None,25)

    START_STATE = (1,8,2,9,4,3,7,6,5); GOAL_STATE = (1,2,3,4,5,6,7,8,9)
    if not is_solvable(START_STATE):
        print(f"Cảnh báo: START_STATE {START_STATE} không giải được! Sử dụng trạng thái giải được mặc định.")
        START_STATE = (1,2,3,4,5,6,7,9,8)
    main()