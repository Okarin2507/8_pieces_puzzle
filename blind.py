import pygame
import sys
import random
from collections import deque
import time

# --- Theme Colors: Blue Rose (Copied from main.py) ---
GRADIENT_TOP_COLOR = (30, 30, 70); GRADIENT_BOTTOM_COLOR = (50, 60, 100)
PRIMARY = (110, 130, 230); PRIMARY_DARK = (80, 100, 200)
ACCENT_COLOR = (200, 140, 180)
SIDEBAR_BG = (40, 50, 80)
TEXT_PRIMARY = (225, 230, 245); TEXT_SECONDARY = (180, 190, 215)
TEXT_PLACEHOLDER = (130, 140, 160)
BUTTON_SHADOW_COLOR = (20, 25, 45)
ERROR_COLOR = (230, 60, 70); WARNING_COLOR = (255, 190, 0)
NUMBER_TILE_COLORS = {
    1:(66,133,244), 2:(219,68,55), 3:(244,180,0), 4:(15,157,88),
    5:(171,71,188), 6:(255,112,67), 7:(0,172,193), 8:(255,160,0)
}
SOLVED_BORDER_COLOR = (250,250,250); SOLVED_BORDER_WIDTH = 3
TILE_BG_DEFAULT = (70,80,120)
SHAKE_BORDER_COLOR = ACCENT_COLOR
SIDEBAR_ITEM_BG = (60, 70, 110)

# --- UI Constants for Blind Search ---
PATH_LIST_WIDTH = 280
PATH_LIST_MARGIN = 20
PATH_LIST_AREA_WIDTH = PATH_LIST_WIDTH + PATH_LIST_MARGIN * 2
PATH_LIST_ITEM_HEIGHT = 40
PATH_LIST_PADDING = 5
PATH_LIST_MAX_VISIBLE_STEPS = 7
PUZZLE_AREA_HORIZONTAL_PADDING_RATIO = 0.05

# --- Animation Constants ---
SHAKE_DURATION = 200; SHAKE_MAGNITUDE = 6
DEFAULT_ANIM_SPEED_BLIND = 400
MIN_ANIM_SPEED_BLIND = 50
MAX_ANIM_SPEED_BLIND = 1500
SLIDER_TRACK_H_BLIND = 14
SLIDER_HANDLE_W_BLIND = 32
SLIDER_HANDLE_H_BLIND = 26

# --- Target Goal States ---
TARGET_GOAL_STATES = {(1,2,3,4,5,6,7,8,9), (1,4,7,2,5,8,3,6,9), (1,2,3,8,9,4,7,6,5)}
TARGET_GOAL_LIST = list(TARGET_GOAL_STATES)

WIDTH, HEIGHT = 0,0

# --- Gradient Background Function ---
def draw_gradient_background(surface, top_color, bottom_color):
    height = surface.get_height(); width = surface.get_width(); rect_strip = pygame.Rect(0,0,width,1)
    for y in range(height):
        r,g,b = [top_color[i] + (bottom_color[i]-top_color[i])*y/height for i in range(3)]
        rect_strip.top = y; pygame.draw.rect(surface, (int(r),int(g),int(b)), rect_strip)

# --- Text Helper ---
def truncate_text(text, font, max_width, ellipsis="..."):
    if not text or font.size(text)[0] <= max_width: return text
    truncated = ""
    for char in text:
        if font.size(truncated + char + ellipsis)[0] > max_width: break
        truncated += char
    return truncated + ellipsis

def render_text_wrapped(text, font, color, max_width, surf, start_x, start_y, line_spacing=5, center_x=False, rect_center_in=None):
    words = text.split(' '); lines = []; current_line = ""
    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] <= max_width: current_line = test_line
        else:
            if current_line: lines.append(current_line.strip())
            current_line = word + " "
            if font.size(current_line)[0] > max_width: lines.append(truncate_text(word,font,max_width)); current_line=""
    if current_line: lines.append(current_line.strip())
    y_off = 0
    total_height = 0
    for i, ln_txt in enumerate(lines):
        if not ln_txt: continue
        ln_surf = font.render(ln_txt, True, color)
        ln_r = ln_surf.get_rect(centerx=rect_center_in.centerx, top=start_y+y_off) if center_x and rect_center_in else ln_surf.get_rect(left=start_x, top=start_y+y_off)
        surf.blit(ln_surf, ln_r)
        current_line_height = font.get_height()
        y_off += current_line_height
        total_height += current_line_height
        if i < len(lines) -1 :
            y_off += line_spacing
            total_height += line_spacing
    return total_height


# --- Puzzle Logic Helpers ---
def get_inversions(st): st_nb=[x for x in st if x!=9]; inv=0; L=len(st_nb); [(inv:=inv+1) for i in range(L) for j in range(i+1,L) if st_nb[i]>st_nb[j]]; return inv
def is_solvable(st): return (9 in st and len(st)==9) and get_inversions(st)%2==0
def apply_move(st, mv_dir):
    s=list(st);
    try: bi=s.index(9)
    except ValueError: return None
    r,c=divmod(bi,3); dr,dc={'U':(-1,0),'D':(1,0),'L':(0,-1),'R':(0,1)}.get(mv_dir[0].upper(),(0,0))
    if dr==0 and dc==0 and mv_dir[0].upper() not in ['U','D','L','R']: return None
    nr,nc=r+dr,c+dc
    if 0<=nr<3 and 0<=nc<3: ni=nr*3+nc; s[bi],s[ni]=s[ni],s[bi]; return tuple(s)
    return None
def generate_specific_solvable_states(num_sts, max_rev_depth=10, req_start_val=1):
    gen_sts=set(); att=0; max_att=num_sts*200
    while len(gen_sts)<num_sts and att<max_att:
        att+=1; curr_st=random.choice(TARGET_GOAL_LIST); depth=random.randint(max(1,max_rev_depth//2),max_rev_depth); tmp_st=curr_st
        mvs=['Up','Down','Left','Right']; valid_seq=True
        for _ in range(depth):
            poss_next_sts={m:apply_move(tmp_st,m) for m in mvs if apply_move(tmp_st,m) is not None}
            if not poss_next_sts: valid_seq=False; break
            tmp_st=random.choice(list(poss_next_sts.values()))
        if not valid_seq: continue
        if tmp_st[0]==req_start_val and is_solvable(tmp_st): gen_sts.add(tmp_st)
    if len(gen_sts)<num_sts: print(f"Cảnh báo: Chỉ tạo {len(gen_sts)}/{num_sts} trạng thái."); return list(gen_sts)[:num_sts] if gen_sts else [(1,2,3,4,5,9,7,8,6)]
    return list(gen_sts)[:num_sts]

# --- Classes ---
class AnimatedTile:
    def __init__(self, val, x, y, s):
        self.value=val; self.size=s; self.inner_size=int(s*0.90); self.rect=pygame.Rect(x,y,s,s)
        self.inner_rect=pygame.Rect(x+(s-self.inner_size)//2,y+(s-self.inner_size)//2,self.inner_size,self.inner_size)
        self.cx,self.cy,self.tx,self.ty = float(x),float(y),float(x),float(y)
        self.speed=0.24; self.is_shaking=False; self.shake_start=0; self.shake_dur=SHAKE_DURATION; self.shake_mag=SHAKE_MAGNITUDE
        self.orig_x,self.orig_y = float(x),float(y); self.radius = max(7,int(self.inner_size*0.13))
    def set_target(self,x,y):
        if not self.is_shaking: self.tx,self.ty=float(x),float(y); self.orig_x,self.orig_y=self.cx,self.cy
    def shake(self):
        if not self.is_shaking: self.is_shaking=True; self.shake_start=pygame.time.get_ticks(); self.orig_x,self.orig_y=self.cx,self.cy; self.tx,self.ty=self.orig_x,self.orig_y
    def update(self):
        now=pygame.time.get_ticks()
        if self.is_shaking:
            el_sh = now-self.shake_start
            if el_sh>=self.shake_dur: self.is_shaking=False; self.cx,self.cy=self.orig_x,self.orig_y
            else: self.cx=self.orig_x+random.uniform(-self.shake_mag,self.shake_mag); self.cy=self.orig_y+random.uniform(-self.shake_mag,self.shake_mag)
        else:
            dx,dy = self.tx-self.cx, self.ty-self.cy
            if abs(dx)>0.5 or abs(dy)>0.5: self.cx+=dx*self.speed; self.cy+=dy*self.speed
            else: self.cx,self.cy=self.tx,self.ty
        self.rect.x,self.rect.y=int(self.cx),int(self.cy); self.inner_rect.center=self.rect.center
    def draw(self, surf, font_s, is_final_goal=False):
        if self.value == 9:
            if self.is_shaking: pygame.draw.rect(surf, SHAKE_BORDER_COLOR, self.rect.inflate(-self.size*0.08,-self.size*0.08),border_radius=self.radius-2,width=3)
            return
        bg_c = NUMBER_TILE_COLORS.get(self.value, TILE_BG_DEFAULT); pygame.draw.rect(surf,bg_c,self.inner_rect,border_radius=self.radius)
        txt_s = font_s.render(str(self.value),True,TEXT_PRIMARY); surf.blit(txt_s,txt_s.get_rect(center=self.inner_rect.center))
        if is_final_goal: pygame.draw.rect(surf,SOLVED_BORDER_COLOR,self.inner_rect,border_radius=self.radius,width=SOLVED_BORDER_WIDTH)
    def is_at_target(self): return not self.is_shaking and abs(self.cx-self.tx)<0.5 and abs(self.cy-self.ty)<0.5

class Button:
     def __init__(self,x,y,w,h,txt,col=PRIMARY,hcol=PRIMARY_DARK,shcol=BUTTON_SHADOW_COLOR):
         self.rect=pygame.Rect(x,y,w,h);self.text=txt;self.base_color=col;self.hover_color=hcol;self.shadow_color=shcol
         self.is_hovered=False;self.radius=12;self.sh_offset=4;self.y_off=0
     def draw(self,surf,font_s):
         curr_c=self.hover_color if self.is_hovered else self.base_color; sh_r=self.rect.move(self.sh_offset,self.sh_offset+self.y_off)
         pygame.draw.rect(surf,self.shadow_color,sh_r,border_radius=self.radius); btn_r=self.rect.move(0,self.y_off)
         pygame.draw.rect(surf,curr_c,btn_r,border_radius=self.radius); txt_s=font_s.render(self.text,True,TEXT_PRIMARY)
         surf.blit(txt_s,txt_s.get_rect(center=btn_r.center))
     def check_hover(self,mpos): self.is_hovered=self.rect.collidepoint(mpos); return self.is_hovered
     def is_clicked(self,mpos,mclick):
        cl=self.is_hovered and mclick
        if cl: self.y_off = self.sh_offset
        return cl

class SpeedSlider:
    def __init__(self, handle_width, handle_height, track_color, handle_color, min_val, max_val, initial_val):
        self.min_value = min_val; self.max_value = max_val; self.current_value = initial_val
        self.track_rect = pygame.Rect(0,0,0,0); self.handle_rect = pygame.Rect(0,0, handle_width, handle_height)
        self.slider_min_x = 0; self.slider_max_x = 0; self.slider_range_x = 0
        self.track_color = track_color; self.handle_color = handle_color
        self.is_dragging = False; self.active = True

    def update_layout(self, x_track_start, y_center, track_width):
        track_h = SLIDER_TRACK_H_BLIND
        self.track_rect = pygame.Rect(x_track_start, y_center - track_h // 2, track_width, track_h)
        self.slider_min_x = self.track_rect.left + self.handle_rect.width // 2
        self.slider_max_x = self.track_rect.right - self.handle_rect.width // 2
        self.slider_range_x = self.slider_max_x - self.slider_min_x
        if self.slider_range_x <= 0: self.slider_range_x = 1
        self._update_handle_pos_from_value()

    def _update_handle_pos_from_value(self):
        if not self.track_rect.height: return
        percentage = (self.current_value - self.min_value) / (self.max_value - self.min_value) if self.max_value != self.min_value else 0.5
        percentage = max(0, min(1, percentage))
        handle_center_x = self.slider_min_x + percentage * self.slider_range_x
        self.handle_rect.center = (int(handle_center_x), self.track_rect.centery)

    def _update_value_from_handle_pos(self):
        percentage = (self.handle_rect.centerx - self.slider_min_x) / self.slider_range_x if self.slider_range_x else 0
        self.current_value = self.min_value + percentage * (self.max_value - self.min_value)
        self.current_value = max(self.min_value, min(self.max_value, self.current_value))

    def handle_event(self, event, mouse_pos, time_per_move_ref_list):
        if not self.active: return False
        changed_val = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.handle_rect.collidepoint(mouse_pos) or self.track_rect.collidepoint(mouse_pos):
                self.is_dragging = True
                if self.track_rect.collidepoint(mouse_pos) and not self.handle_rect.collidepoint(mouse_pos):
                    self.handle_rect.centerx = max(self.slider_min_x, min(mouse_pos[0], self.slider_max_x))
                self._update_value_from_handle_pos(); time_per_move_ref_list[0] = int(self.current_value); changed_val = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_dragging: self.is_dragging = False; changed_val = True
        elif event.type == pygame.MOUSEMOTION and self.is_dragging:
            self.handle_rect.centerx = max(self.slider_min_x, min(mouse_pos[0], self.slider_max_x))
            self._update_value_from_handle_pos(); time_per_move_ref_list[0] = int(self.current_value); changed_val = True
        return changed_val

    def draw(self, screen_surf, font_s):
        if not self.active or not self.track_rect.height: return
        pygame.draw.rect(screen_surf, self.track_color, self.track_rect, border_radius=self.track_rect.height//2)
        pygame.draw.rect(screen_surf, self.handle_color, self.handle_rect, border_radius=7)
        speed_text = f"Tốc độ: {int(self.current_value)}ms"; text_surf = font_s.render(speed_text,True,TEXT_SECONDARY)
        text_r = text_surf.get_rect(midleft=(self.track_rect.right+20, self.track_rect.centery)); screen_surf.blit(text_surf,text_r)
        fast_lbl_s = font_s.render("Nhanh",True,TEXT_SECONDARY); slow_lbl_s = font_s.render("Chậm",True,TEXT_SECONDARY)
        screen_surf.blit(fast_lbl_s, fast_lbl_s.get_rect(midright=(self.track_rect.left-15, self.track_rect.centery)))
        screen_surf.blit(slow_lbl_s, slow_lbl_s.get_rect(midleft=(text_r.right+15, self.track_rect.centery)))
    def get_value(self): return int(self.current_value)


def find_common_path(init_beliefs, targets_set):
    if not init_beliefs: return None
    init_b_tuple = tuple(sorted(init_beliefs))
    if all(st in targets_set for st in init_b_tuple): return []
    q = deque([(init_b_tuple, [])]); visited = {init_b_tuple}
    mvs = ['Up','Down','Left','Right']; max_iter=250000; it=0
    while q:
        it+=1;
        if it>max_iter: print(f"Blind Search: Max iter {max_iter} reached."); return None
        curr_b_tuple, curr_path = q.popleft()
        for mv in mvs:
            next_b_list = [apply_move(st,mv) or st for st in curr_b_tuple]
            next_b_tuple_unsorted = [s for s in next_b_list if s is not None]
            if len(next_b_tuple_unsorted) != len(curr_b_tuple):
                 print(f"Warning: move {mv} on {curr_b_tuple} resulted in different number of states.")
                 continue
            next_b_tuple = tuple(sorted(next_b_tuple_unsorted))

            if next_b_tuple not in visited:
                if all(st in targets_set for st in next_b_tuple): return curr_path + [mv]
                visited.add(next_b_tuple); q.append((next_b_tuple, curr_path+[mv]))
    print("Blind Search: Queue exhausted."); return None

def run_blind_search():
    global WIDTH, HEIGHT; local_W, local_H = WIDTH, HEIGHT
    if not pygame.get_init(): pygame.init(); pygame.font.init()
    try:
        screen_surf = pygame.display.get_surface()
        if screen_surf is None: screen_surf = pygame.display.set_mode((local_W,local_H), pygame.FULLSCREEN if pygame.display.Info().current_w==local_W else 0)
        else: local_W,local_H = screen_surf.get_size()
        pygame.display.set_caption("Tìm kiếm Mù - 8 Puzzle")
    except pygame.error as e: print(f"Lỗi màn hình (blind): {e}."); local_W,local_H=1280,720; screen_surf = pygame.display.set_mode((local_W,local_H))

    clock = pygame.time.Clock()
    vn_fonts = ["Tahoma","Arial","Segoe UI","Calibri","Times New Roman","Verdana","Roboto"]
    font_name_sel = pygame.font.get_default_font(); sys_f_list = pygame.font.get_fonts()
    for f_n in vn_fonts:
        if f_n.lower().replace(" ","") in [s.lower().replace(" ","") for s in sys_f_list]: font_name_sel=f_n; break
    print(f"Blind.py sử dụng font: {font_name_sel}")
    try:
        font_ui = pygame.font.SysFont(font_name_sel, 25, bold=True)
        title_f = pygame.font.SysFont(font_name_sel, 44, bold=True)
        puzzle_f_small = pygame.font.SysFont(font_name_sel, 36, bold=True)
        puzzle_f_large = pygame.font.SysFont(font_name_sel, 56, bold=True)
        move_info_f = pygame.font.SysFont(font_name_sel, 30, bold=True)
        path_list_font = pygame.font.SysFont(font_name_sel, 22)
    except Exception as e:
        print(f"Lỗi font (blind.py): {e}.");
        font_ui=pygame.font.Font(None,27); title_f=pygame.font.Font(None,44); puzzle_f_small=pygame.font.Font(None,36);
        puzzle_f_large=pygame.font.Font(None,56); move_info_f=pygame.font.Font(None,30); path_list_font=pygame.font.Font(None,24)


    gui_state="generating"; init_sts_list=[]; common_path_res=None; all_anim_puzzles=[]; curr_anim_st_tuples=[]
    curr_mv_idx=0;
    time_per_move_wrapper = [DEFAULT_ANIM_SPEED_BLIND]
    last_anim_upd=0
    status_msg_display="Đang tìm cấu hình giải được..."
    num_init_sts=2; gen_max_depth=10; max_retries_val=4; retry_c=0

    btn_w, btn_h = 160, 50
    btn_margin_bottom = 30; btn_margin_right = 30

    back_btn = Button(0,0, btn_w,btn_h,"Về Menu")
    auto_mode_blind = True
    auto_btn_blind = Button(0,0, btn_w,btn_h, "Tự động: Bật")
    reset_btn_blind = Button(0,0, btn_w,btn_h, "Làm lại")
    next_btn_blind = Button(0,0, btn_w, btn_h, "Tiếp theo")

    speed_slider_blind = SpeedSlider(SLIDER_HANDLE_W_BLIND, SLIDER_HANDLE_H_BLIND, TEXT_PLACEHOLDER, PRIMARY, MIN_ANIM_SPEED_BLIND, MAX_ANIM_SPEED_BLIND, DEFAULT_ANIM_SPEED_BLIND)
    slider_active_in_blind = False

    gen_ok=False; mouse_was_down_prev_frame=False
    anim_puz_grid_s = 0
    puzzles_start_x = 0
    puzzles_start_y = 0
    puz_space = 0

    TOP_MARGIN = 60
    PUZZLE_AREA_HORIZONTAL_PADDING_PX = local_W * PUZZLE_AREA_HORIZONTAL_PADDING_RATIO
    BOTTOM_CONTROLS_AREA_HEIGHT = btn_h + btn_margin_bottom + 40

    status_msg_y_pos = TOP_MARGIN + title_f.get_height() + 20
    status_text_height = 0
    puzzle_area_top_y_calc = 0
    puzzle_area_bottom_y_calc = 0
    available_puzzle_area_h_calc = 0

    temp_surf_for_calc = pygame.Surface((1,1))

    while common_path_res is None and retry_c < max_retries_val:
        retry_c+=1; print(f"\n--- Lần thử {retry_c}/{max_retries_val} ---")
        draw_gradient_background(screen_surf, GRADIENT_TOP_COLOR, GRADIENT_BOTTOM_COLOR)
        title_s = title_f.render("Tìm kiếm Mù", True, ACCENT_COLOR if ACCENT_COLOR else PRIMARY)
        screen_surf.blit(title_s, title_s.get_rect(centerx=local_W//2, y=TOP_MARGIN))
        search_msg_txt = f"Đang tìm cấu hình... (Lần thử {retry_c})"
        render_text_wrapped(search_msg_txt, font_ui, TEXT_SECONDARY, local_W*0.8, screen_surf,0,status_msg_y_pos,line_spacing=7,center_x=True,rect_center_in=screen_surf.get_rect())
        pygame.display.flip(); pygame.time.delay(150); pygame.event.pump()

        init_sts_list = generate_specific_solvable_states(num_init_sts,gen_max_depth,1)
        if not init_sts_list: status_msg_display="Lỗi: Không tạo được trạng thái."; gui_state="no_path"; gen_ok=False; break
        gen_ok=True; common_path_res = find_common_path(init_sts_list,TARGET_GOAL_STATES)

    status_text_height = render_text_wrapped(status_msg_display,font_ui,TEXT_SECONDARY,local_W*0.85,temp_surf_for_calc,0,0,line_spacing=7,center_x=True,rect_center_in=screen_surf.get_rect())

    if common_path_res is not None:
        gui_state="animating";
        slider_active_in_blind = True
        curr_anim_st_tuples=list(init_sts_list); num_p=len(init_sts_list);

        effective_puzzle_area_width = local_W - (PATH_LIST_AREA_WIDTH if num_p > 0 else 0) - PUZZLE_AREA_HORIZONTAL_PADDING_PX * 2
        slider_total_height_needed = SLIDER_HANDLE_H_BLIND + 50

        puzzle_area_top_y_calc = TOP_MARGIN + title_f.get_height() + status_text_height + 20 + slider_total_height_needed
        puzzle_area_bottom_y_calc = local_H - BOTTOM_CONTROLS_AREA_HEIGHT - move_info_f.get_height() - 30
        available_puzzle_area_h_calc = puzzle_area_bottom_y_calc - puzzle_area_top_y_calc
        available_puzzle_area_h_calc = max(200, available_puzzle_area_h_calc)

        max_t_s,min_t_s = 150, 40

        tile_s_based_on_width = (effective_puzzle_area_width / num_p if num_p > 0 else effective_puzzle_area_width) * 0.85 / 3
        tile_s_based_on_height = available_puzzle_area_h_calc * 0.9 / 3
        anim_t_s = min(tile_s_based_on_width, tile_s_based_on_height)
        anim_t_s = max(min_t_s, min(anim_t_s, max_t_s)); anim_t_s = max(1, int(anim_t_s))


        anim_puz_grid_s = anim_t_s*3
        puz_space = anim_t_s * 0.4
        total_puzzles_width_val = num_p * anim_puz_grid_s + max(0, num_p-1) * puz_space

        puzzles_start_x_base = PUZZLE_AREA_HORIZONTAL_PADDING_PX
        puzzles_start_x = puzzles_start_x_base + (effective_puzzle_area_width - total_puzzles_width_val) / 2

        puzzles_start_y = puzzle_area_top_y_calc + (available_puzzle_area_h_calc - anim_puz_grid_s) / 2
        puzzles_start_y = max(puzzle_area_top_y_calc, puzzles_start_y)

        all_anim_puzzles = []
        for i,init_st_val in enumerate(init_sts_list):
            anim_sx=puzzles_start_x+i*(anim_puz_grid_s+puz_space); anim_sy=puzzles_start_y
            puz_ts=[AnimatedTile(val,anim_sx+c*anim_t_s,anim_sy+r_tile*anim_t_s,anim_t_s) for idx,val in enumerate(init_st_val) for r_tile,c in [divmod(idx,3)]]
            all_anim_puzzles.append(puz_ts)

        slider_track_w_val = local_W * 0.45
        slider_center_x_area = (local_W - (PATH_LIST_AREA_WIDTH if common_path_res else 0)) / 2 + (PUZZLE_AREA_HORIZONTAL_PADDING_PX if common_path_res else 0)
        slider_track_x_start = slider_center_x_area - slider_track_w_val / 2

        slider_y_center_val = TOP_MARGIN + title_f.get_height() + status_text_height + 30 + SLIDER_HANDLE_H_BLIND // 2
        speed_slider_blind.update_layout(slider_track_x_start, slider_y_center_val, slider_track_w_val)

        last_anim_upd=pygame.time.get_ticks()
    elif not gen_ok: slider_active_in_blind = False
    else: status_msg_display=f"Không tìm thấy đường đi chung sau {max_retries_val} lần thử."; gui_state="no_path"; slider_active_in_blind = False

    running_loop=True
    all_tiles_settled_current_frame = True

    while running_loop:
        mpos=pygame.mouse.get_pos(); curr_mdown=pygame.mouse.get_pressed()[0]; mclick_frame=False

        for evt in pygame.event.get():
            if evt.type==pygame.QUIT: running_loop=False
            elif evt.type==pygame.KEYDOWN and evt.key==pygame.K_ESCAPE: running_loop=False
            elif evt.type==pygame.MOUSEBUTTONDOWN and evt.button==1: mclick_frame=True

            if slider_active_in_blind:
                speed_slider_blind.handle_event(evt, mpos, time_per_move_wrapper)

            if gui_state in ["animating", "finished"] and common_path_res:
                 if mclick_frame:
                    if auto_btn_blind.is_clicked(mpos,True):
                        auto_mode_blind = not auto_mode_blind
                        auto_btn_blind.text = "Tự động: Bật" if auto_mode_blind else "Tự động: Tắt"
                        if auto_mode_blind: last_anim_upd = pygame.time.get_ticks()
                    elif reset_btn_blind.is_clicked(mpos,True):
                        curr_mv_idx = 0; last_anim_upd = pygame.time.get_ticks(); curr_anim_st_tuples=list(init_sts_list)
                        if all_anim_puzzles and init_sts_list and anim_puz_grid_s > 0 and len(all_anim_puzzles) > 0 and len(all_anim_puzzles[0]) > 0:
                             anim_t_s_val=all_anim_puzzles[0][0].size
                             for i, p_tiles in enumerate(all_anim_puzzles):
                                target_st_val = init_sts_list[i]; val_pos_map={v:idx_v for idx_v,v in enumerate(target_st_val)}
                                anim_sx=puzzles_start_x+i*(anim_puz_grid_s+puz_space); anim_sy=puzzles_start_y
                                for t_o in p_tiles:
                                    if t_o.value in val_pos_map: new_i_val=val_pos_map[t_o.value]; r_t,c_t=divmod(new_i_val,3); t_o.set_target(anim_sx+c_t*anim_t_s_val,anim_sy+r_t*anim_t_s_val)
                    elif next_btn_blind.is_clicked(mpos, True) and not auto_mode_blind and curr_mv_idx < len(common_path_res):
                        current_all_ready = True
                        if all_anim_puzzles:
                            for p_ts_list_check in all_anim_puzzles:
                                if not all(t.is_at_target() for t in p_ts_list_check if not t.is_shaking) or \
                                   any(t.value == 9 and t.is_shaking for t in p_ts_list_check):
                                    current_all_ready = False
                                    break
                        
                        if current_all_ready:
                            mv_apply=common_path_res[curr_mv_idx]; upd_indices=[]
                            for i,curr_p_st in enumerate(curr_anim_st_tuples):
                                next_s=apply_move(curr_p_st,mv_apply)
                                if next_s: curr_anim_st_tuples[i]=next_s; upd_indices.append(i)
                                else:
                                    bl_t=None
                                    if i < len(all_anim_puzzles):
                                        bl_t = next((t for t in all_anim_puzzles[i] if t.value==9),None)
                                    if bl_t: bl_t.shake()
                            if upd_indices and all_anim_puzzles and anim_puz_grid_s > 0 and len(all_anim_puzzles) > 0 and len(all_anim_puzzles[0]) > 0:
                                anim_t_s_val=all_anim_puzzles[0][0].size
                                for p_idx in upd_indices:
                                    if p_idx < len(all_anim_puzzles) and p_idx < len(curr_anim_st_tuples):
                                        anim_sx_val=puzzles_start_x+p_idx*(anim_puz_grid_s+puz_space); anim_sy_val=puzzles_start_y
                                        ts_to_upd=all_anim_puzzles[p_idx]; target_s_val=curr_anim_st_tuples[p_idx]
                                        val_pos_map={v:i_v for i_v,v in enumerate(target_s_val)}
                                        for t_o in ts_to_upd:
                                            if t_o.value in val_pos_map: new_i_val=val_pos_map[t_o.value]; r_t,c_t=divmod(new_i_val,3); t_o.set_target(anim_sx_val+c_t*anim_t_s_val,anim_sy_val+r_t*anim_t_s_val)
                            
                            curr_mv_idx+=1
                            last_anim_upd=pygame.time.get_ticks()


        if not curr_mdown and mouse_was_down_prev_frame:
            back_btn.y_off=0; auto_btn_blind.y_off=0; reset_btn_blind.y_off=0; next_btn_blind.y_off=0
        if mclick_frame and back_btn.is_clicked(mpos,True): running_loop=False
        mouse_was_down_prev_frame=curr_mdown

        all_tiles_settled_current_frame = True
        if gui_state in ["animating", "finished"] and all_anim_puzzles:
            for i,p_tiles_list in enumerate(all_anim_puzzles):
                for t_obj in p_tiles_list:
                    t_obj.update()
                    if not t_obj.is_at_target() and not t_obj.is_shaking:
                        all_tiles_settled_current_frame = False
        elif not all_anim_puzzles and gui_state in ["animating", "finished"]:
            all_tiles_settled_current_frame = True


        if gui_state == "animating" and common_path_res and curr_mv_idx < len(common_path_res):
            if auto_mode_blind and all_tiles_settled_current_frame and \
               (pygame.time.get_ticks() - last_anim_upd >= time_per_move_wrapper[0]):

                mv_apply = common_path_res[curr_mv_idx]
                upd_indices = []
                for i, curr_p_st_tuple in enumerate(curr_anim_st_tuples):
                    next_s = apply_move(curr_p_st_tuple, mv_apply)
                    if next_s:
                        curr_anim_st_tuples[i] = next_s
                        upd_indices.append(i)
                    else:
                        blank_tile_to_shake = None
                        if i < len(all_anim_puzzles):
                             blank_tile_to_shake = next((t for t in all_anim_puzzles[i] if t.value == 9), None)
                        if blank_tile_to_shake:
                            blank_tile_to_shake.shake()

                if upd_indices and all_anim_puzzles and anim_puz_grid_s > 0 and len(all_anim_puzzles) > 0 and len(all_anim_puzzles[0]) > 0:
                    anim_t_s_val = all_anim_puzzles[0][0].size
                    for p_idx in upd_indices:
                        if p_idx < len(all_anim_puzzles) and p_idx < len(curr_anim_st_tuples):
                            anim_sx_val = puzzles_start_x + p_idx * (anim_puz_grid_s + puz_space)
                            anim_sy_val = puzzles_start_y
                            tiles_to_update = all_anim_puzzles[p_idx]
                            target_state_val = curr_anim_st_tuples[p_idx]
                            value_pos_map = {v: idx_v for idx_v, v in enumerate(target_state_val)}
                            for t_obj in tiles_to_update:
                                if t_obj.value in value_pos_map:
                                    new_idx_val = value_pos_map[t_obj.value]
                                    r_t, c_t = divmod(new_idx_val, 3)
                                    t_obj.set_target(anim_sx_val + c_t * anim_t_s_val, anim_sy_val + r_t * anim_t_s_val)
                
                curr_mv_idx += 1
                last_anim_upd = pygame.time.get_ticks()


        draw_gradient_background(screen_surf, GRADIENT_TOP_COLOR, GRADIENT_BOTTOM_COLOR)
        title_txt="Kết quả Tìm kiếm Mù" if gui_state!="generating" else "Tìm kiếm Mù"
        title_s=title_f.render(title_txt,True,ACCENT_COLOR if ACCENT_COLOR else PRIMARY)
        title_rect = title_s.get_rect(centerx=local_W//2,y=TOP_MARGIN)
        screen_surf.blit(title_s,title_rect)

        current_bottom_of_text = title_rect.bottom + 20
        status_text_height_render = render_text_wrapped(status_msg_display,font_ui,TEXT_SECONDARY,local_W*0.85,screen_surf,0,current_bottom_of_text,line_spacing=7,center_x=True,rect_center_in=screen_surf.get_rect())
        current_bottom_of_text += status_text_height_render

        back_btn.rect.bottomright = (local_W - btn_margin_right, local_H - btn_margin_bottom)
        back_btn.check_hover(mpos); back_btn.draw(screen_surf,font_ui)

        if gui_state=="no_path":
            if gen_ok and init_sts_list:
                available_height_for_no_path_grid = local_H - current_bottom_of_text - (back_btn.rect.height + btn_margin_bottom + 40)
                available_height_for_no_path_grid = max(200, available_height_for_no_path_grid)
                grid_cols_val=min(len(init_sts_list),2);
                grid_rows_val=(len(init_sts_list)+grid_cols_val-1)//grid_cols_val

                puz_w_per_col_no_path = (local_W * 0.70) / grid_cols_val
                puz_h_per_row_no_path = available_height_for_no_path_grid / grid_rows_val
                tile_s_val = min(puz_w_per_col_no_path * 0.85 / 3, puz_h_per_row_no_path * 0.85 / 3)
                tile_s_val = max(40, min(tile_s_val, 120))
                tile_s_val = int(tile_s_val)


                actual_puzzle_grid_width = tile_s_val * 3
                actual_puzzle_grid_height = tile_s_val * 3

                h_spacing_between_puzzles = tile_s_val
                total_preview_grid_width = grid_cols_val * actual_puzzle_grid_width + max(0, grid_cols_val-1) * h_spacing_between_puzzles
                total_preview_grid_height = grid_rows_val * actual_puzzle_grid_height + max(0, grid_rows_val-1) * (h_spacing_between_puzzles / 2)

                start_x_grid_val = (local_W - total_preview_grid_width) / 2
                start_y_grid_val = current_bottom_of_text + 20 + (available_height_for_no_path_grid - total_preview_grid_height) / 2
                start_y_grid_val = max(current_bottom_of_text + 20, start_y_grid_val)

                for i,init_st in enumerate(init_sts_list):
                    r_idx,c_idx=divmod(i,grid_cols_val)
                    px = start_x_grid_val + c_idx*(actual_puzzle_grid_width + h_spacing_between_puzzles)
                    py = start_y_grid_val + r_idx*(actual_puzzle_grid_height + h_spacing_between_puzzles / 2)
                    for idx,val_t in enumerate(init_st):
                        r_tile,c_tile=divmod(idx,3); xt,yt=px+c_tile*tile_s_val,py+r_tile*tile_s_val
                        if val_t==9: continue
                        pad_val=max(1,int(tile_s_val*0.03)); inner_s_val=tile_s_val-2*pad_val
                        rect_t_val=pygame.Rect(xt+pad_val,yt+pad_val,inner_s_val,inner_s_val)
                        bg_color_val=NUMBER_TILE_COLORS.get(val_t,TILE_BG_DEFAULT)
                        pygame.draw.rect(screen_surf,bg_color_val,rect_t_val,border_radius=max(4,int(inner_s_val*0.1)))
                        screen_surf.blit(puzzle_f_small.render(str(val_t),True,TEXT_PRIMARY),puzzle_f_small.render(str(val_t),True,TEXT_PRIMARY).get_rect(center=rect_t_val.center))

        elif gui_state in ["animating","finished"]:
            slider_y_center_pos = current_bottom_of_text + 20 + SLIDER_HANDLE_H_BLIND // 2
            if slider_active_in_blind :
                effective_path_list_width = PATH_LIST_AREA_WIDTH if common_path_res else 0
                slider_w_area = local_W - effective_path_list_width - PUZZLE_AREA_HORIZONTAL_PADDING_PX * 2
                slider_track_w_val = min(slider_w_area * 0.7, local_W * 0.45)

                slider_x_base = PUZZLE_AREA_HORIZONTAL_PADDING_PX if common_path_res and num_p > 0 else 0
                slider_track_x_start = slider_x_base + (slider_w_area - slider_track_w_val) / 2
                if not common_path_res or num_p == 0:
                    slider_track_x_start = (local_W - slider_track_w_val) / 2

                speed_slider_blind.update_layout(slider_track_x_start, slider_y_center_pos, slider_track_w_val)
                speed_slider_blind.draw(screen_surf, font_ui)

            if all_anim_puzzles:
                for i,p_tiles_list_draw in enumerate(all_anim_puzzles):
                    p_st = curr_anim_st_tuples[i] if i < len(curr_anim_st_tuples) else None
                    is_this_p_goal = (gui_state=="finished" or (gui_state=="animating" and common_path_res and curr_mv_idx==len(common_path_res))) and \
                                     (p_st and p_st in TARGET_GOAL_STATES)
                    for t_obj_draw in p_tiles_list_draw:
                        is_t_final_pos=False
                        if is_this_p_goal and p_st:
                            try: curr_idx_t=list(p_st).index(t_obj_draw.value)
                            except ValueError: curr_idx_t=-1
                            if curr_idx_t!=-1 and t_obj_draw.value!=9 and p_st[curr_idx_t]==t_obj_draw.value: is_t_final_pos=True
                        t_obj_draw.draw(screen_surf,puzzle_f_large,is_t_final_pos)


            path_list_rect = None
            max_path_list_h = 0
            if common_path_res:
                path_list_top_y = TOP_MARGIN + title_f.get_height() + 20
                max_path_list_h = local_H - path_list_top_y - (btn_h + btn_margin_bottom + 20)
                path_list_actual_h = min(PATH_LIST_MAX_VISIBLE_STEPS * PATH_LIST_ITEM_HEIGHT + PATH_LIST_PADDING * 2 + font_ui.get_height() + 20, max_path_list_h)

                path_list_rect = pygame.Rect(local_W - PATH_LIST_AREA_WIDTH + PATH_LIST_MARGIN, path_list_top_y, PATH_LIST_WIDTH, path_list_actual_h)

                pygame.draw.rect(screen_surf, SIDEBAR_BG, path_list_rect, border_radius=10)
                path_title_s = font_ui.render("Các Bước Đi", True, TEXT_PRIMARY)
                path_title_r = path_title_s.get_rect(centerx=path_list_rect.centerx, top=path_list_rect.top + 10)
                screen_surf.blit(path_title_s, path_title_r)

                path_item_y = path_title_r.bottom + 10
                num_before = (PATH_LIST_MAX_VISIBLE_STEPS -1) // 2
                start_display_idx_path = max(0, curr_mv_idx - num_before)
                if curr_mv_idx == len(common_path_res) and len(common_path_res) > 0:
                    start_display_idx_path = max(0, curr_mv_idx - 1 - num_before)


                end_display_idx_path = min(len(common_path_res), start_display_idx_path + PATH_LIST_MAX_VISIBLE_STEPS)
                if end_display_idx_path - start_display_idx_path < PATH_LIST_MAX_VISIBLE_STEPS:
                    start_display_idx_path = max(0, end_display_idx_path - PATH_LIST_MAX_VISIBLE_STEPS)


                for i in range(start_display_idx_path, end_display_idx_path):
                    if path_item_y + PATH_LIST_ITEM_HEIGHT > path_list_rect.bottom - PATH_LIST_PADDING: break
                    move_str = f"B {i+1}: {common_path_res[i]}"
                    item_r = pygame.Rect(path_list_rect.x + PATH_LIST_PADDING, path_item_y, path_list_rect.width - 2*PATH_LIST_PADDING, PATH_LIST_ITEM_HEIGHT - PATH_LIST_PADDING)
                    
                    is_current_highlight = (i == curr_mv_idx)
                    if curr_mv_idx == len(common_path_res) and i == len(common_path_res) -1 :
                         is_current_highlight = True
                    
                    item_bg_c = PRIMARY_DARK if is_current_highlight else SIDEBAR_ITEM_BG
                    pygame.draw.rect(screen_surf, item_bg_c, item_r, border_radius=6)
                    move_text_surf = path_list_font.render(truncate_text(move_str, path_list_font, item_r.width - 10), True, TEXT_PRIMARY)
                    screen_surf.blit(move_text_surf, move_text_surf.get_rect(midleft=(item_r.left + 10, item_r.centery)))
                    path_item_y += PATH_LIST_ITEM_HEIGHT

            control_btn_y_pos = local_H - btn_margin_bottom - btn_h
            control_btn_spacing = 20

            all_control_buttons = [auto_btn_blind, next_btn_blind, reset_btn_blind]
            total_control_btns_width_current = sum(b.rect.width for b in all_control_buttons) + max(0, len(all_control_buttons)-1) * control_btn_spacing

            control_area_w = local_W - (PATH_LIST_AREA_WIDTH if common_path_res else 0) - PUZZLE_AREA_HORIZONTAL_PADDING_PX * 2
            control_btns_start_x_pos = (PUZZLE_AREA_HORIZONTAL_PADDING_PX if common_path_res else 0) + (control_area_w - total_control_btns_width_current) / 2
            control_btns_start_x_pos = max(PUZZLE_AREA_HORIZONTAL_PADDING_PX if common_path_res else 20, control_btns_start_x_pos)


            current_x_btn = control_btns_start_x_pos
            for btn in all_control_buttons:
                btn.rect.topleft = (current_x_btn, control_btn_y_pos)
                btn.check_hover(mpos); btn.draw(screen_surf, font_ui)
                current_x_btn += btn.rect.width + control_btn_spacing

            move_text_y_final_pos = control_btn_y_pos - move_info_f.get_height() - 15
            move_text_center_x_pos = control_btns_start_x_pos + total_control_btns_width_current / 2

            if common_path_res:
                mv_txt_disp=""; final_step_comp=(gui_state=="finished" or (gui_state=="animating" and curr_mv_idx==len(common_path_res)))
                all_puz_goal = all(st in TARGET_GOAL_STATES for st in curr_anim_st_tuples)

                if curr_mv_idx < len(common_path_res):
                    mv_txt_disp=f"Bước {curr_mv_idx+1}/{len(common_path_res)}: {common_path_res[curr_mv_idx]}"
                elif final_step_comp and all_puz_goal: mv_txt_disp=f"Đã đạt đích! ({len(common_path_res)} Bước)"
                elif final_step_comp: mv_txt_disp="Hoàn thành (Lỗi trạng thái cuối)"
                if mv_txt_disp:
                    txt_c_mv=ERROR_COLOR if "Lỗi" in mv_txt_disp else (PRIMARY if (final_step_comp and all_puz_goal) else TEXT_PRIMARY)
                    mv_s=move_info_f.render(mv_txt_disp,True,txt_c_mv)
                    screen_surf.blit(mv_s,mv_s.get_rect(center=(move_text_center_x_pos,move_text_y_final_pos)))

            if gui_state=="animating" and common_path_res and curr_mv_idx==len(common_path_res) and all_tiles_settled_current_frame:
                if not any(t.is_shaking for p_ts_list in all_anim_puzzles for t in p_ts_list):
                    if all_puz_goal: gui_state="finished"; status_msg_display=f"Tất cả trạng thái đã đạt đích!"
                    else: gui_state="finished"; status_msg_display=f"Hoàn thành (Một số trạng thái có thể chưa đạt đích chính xác!)"
        pygame.display.flip(); clock.tick(60)
    print("Thoát tìm kiếm mù.")

if __name__=="__main__":
    pygame.init(); pygame.font.init();
    try:
        s_info = pygame.display.Info()
        WIDTH, HEIGHT = s_info.current_w, s_info.current_h
    except pygame.error:
        WIDTH, HEIGHT = 1280, 720
    run_blind_search()
    pygame.quit(); sys.exit()