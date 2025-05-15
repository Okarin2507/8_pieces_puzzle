import pygame
import sys
import threading
import time
import math
import random
from collections import deque

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
    5:(171,71,188), 6:(255,112,67), 7:(0,172,193), 8:(255,160,0), 9:(108,52,131)
}
TILE_BG_DEFAULT = (70,80,120)

WIDTH, HEIGHT = 0,0; screen_surf_global = None; clock_global = None
font_ui, title_f_global, puzzle_f_global, button_f_global, info_f_global = [None]*5
EMPTY_SLOT = 0

# --- Gradient Background ---
def draw_gradient_background(surface, top_color, bottom_color):
    h, w = surface.get_height(), surface.get_width(); rect_s = pygame.Rect(0,0,w,1)
    for y_val in range(h):
        r,g,b = [top_color[i]+(bottom_color[i]-top_color[i])*y_val/h for i in range(3)]
        rect_s.top=y_val; pygame.draw.rect(surface,(int(r),int(g),int(b)),rect_s)

# --- Text Helpers ---
def truncate_text(txt, fnt, max_w, ellps="..."):
    if not txt or fnt.size(txt)[0] <= max_w: return txt
    trunc_txt = ""; sz_a = fnt.size("a")[0] if fnt.size("a")[0]>0 else 10
    for char_idx, char_val in enumerate(txt):
        if fnt.size(trunc_txt+char_val+ellps)[0] > max_w:
            if char_idx==0: return txt[:max(0,max_w//sz_a-len(ellps))] + ellps if sz_a > 0 else ellps
            break
        trunc_txt += char_val
    return trunc_txt + ellps

def render_text_wrapped(txt, fnt, col, max_w, surf, sx, sy, line_spacing=5, cx=False, r_center_in=None):
    words=txt.split(' '); lines=[]; curr_ln_txt=""
    for wd in words:
        test_ln=curr_ln_txt+wd+" "
        if fnt.size(test_ln)[0]<=max_w: curr_ln_txt=test_ln
        else:
            if curr_ln_txt: lines.append(curr_ln_txt.strip())
            curr_ln_txt=wd+" "
            if fnt.size(curr_ln_txt)[0]>max_w: lines.append(truncate_text(wd,fnt,max_w)); curr_ln_txt=""
    if curr_ln_txt: lines.append(curr_ln_txt.strip())
    y_off=0
    total_h = 0
    for i, ln_t_val in enumerate(lines):
        if not ln_t_val: continue
        ln_s=fnt.render(ln_t_val,True,col)
        ln_r=ln_s.get_rect(centerx=r_center_in.centerx,top=sy+y_off) if cx and r_center_in else ln_s.get_rect(left=sx,top=sy+y_off)
        surf.blit(ln_s,ln_r)
        line_h = fnt.get_height()
        y_off+=line_h
        total_h += line_h
        if i < len(lines) -1:
            y_off += line_spacing
            total_h += line_spacing
    return total_h

def is_valid_puzzle_state(st_val): return isinstance(st_val,(list,tuple)) and len(st_val)==9 and sorted(st_val)==list(range(1,10))

class Button:
     def __init__(self,x,y,w,h,txt,col=PRIMARY,hcol=PRIMARY_DARK,shcol=BUTTON_SHADOW_COLOR):
         self.rect=pygame.Rect(x,y,w,h);self.text=txt;self.base_color=col;self.hover_color=hcol;self.shadow_color=shcol
         self.is_hovered=False;self.radius=12;self.sh_offset=4;self.y_off=0
     def draw(self,surf,fnt_s):
         curr_c=self.hover_color if self.is_hovered else self.base_color; sh_r=self.rect.move(self.sh_offset,self.sh_offset+self.y_off)
         pygame.draw.rect(surf,self.shadow_color,sh_r,border_radius=self.radius); btn_r=self.rect.move(0,self.y_off)
         pygame.draw.rect(surf,curr_c,btn_r,border_radius=self.radius); txt_s=fnt_s.render(self.text,True,TEXT_PRIMARY)
         surf.blit(txt_s,txt_s.get_rect(center=btn_r.center))
     def check_hover(self,mpos): self.is_hovered=self.rect.collidepoint(mpos); return self.is_hovered
     def is_clicked(self,mpos,mclick):
        cl=self.is_hovered and mclick
        if cl: self.y_off = self.sh_offset
        return cl

class MessageBox:
    def __init__(self,w_val,h_val,title_txt,msg_txt,btn_disp_txt="OK"):
        self.rect=pygame.Rect((WIDTH-w_val)//2,(HEIGHT-h_val)//2,w_val,h_val); self.title=title_txt; self.message=msg_txt
        self.radius=14; self.active=False; btn_w,btn_h=130,48
        self.ok_button=Button(self.rect.x+(self.rect.width-btn_w)//2,self.rect.bottom-btn_h-30,btn_w,btn_h,btn_disp_txt,col=PRIMARY,hcol=PRIMARY_DARK)
    def draw(self,surf,title_f_s,font_s,btn_f_s):
        if not self.active: return
        overlay=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA); overlay.fill((0,0,0,180)); surf.blit(overlay,(0,0))
        pygame.draw.rect(surf,SIDEBAR_BG,self.rect,border_radius=self.radius)
        inner_bg_c=(SIDEBAR_BG[0]-10,SIDEBAR_BG[1]-10,SIDEBAR_BG[2]-10)
        pygame.draw.rect(surf,tuple(max(0,c) for c in inner_bg_c),self.rect.inflate(-8,-8),border_radius=self.radius-3)
        title_s=title_f_s.render(self.title,True,ACCENT_COLOR if ACCENT_COLOR else PRIMARY); title_r_val=title_s.get_rect(centerx=self.rect.centerx,y=self.rect.y+30); surf.blit(title_s,title_r_val)
        msg_sy=self.rect.y+title_r_val.height+55; msg_max_w_val=self.rect.width-70
        render_text_wrapped(self.message,font_s,TEXT_PRIMARY,msg_max_w_val,surf,self.rect.x+35,msg_sy,line_spacing=7,cx=True,r_center_in=self.rect)
        self.ok_button.draw(surf,btn_f_s)
    def check_hover(self,mpos): return self.ok_button.check_hover(mpos) if self.active else False
    def handle_event(self,evt):
        if not self.active: return False
        if evt.type==pygame.MOUSEBUTTONDOWN and evt.button==1 and self.ok_button.is_clicked(evt.pos,True): self.active=False; return True
        return False

class AnimatedNumberTile:
    def __init__(self,val,x,y,s):
        self.value=val;self.target_value=val;self.size=s;self.inner_size=int(s*0.90)
        self.rect=pygame.Rect(x,y,s,s);self.inner_rect=pygame.Rect(0,0,self.inner_size,self.inner_size);self.inner_rect.center=self.rect.center
        self.radius=max(7,int(self.inner_size*0.13));self.is_appearing=False;self.appear_start=0;self.appear_dur=0.40
        self.curr_scale=1.0;self.curr_y_off=0;self.highlight_c=None

    def set_value(self, new_value, trigger_animation=False):
        if new_value != self.value:
            self.target_value = new_value
            if trigger_animation and new_value != EMPTY_SLOT:
                self.is_appearing = True
                self.appear_start = time.time()
                self.curr_scale = 1.7
                self.curr_y_off = -self.size * 0.3
                self.highlight_c = WARNING_COLOR
            else:
                self.value = new_value
                self.is_appearing = False
                self.highlight_c = WARNING_COLOR if new_value != EMPTY_SLOT else None

    def update(self):
        if self.is_appearing:
            el=time.time()-self.appear_start
            if el>=self.appear_dur:
                self.is_appearing=False
                self.value=self.target_value
                self.curr_scale=1.0
                self.curr_y_off=0
            else:
                prog=el/self.appear_dur
                ease_out=(1.0-(1.0-prog)**4)
                self.curr_scale=1.0+0.7*(1.0-ease_out)
                self.curr_y_off=-self.size*0.3*(1.0-ease_out)
                self.value=self.target_value

    def draw(self,surf,fnt_s):
        if self.value==EMPTY_SLOT and not self.highlight_c: return

        draw_r_base=self.inner_rect.copy();scaled_s_val=int(self.inner_size*self.curr_scale)
        draw_r_base.width=scaled_s_val;draw_r_base.height=scaled_s_val
        draw_r_base.centerx=self.inner_rect.centerx
        draw_r_base.centery=self.inner_rect.centery+int(self.curr_y_off)

        bg_c_val=NUMBER_TILE_COLORS.get(self.value,TILE_BG_DEFAULT) if self.value!=EMPTY_SLOT else tuple(max(0,c-20) for c in GRADIENT_BOTTOM_COLOR)

        final_bg_c_val = bg_c_val
        if self.highlight_c:
            if self.is_appearing:
                final_bg_c_val = self.highlight_c
            else:
                try:
                    final_bg_c_val = pygame.Color(bg_c_val).lerp(pygame.Color(self.highlight_c), 0.7)
                except (ValueError, TypeError):
                    final_bg_c_val = self.highlight_c

        pygame.draw.rect(surf,final_bg_c_val,draw_r_base,border_radius=int(self.radius*self.curr_scale))

        if self.value!=EMPTY_SLOT:
            try:
                scaled_f_s_val = int(fnt_s.get_height()*self.curr_scale)
                if scaled_f_s_val <=0: scaled_f_s_val = 1
                font_name_attempt = fnt_s.get_name() if hasattr(fnt_s, 'get_name') else None
                scaled_f = pygame.font.SysFont(font_name_attempt, scaled_f_s_val, bold=True) if font_name_attempt else pygame.font.Font(None, scaled_f_s_val)
            except:
                scaled_f_s_val = int(pygame.font.Font(None, 30).get_height() * self.curr_scale)
                if scaled_f_s_val <=0: scaled_f_s_val = 1
                scaled_f = pygame.font.Font(None, scaled_f_s_val)


            txt_s=scaled_f.render(str(self.value),True,TEXT_PRIMARY)
            surf.blit(txt_s,txt_s.get_rect(center=draw_r_base.center))

def backtrack_fill_recursive(idx,curr_grid_st,used_nums):
    global animation_path_list,backtrack_target_st,backtrack_is_running
    if not backtrack_is_running: return False
    if idx==9: return list(curr_grid_st)==list(backtrack_target_st)
    corr_num=backtrack_target_st[idx]
    if corr_num in used_nums: return False
    curr_grid_st[idx]=corr_num;used_nums.add(corr_num);animation_path_list.append(list(curr_grid_st))
    if backtrack_fill_recursive(idx+1,curr_grid_st,used_nums): return True
    if backtrack_is_running:
        used_nums.remove(corr_num);curr_grid_st[idx]=EMPTY_SLOT;animation_path_list.append(list(curr_grid_st))
    return False

def run_backtracking_thread(target_st_param):
    global animation_path_list,backtrack_target_st,backtrack_is_running,backtrack_is_finished,backtrack_was_success
    backtrack_target_st=target_st_param;backtrack_is_running=True;backtrack_is_finished=False;backtrack_was_success=False;animation_path_list.clear()
    init_grid=[EMPTY_SLOT]*9;used=set();animation_path_list.append(list(init_grid))
    try: backtrack_was_success=backtrack_fill_recursive(0,init_grid,used)
    except Exception as e: print(f"Lỗi thread (fill): {e}");backtrack_was_success=False
    finally:
        backtrack_is_running=False;backtrack_is_finished=True;print(f"Backtracking (fill) xong. Thành công: {backtrack_was_success}");
        if not backtrack_was_success and (not animation_path_list or animation_path_list[-1] != [EMPTY_SLOT]*9):
             animation_path_list.append([EMPTY_SLOT]*9)

def draw_grid_anim(surf,tiles_list_obj,fnt_s_obj):
    for tile_o in tiles_list_obj: tile_o.draw(surf,fnt_s_obj)

def draw_target_editor(surf,editor_ts_list,editor_st_list,sel_idx,title_f_s,gen_f_s,info_f_s,puz_f_s,btn_f_s,start_btn_o,back_btn_o):
    title_s_obj=title_f_s.render("Chọn Trạng Thái Đích",True,ACCENT_COLOR if ACCENT_COLOR else PRIMARY)
    title_r_o=title_s_obj.get_rect(centerx=WIDTH//2,y=75); surf.blit(title_s_obj,title_r_o)
    instr_l=["Click ô, nhập số (1-9).","Số nhập sẽ đổi chỗ.","Phải là hoán vị 1-9.","Nhấn 'Bắt đầu' để xem."]
    instr_y_val=title_r_o.bottom+50; instr_max_w_val=WIDTH*0.8; curr_instr_y_val=instr_y_val
    for txt_i in instr_l: curr_instr_y_val+=render_text_wrapped(txt_i,info_f_s,TEXT_SECONDARY,instr_max_w_val,surf,0,curr_instr_y_val,line_spacing=8,cx=True,r_center_in=surf.get_rect())+8

    if not editor_ts_list: return
    tile_s_o=editor_ts_list[0].size; puz_w_o=tile_s_o*3; puz_h_o=tile_s_o*3
    grid_x_o=(WIDTH-puz_w_o)//2; grid_y_o=curr_instr_y_val+40
    for i,tile_o_val in enumerate(editor_ts_list):
        r,c=divmod(i,3);tile_o_val.rect.topleft=(grid_x_o+c*tile_s_o,grid_y_o+r*tile_s_o);tile_o_val.inner_rect.center=tile_o_val.rect.center
        tile_o_val.draw(surf,puz_f_s)
        if i==sel_idx: pygame.draw.rect(surf,PRIMARY,tile_o_val.inner_rect.inflate(10,10),border_radius=tile_o_val.radius+3,width=5)

    is_v=is_valid_puzzle_state(editor_st_list);status_txt_val="Hợp lệ (1-9)" if is_v else "Không hợp lệ (thiếu/trùng)"
    status_c_val=PRIMARY if is_v else ERROR_COLOR
    status_s_obj=gen_f_s.render(status_txt_val,True,status_c_val);status_r_o=status_s_obj.get_rect(center=(WIDTH//2,grid_y_o+puz_h_o+60));surf.blit(status_s_obj,status_r_o)

    btn_y_val = status_r_o.bottom+45
    min_btn_y = HEIGHT - start_btn_o.rect.height - 30
    btn_y_val = min(btn_y_val, min_btn_y)

    btn_total_w_val=start_btn_o.rect.width+back_btn_o.rect.width+35
    start_btn_o.rect.topleft=((WIDTH-btn_total_w_val)//2,btn_y_val);back_btn_o.rect.topleft=(start_btn_o.rect.right+35,btn_y_val)
    start_btn_o.check_hover(pygame.mouse.get_pos());back_btn_o.check_hover(pygame.mouse.get_pos());start_btn_o.draw(surf,btn_f_s);back_btn_o.draw(surf,btn_f_s)

def draw_filling_animation(surf,anim_ts_list,curr_step,total_steps,target_st_val,auto_mode_flag,puz_f_s,gen_f_s,info_f_s,btn_f_s,auto_b,next_b,reset_b,back_b):
    title_s_obj=title_f_global.render("Hoạt ảnh điền số",True,ACCENT_COLOR if ACCENT_COLOR else PRIMARY)
    surf.blit(title_s_obj,title_s_obj.get_rect(centerx=WIDTH//2,y=65))

    grid_y_pos_val=170
    grid_bottom_y = grid_y_pos_val
    if anim_ts_list:
        tile_s_o=anim_ts_list[0].size;puz_w_o=tile_s_o*3; grid_x_o=(WIDTH-puz_w_o)//2
        grid_bottom_y = grid_y_pos_val + tile_s_o*3
        for i,tile_o_val in enumerate(anim_ts_list):
            r,c=divmod(i,3);tile_o_val.rect.topleft=(grid_x_o+c*tile_s_o,grid_y_pos_val+r*tile_s_o);tile_o_val.inner_rect.center=tile_o_val.rect.center
        draw_grid_anim(surf,anim_ts_list,puz_f_s)

    info_y_pos_val=grid_bottom_y+55
    target_str_disp_val=truncate_text(f"({', '.join(map(str,target_st_val))})",info_f_s,WIDTH*0.7)
    
    thread_alive = backtrack_thread_obj and backtrack_thread_obj.is_alive()
    status_msg_disp_val = "Đang tạo..." if thread_alive and not backtrack_is_finished else ('Hoàn thành!' if backtrack_was_success else 'Lỗi/Không thành công')

    info_txt_list=[f"Đích: {target_str_disp_val}",f"Bước: {curr_step}/{total_steps}",f"Tình trạng: {status_msg_disp_val}"]

    current_info_text_y = info_y_pos_val
    for i,txt_val in enumerate(info_txt_list):
        line_s_obj=info_f_s.render(txt_val,True,TEXT_SECONDARY)
        surf.blit(line_s_obj,line_s_obj.get_rect(centerx=WIDTH//2,y=current_info_text_y)); current_info_text_y+=info_f_s.get_height()+8

    btn_y_pos_val = current_info_text_y + 30
    min_btn_y_val = HEIGHT - auto_b.rect.height - 30
    btn_y_pos_val = min(btn_y_pos_val, min_btn_y_val)

    btn_space_val=30; btn_tot_w_val=auto_b.rect.width+next_b.rect.width+reset_b.rect.width+back_b.rect.width+3*btn_space_val
    btns_start_x_val=(WIDTH-btn_tot_w_val)//2
    auto_b.rect.topleft=(btns_start_x_val,btn_y_pos_val);next_b.rect.topleft=(auto_b.rect.right+btn_space_val,btn_y_pos_val)
    reset_b.rect.topleft=(next_b.rect.right+btn_space_val,btn_y_pos_val);back_b.rect.topleft=(reset_b.rect.right+btn_space_val,btn_y_pos_val)
    auto_b.text="Tự động: Bật" if auto_mode_flag else "Tự động: Tắt"
    for btn_o in [auto_b,next_b,reset_b,back_b]: btn_o.check_hover(pygame.mouse.get_pos()); btn_o.draw(surf,btn_f_s)

def init_number_tiles(st_list,off_x,off_y,tile_s_o):
    return [AnimatedNumberTile(val,off_x+c*tile_s_o,off_y+r*tile_s_o,tile_s_o) for i,val in enumerate(st_list) for r,c in [divmod(i,3)]]

def update_animation_tiles(anim_ts_list,prev_st,curr_st):
    global highlight_end_time
    if not anim_ts_list or len(prev_st)!=9 or len(curr_st)!=9: return
    changed_anim_flag=False
    for i in range(9):
        if prev_st[i]!=curr_st[i]:
            is_fill_action=(prev_st[i]==EMPTY_SLOT and curr_st[i]!=EMPTY_SLOT)
            anim_ts_list[i].set_value(curr_st[i],trigger_animation=is_fill_action)
            if is_fill_action: changed_anim_flag=True
            else: anim_ts_list[i].highlight_c=WARNING_COLOR
        elif not anim_ts_list[i].is_appearing :
            anim_ts_list[i].highlight_c=None
    highlight_end_time=time.time()+(0.50 if changed_anim_flag else 0.30)

def fill_main():
    global screen_surf_global, clock_global, font_ui, title_f_global, puzzle_f_global, button_f_global, info_f_global
    global backtrack_thread_obj, backtrack_is_running, backtrack_is_finished, backtrack_was_success
    global animation_path_list, highlight_end_time

    backtrack_thread_obj = None

    curr_view="target_editor";target_st_tup=tuple(range(1,10));edit_target_st_list=list(target_st_tup);editor_sel_idx_val=-1
    editor_t_s=min(WIDTH*0.50,HEIGHT*0.50)/3*0.9; editor_t_s=int(editor_t_s)
    editor_p_w=editor_t_s*3
    editor_x_val=(WIDTH-editor_p_w)//2; editor_y_val=300
    editor_ts_list_obj=init_number_tiles(edit_target_st_list,editor_x_val,editor_y_val,editor_t_s)

    anim_ts_list_obj=[]; anim_t_s_val=min(WIDTH*0.62,HEIGHT*0.62)/3*0.9; anim_t_s_val = int(anim_t_s_val)
    anim_p_w_val=anim_t_s_val*3
    anim_x_val=(WIDTH-anim_p_w_val)//2; anim_y_val=170
    curr_anim_step_val=0; auto_mode_f=True; last_sw_t_ms=0; sw_interval_ms_val=600

    edit_btn_w,edit_btn_h=240,58; start_anim_b=Button(0,0,edit_btn_w,edit_btn_h,"Bắt đầu"); back_main_b_edit=Button(0,0,220,edit_btn_h,"Về Menu Chính")
    anim_btn_w,anim_btn_h=145,50; auto_b_obj=Button(0,0,anim_btn_w,anim_btn_h,"Tự động: Bật"); next_b_obj=Button(0,0,anim_btn_w,anim_btn_h,"Tiếp theo")
    reset_b_obj=Button(0,0,anim_btn_w,anim_btn_h,"Reset"); back_edit_b_obj=Button(0,0,180,anim_btn_h,"Chọn Lại Đích")
    msg_box_obj=MessageBox(520,300,"Thông báo","")
    mouse_was_down_f=False

    running_f=True
    while running_f:
        mpos_val=pygame.mouse.get_pos();curr_mdown_f=pygame.mouse.get_pressed()[0];mclick_f_frame=False
        for evt_item in pygame.event.get():
            if evt_item.type==pygame.QUIT:
                running_f=False
                backtrack_is_running=False
                if backtrack_thread_obj and backtrack_thread_obj.is_alive():
                    backtrack_thread_obj.join(timeout=0.5)
            if evt_item.type==pygame.MOUSEBUTTONDOWN and evt_item.button==1: mclick_f_frame=True
            if msg_box_obj.active and msg_box_obj.handle_event(evt_item): continue

            if curr_view=="target_editor":
                if evt_item.type==pygame.KEYDOWN:
                    if evt_item.key==pygame.K_ESCAPE: running_f=False
                    elif editor_sel_idx_val!=-1 and pygame.K_1<=evt_item.key<=pygame.K_9:
                        new_n_val=evt_item.key-pygame.K_0;curr_n_val=edit_target_st_list[editor_sel_idx_val]
                        if new_n_val!=curr_n_val:
                            try:
                                sw_idx=edit_target_st_list.index(new_n_val);edit_target_st_list[editor_sel_idx_val]=new_n_val;edit_target_st_list[sw_idx]=curr_n_val
                                editor_ts_list_obj[editor_sel_idx_val].set_value(new_n_val, trigger_animation=True); editor_ts_list_obj[sw_idx].set_value(curr_n_val, trigger_animation=True)
                            except ValueError: msg_box_obj.message=f"Số {new_n_val} không có trong lưới.";msg_box_obj.active=True
                        editor_sel_idx_val=-1
                if mclick_f_frame:
                    if start_anim_b.is_clicked(mpos_val,True):
                        if is_valid_puzzle_state(edit_target_st_list):
                            target_st_tup=tuple(edit_target_st_list)
                            if not (backtrack_thread_obj and backtrack_thread_obj.is_alive()):
                                animation_path_list.clear();curr_anim_step_val=0;backtrack_is_finished=False;highlight_end_time=0
                                backtrack_thread_obj=threading.Thread(target=run_backtracking_thread,args=(target_st_tup,),daemon=True);backtrack_thread_obj.start()
                                curr_view="filling_animation";anim_ts_list_obj=init_number_tiles([EMPTY_SLOT]*9,anim_x_val,anim_y_val,anim_t_s_val)
                                for tile_obj in anim_ts_list_obj: tile_obj.highlight_c = None
                                if animation_path_list:
                                     update_animation_tiles(anim_ts_list_obj, [EMPTY_SLOT]*9, animation_path_list[0])

                        else: msg_box_obj.message="Trạng thái đích không hợp lệ (phải là hoán vị của 1-9).";msg_box_obj.active=True
                    elif back_main_b_edit.is_clicked(mpos_val,True): running_f=False
                    else:
                        new_sel_idx = -1
                        for i,t in enumerate(editor_ts_list_obj):
                            if t.rect.collidepoint(mpos_val):
                                new_sel_idx = i
                                break
                        editor_sel_idx_val = new_sel_idx


            elif curr_view=="filling_animation":
                if evt_item.type==pygame.KEYDOWN and evt_item.key==pygame.K_ESCAPE:
                    curr_view="target_editor"
                    backtrack_is_running=False
                    if backtrack_thread_obj and backtrack_thread_obj.is_alive():
                        backtrack_thread_obj.join(0.5)
                    backtrack_thread_obj=None
                    backtrack_is_finished=True
                if mclick_f_frame:
                    if auto_b_obj.is_clicked(mpos_val,True): auto_mode_f=not auto_mode_f; last_sw_t_ms=time.time()*1000 if auto_mode_f else last_sw_t_ms
                    elif next_b_obj.is_clicked(mpos_val,True) and not auto_mode_f and backtrack_is_finished and animation_path_list and curr_anim_step_val<len(animation_path_list)-1:
                        curr_anim_step_val+=1;update_animation_tiles(anim_ts_list_obj,animation_path_list[curr_anim_step_val-1],animation_path_list[curr_anim_step_val])
                    elif reset_b_obj.is_clicked(mpos_val,True):
                        curr_anim_step_val=0;last_sw_t_ms=time.time()*1000;highlight_end_time=0
                        initial_display_state = animation_path_list[0] if animation_path_list else [EMPTY_SLOT]*9
                        anim_ts_list_obj=init_number_tiles(initial_display_state,anim_x_val,anim_y_val,anim_t_s_val)
                        for t_o in anim_ts_list_obj: t_o.highlight_c=None


                    elif back_edit_b_obj.is_clicked(mpos_val,True):
                        curr_view="target_editor"
                        backtrack_is_running=False
                        if backtrack_thread_obj and backtrack_thread_obj.is_alive():
                            backtrack_thread_obj.join(0.5)
                        backtrack_thread_obj=None
                        backtrack_is_finished=True

        if not curr_mdown_f and mouse_was_down_f:
            all_btns=[start_anim_b,back_main_b_edit,auto_b_obj,next_b_obj,reset_b_obj,back_edit_b_obj]
            if msg_box_obj.active: all_btns.append(msg_box_obj.ok_button)
            for btn_o_val in all_btns: btn_o_val.y_off=0
        mouse_was_down_f=curr_mdown_f

        for tile_obj in editor_ts_list_obj: tile_obj.update()

        if curr_view=="filling_animation":
            for tile_o_obj in anim_ts_list_obj: tile_o_obj.update()
            if time.time()>highlight_end_time:
                 for tile_o_obj in anim_ts_list_obj:
                     if not tile_o_obj.is_appearing: tile_o_obj.highlight_c=None
            now_ms_f_val=time.time()*1000
            if auto_mode_f and backtrack_is_finished and animation_path_list and curr_anim_step_val<len(animation_path_list)-1 and now_ms_f_val-last_sw_t_ms>=sw_interval_ms_val:
                curr_anim_step_val+=1;update_animation_tiles(anim_ts_list_obj,animation_path_list[curr_anim_step_val-1],animation_path_list[curr_anim_step_val]);last_sw_t_ms=now_ms_f_val

        draw_gradient_background(screen_surf_global, GRADIENT_TOP_COLOR, GRADIENT_BOTTOM_COLOR)
        if curr_view=="target_editor": draw_target_editor(screen_surf_global,editor_ts_list_obj,edit_target_st_list,editor_sel_idx_val,title_f_global,font_ui,info_f_global,puzzle_f_global,button_f_global,start_anim_b,back_main_b_edit)
        elif curr_view=="filling_animation":
            thread_alive = backtrack_thread_obj and backtrack_thread_obj.is_alive()
            if thread_alive and not animation_path_list and not backtrack_is_finished:
                 load_s=title_f_global.render("Đang tạo hoạt ảnh...",True,WARNING_COLOR);screen_surf_global.blit(load_s,load_s.get_rect(center=(WIDTH//2,HEIGHT//2)))
            else:
                total_s_o=max(0,len(animation_path_list)-1) if animation_path_list else 0
                draw_filling_animation(screen_surf_global,anim_ts_list_obj,curr_anim_step_val,total_s_o,target_st_tup,auto_mode_f,puzzle_f_global,font_ui,info_f_global,button_f_global,auto_b_obj,next_b_obj,reset_b_obj,back_edit_b_obj)
        if msg_box_obj.active: msg_box_obj.draw(screen_surf_global,title_f_global,font_ui,button_f_global)
        pygame.display.flip();clock_global.tick(60)

    backtrack_is_running=False
    if backtrack_thread_obj and backtrack_thread_obj.is_alive():
        backtrack_thread_obj.join(timeout=0.5)

animation_path_list=[]
backtrack_target_st=[]
backtrack_thread_obj=None
backtrack_is_running=False
backtrack_is_finished=False
backtrack_was_success=False
highlight_end_time=0

if __name__=="__main__":
    pygame.init();pygame.font.init()
    try: scr_inf=pygame.display.Info();WIDTH,HEIGHT=scr_inf.current_w,scr_inf.current_h;screen_surf_global=pygame.display.set_mode((WIDTH,HEIGHT),pygame.FULLSCREEN|pygame.SRCALPHA)
    except pygame.error: WIDTH,HEIGHT=1280,720;screen_surf_global=pygame.display.set_mode((WIDTH,HEIGHT))
    pygame.display.set_caption("Fill Animation Visualizer");clock_global=pygame.time.Clock()

    vn_f_list=["Tahoma","Arial","Segoe UI","Calibri","Times New Roman","Verdana","Roboto"]
    f_name_s=pygame.font.get_default_font();sys_f_l=pygame.font.get_fonts()
    for f_n_val in vn_f_list:
        if f_n_val.lower().replace(" ","") in [s_val.lower().replace(" ","") for s_val in sys_f_l]: f_name_s=f_n_val;break
    print(f"Fill.py sử dụng font: {f_name_s}")
    try:
        font_ui=pygame.font.SysFont(f_name_s,25, bold=True)
        title_f_global=pygame.font.SysFont(f_name_s,50,bold=True)
        puzzle_f_global=pygame.font.SysFont(f_name_s,66,bold=True)
        button_f_global=pygame.font.SysFont(f_name_s,23,bold=True)
        info_f_global=pygame.font.SysFont(f_name_s,23)
    except Exception as e_f: print(f"Lỗi font (fill.py): {e_f}.");font_ui=pygame.font.Font(None,27);title_f_global=pygame.font.Font(None,50);puzzle_f_global=pygame.font.Font(None,66);button_f_global=pygame.font.Font(None,23);info_f_global=pygame.font.Font(None,25)
    fill_main()
    pygame.quit(); sys.exit()