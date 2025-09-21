import pygame
import sys
import os
import sqlite3
import textwrap
import random
import math

pygame.init()

SCREEN_WIDTH = 440
SCREEN_HEIGHT = 782
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("MindGarden")

GREEN = (162, 217, 140)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BEIGE = (245, 236, 210)
RED = (200, 50, 50)

# 3 levels for flowers
HOME_SCREEN_Y_POSITIONS = [450, 325, 200]

# Screens
screens = ["home", "note"]
current_screen_index = 0

# Database
DB_FILE = "notes.db"
conn = sqlite3.connect(DB_FILE)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, title TEXT, body TEXT)")
conn.commit()

# Base path for assets
BASE_DIR = os.path.dirname(__file__)

def load_image(filename):
    return pygame.image.load(os.path.join(BASE_DIR, "assets", filename)).convert_alpha()

# Load images
prev_button_img = load_image("previousbutton.png")
next_button_img = load_image("nextbutton.png")
newnote_button_img = load_image("newnote.png")
hamburger_img = load_image("menu.png")
searchbar_img = load_image("searchbar.png")
searchbar_blank_img = load_image("searchbar_blank.png")
text_box_img = load_image("text.png")
bg_img = load_image("bg.png")
title_textbox_img = load_image("title.png")
desc_textbox_img = load_image("desc.png")
edit_button_img = load_image("edit.png")
delete_button_img = load_image("delete.png")
home_background_img = load_image("background.png")
home_background_img = pygame.transform.scale(home_background_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
close_img = load_image("closebg.png")
close_img = pygame.transform.scale(close_img, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Button sizes
prev_next_w = (103 / 220) * SCREEN_WIDTH
prev_next_h = prev_next_w * (22 / 103)
searchbar_w = (185 / 220) * SCREEN_WIDTH
searchbar_h = searchbar_w * (22 / 185)
hamburger_w = (20 / 220) * SCREEN_WIDTH
hamburger_h = hamburger_w * (22 / 20)
newnote_w = (210 / 220) * SCREEN_WIDTH
newnote_h = newnote_w * (39 / 210)

text_box_w = (210 / 220) * SCREEN_WIDTH
text_box_h = text_box_w * (123 / 210)

# Custom textbox for note editor
title_textbox_w = (210 / 220) * SCREEN_WIDTH
title_textbox_h = title_textbox_w * (27 / 210)
desc_textbox_w = (210 / 220) * SCREEN_WIDTH
desc_textbox_h = desc_textbox_w * (251 / 210)

edit_button_w = (11 / 220) * SCREEN_WIDTH
edit_button_h = edit_button_w * (11 / 11)

delete_button_w = (9 / 220) * SCREEN_WIDTH
delete_button_h = delete_button_w * (11 / 9)

bg_w = (210 / 220) * SCREEN_WIDTH
bg_h = bg_w * (281 / 210)

prev_button_img = pygame.transform.scale(prev_button_img, (prev_next_w, prev_next_h))
next_button_img = pygame.transform.scale(next_button_img, (prev_next_w, prev_next_h))
newnote_button_img = pygame.transform.scale(newnote_button_img, (newnote_w, newnote_h))
hamburger_img = pygame.transform.scale(hamburger_img, (hamburger_w, hamburger_h))
searchbar_img = pygame.transform.scale(searchbar_img, (searchbar_w, searchbar_h))
searchbar_blank_img = pygame.transform.scale(searchbar_blank_img, (searchbar_w, searchbar_h))
text_box_img = pygame.transform.scale(text_box_img, (int(text_box_w), int(text_box_h)))
bg_img = pygame.transform.scale(bg_img, (int(bg_w), int(bg_h)))
title_textbox_img = pygame.transform.scale(title_textbox_img, (int(title_textbox_w), int(title_textbox_h)))
desc_textbox_img = pygame.transform.scale(desc_textbox_img, (int(desc_textbox_w), int(desc_textbox_h)))
edit_button_img = pygame.transform.scale(edit_button_img, (int(edit_button_w), int(edit_button_h)))
delete_button_img = pygame.transform.scale(delete_button_img, (int(delete_button_w), int(delete_button_h)))

margin = 11
# shift buttons up
button_lift = 17

newnote_button_rect = newnote_button_img.get_rect(
    midbottom=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - margin - button_lift)
)

button_spacing = 5
prev_button_rect = prev_button_img.get_rect(
    midbottom=(margin + prev_next_w // 2, newnote_button_rect.top - button_spacing)
)
next_button_rect = next_button_img.get_rect(
    midbottom=(SCREEN_WIDTH - margin - prev_next_w // 2, newnote_button_rect.top - button_spacing)
)

hamburger_rect = hamburger_img.get_rect(topleft=(margin, margin))
searchbar_rect = searchbar_img.get_rect(
    midleft=(hamburger_rect.right + (margin - 2), hamburger_rect.centery)
)

# note view
text_box_rect = text_box_img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))

# note editor
title_textbox_rect = title_textbox_img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 304))
desc_textbox_rect = desc_textbox_img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 19))

# notes list
bg_rect = bg_img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))

# fonts
FONT_PATH = os.path.join(BASE_DIR, "assets", "pixelfont.ttf")
title_font = pygame.font.Font(FONT_PATH, 28)
body_font = pygame.font.Font(FONT_PATH, 18)

# notes screen states
notes_state = "list"  # "list", "editor", "view"
active_note = None
note_title = ""
note_body = ""
note_focus = "title"

# searchbar state
search_active = False
search_text = ""

# text scrolling state
scroll_offset = 0
max_lines_visible = 6

# notes list scrolling state
notes_list_scroll = 0

# delete button for note view
delete_button_rect = None
edit_button_rect = None

# dictionary to hold plant objects, keyes note_id
plant_objects = {}
# dictionary to store clickable rects for plants on home screen
home_plant_rects = {}

growth_animation_active = False
plant_to_grow = None
growth_stages_remaining = 0
last_growth_time = 0

def trigger_growth_animation(plant, stages):
    global growth_animation_active, plant_to_grow, growth_stages_remaining, last_growth_time
    plant_to_grow = plant
    growth_stages_remaining = stages
    last_growth_time = pygame.time.get_ticks()
    growth_animation_active = True

def wrap_text(text, font, max_width):
    if not text:
        return [""]
    
    lines = []
    paragraphs = text.split('\n')
    
    for paragraph in paragraphs:
        if not paragraph.strip():
            lines.append("")
            continue
            
        words = paragraph.split(' ')
        current_line = ""
        
        for word in words:
            if not word:
                continue
                
            test_line = current_line + (" " if current_line else "") + word
            test_width = font.size(test_line)[0]
            
            if test_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
        
                if font.size(word)[0] > max_width:
                    while word:
                        test_word = ""
                        for i, char in enumerate(word):
                            test_char = test_word + char
                            if font.size(test_char)[0] <= max_width:
                                test_word = test_char
                            else:
                                break
    
                        if test_word:
                            lines.append(test_word)
                            word = word[len(test_word):]
                        else:
                            lines.append(word[0])
                            word = word[1:]
   
                        current_line = ""
                else:
                    current_line = word
        
        if current_line:
            lines.append(current_line)
    
    return lines if lines else [""]

def fetch_notes(query=""):
    if query:
        c.execute("SELECT id, title FROM notes WHERE title LIKE ?", ('%' + query + '%',))
    else:
        c.execute("SELECT id, title FROM notes")
    return c.fetchall()

def delete_note(note_id):
    c.execute("DELETE FROM notes WHERE id=?", (note_id,))
    conn.commit()
    if note_id in plant_objects:
        del plant_objects[note_id]

# back button
def handle_prev_button():
    global current_screen_index, notes_state, active_note, scroll_offset, notes_list_scroll
    
    if screens[current_screen_index] == "note" and notes_state == "view":
        notes_state = "list"
        active_note = None
        scroll_offset = 0
        notes_list_scroll = 0
    elif screens[current_screen_index] == "note" and notes_state == "editor":
        notes_state = "list"
        notes_list_scroll = 0
    else:
        current_screen_index = (current_screen_index - 1) % len(screens)

# text box scroll
def handle_scroll(direction):
    global scroll_offset
    if direction == "up" and scroll_offset > 0:
        scroll_offset -= 1
    elif direction == "down":
        scroll_offset += 1

# list scroll
def handle_notes_list_scroll(direction):
    global notes_list_scroll
    if direction == "up" and notes_list_scroll > 0:
        notes_list_scroll -= 1
    elif direction == "down":
        notes_list_scroll += 1

def draw_screen():
    global delete_button_rect, edit_button_rect
    delete_button_rect = None
    edit_button_rect = None

    if screens[current_screen_index] == "home" and home_background_img:
        screen.blit(home_background_img, (0, 0))
    else:
        screen.blit(close_img, (0, 0))

    screen.blit(prev_button_img, prev_button_rect)
    screen.blit(next_button_img, next_button_rect)
    screen.blit(newnote_button_img, newnote_button_rect)
    screen.blit(hamburger_img, hamburger_rect)
    screen.blit(searchbar_blank_img, searchbar_rect)
    
    if search_text:
        search_surface = body_font.render(search_text, True, BLACK)
    else:
        search_surface = body_font.render("Search...", True, BLACK)
    
    search_rect_draw = search_surface.get_rect(midleft=(searchbar_rect.left + 40, searchbar_rect.centery - 2))
    screen.blit(search_surface, search_rect_draw)

    if screens[current_screen_index] == "home":
        home_plant_rects.clear()
        plant_ids = list(plant_objects.keys())
        
        for note_id in plant_ids:
            plant = plant_objects[note_id]
            
            plant.pos_x = plant.home_pos_x
            plant.pos_y = plant.home_pos_y

            plant.scale = 4.0
            
            blit_rect = plant.draw(screen)
            home_plant_rects[note_id] = pygame.Rect(plant.home_pos_x-50, plant.home_pos_y-50, 100, 100)


    elif screens[current_screen_index] == "note":
        if notes_state == "list":
            # background for notes list
            screen.blit(bg_img, bg_rect)
            
            notes_list_top = bg_rect.top + 30
            notes_list_bottom = bg_rect.top + 530
            notes_list_height = notes_list_bottom - notes_list_top
            notes_list_left = bg_rect.left + 20
            notes_list_width = bg_rect.width - 40
            
            clip_rect = pygame.Rect(notes_list_left, notes_list_top, notes_list_width, notes_list_height)
            screen.set_clip(clip_rect)
            
            notes = fetch_notes(search_text)
            note_height = 60
            note_spacing = 10
            
            start_y = notes_list_top - (notes_list_scroll * (note_height + note_spacing))
            
            for i, (note_id, title) in enumerate(notes):
                y_pos = start_y + i * (note_height + note_spacing)
                
                if y_pos + note_height >= notes_list_top - 50 and y_pos <= notes_list_bottom + 50:
                    note_rect = pygame.Rect(notes_list_left + 10, y_pos, notes_list_width - 20, note_height)
                    
                    pygame.draw.rect(screen, BLACK, note_rect, 2)
                    
                    max_title_width = note_rect.width - 30
                    title_surface = body_font.render(title, True, BLACK)
                    
                    if title_surface.get_width() > max_title_width:
                        truncated_title = title
                        while body_font.size(truncated_title + "...")[0] > max_title_width and len(truncated_title) > 0:
                            truncated_title = truncated_title[:-1]
                        title_surface = body_font.render(truncated_title + "...", True, BLACK)
                    
                    screen.blit(title_surface, (note_rect.x + 15, note_rect.y + 15))
            
            screen.set_clip(None)
            
            if notes_list_scroll > 0:
                up_indicator = body_font.render("↑", True, BLACK)
                screen.blit(up_indicator, (bg_rect.right - 25, notes_list_top + 5))
            
            if len(notes) > 0:
                total_content_height = len(notes) * (note_height + note_spacing)
                visible_content_height = notes_list_height
                max_scroll = max(0, (total_content_height - visible_content_height) // (note_height + note_spacing))
                
                if notes_list_scroll < max_scroll:
                    down_indicator = body_font.render("↓", True, BLACK)
                    screen.blit(down_indicator, (bg_rect.right - 25, notes_list_bottom - 25))

        elif notes_state == "editor":
            screen.blit(title_textbox_img, title_textbox_rect)
            screen.blit(desc_textbox_img, desc_textbox_rect)

            if note_title:
                title_surface = body_font.render(note_title, True, BLACK)
                screen.blit(title_surface, (title_textbox_rect.x + 10, title_textbox_rect.y + 5))
            else:
                title_surface = body_font.render("Title...", True, (128, 128, 128))
                screen.blit(title_surface, (title_textbox_rect.x + 10, title_textbox_rect.y + 5))

            if note_body:
                content_width = desc_textbox_rect.width - 20
                wrapped_lines = wrap_text(note_body, body_font, content_width)
                
                y_offset = desc_textbox_rect.y + 10
                line_height = 20
                max_lines = (desc_textbox_rect.height - 20) // line_height
                
                for i, line in enumerate(wrapped_lines[:max_lines]):
                    if y_offset + line_height > desc_textbox_rect.bottom - 10:
                        break
                    text_surface = body_font.render(line, True, BLACK)
                    screen.blit(text_surface, (desc_textbox_rect.left + 10, y_offset))
                    y_offset += line_height
            else:
                body_surface = body_font.render("Body...", True, (128, 128, 128))
                screen.blit(body_surface, (desc_textbox_rect.x + 10, desc_textbox_rect.y + 10))

        elif notes_state == "view" and active_note:
            note_id = active_note[0]
            if note_id in plant_objects:
                plant = plant_objects[note_id]
                plant.scale = 4
                plant.pos_x = SCREEN_WIDTH // 2
                plant.pos_y = text_box_rect.top - 55
                plant.draw(screen)

            title_surface = title_font.render(active_note[1], True, BLACK)
            title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, text_box_rect.top - 25))
            screen.blit(title_surface, title_rect)
            
            screen.blit(text_box_img, text_box_rect)
            
            if active_note[2]:
                content_width = text_box_rect.width - 40
                wrapped_lines = wrap_text(active_note[2], body_font, content_width)
                
                start_line = max(0, scroll_offset)
                end_line = min(len(wrapped_lines), start_line + max_lines_visible)
                visible_lines = wrapped_lines[start_line:end_line]
                
                y_offset = text_box_rect.top + 15
                line_height = 18
                
                for line in visible_lines:
                    if y_offset + line_height > text_box_rect.bottom - 15:
                        break
                    text_surface = body_font.render(line, True, BLACK)
                    screen.blit(text_surface, (text_box_rect.left + 15, y_offset))
                    y_offset += line_height
                
                if scroll_offset > 0:
                    up_indicator = body_font.render("↑", True, BLACK)
                    screen.blit(up_indicator, (text_box_rect.right - 25, text_box_rect.top + 5))
                
                if start_line + max_lines_visible < len(wrapped_lines):
                    down_indicator = body_font.render("↓", True, BLACK)
                    screen.blit(down_indicator, (text_box_rect.right - 25, text_box_rect.bottom - 25))
            
            edit_button_rect = pygame.Rect(text_box_rect.left + 5, text_box_rect.top - int(edit_button_h) - 10, int(edit_button_w), int(edit_button_h))
            screen.blit(edit_button_img, edit_button_rect)
        
            delete_button_rect = pygame.Rect(edit_button_rect.right + 5, text_box_rect.top - int(delete_button_h) - 10, int(delete_button_w), int(delete_button_h))
            screen.blit(delete_button_img, delete_button_rect)

class Plant:
    def __init__(self, x, y, scale=4.0):
        self.pos_x = x
        self.pos_y = y
        self.scale = scale

        x_padding = 12
        self.home_pos_x = random.randint(x_padding, SCREEN_WIDTH - x_padding)
        self.home_pos_y = random.choice(HOME_SCREEN_Y_POSITIONS)

        # growth stuff
        self.growth_cap = random.randint(7, 16)
        self.main_branch_len_min = random.uniform(1, 4)
        self.main_branch_len_max = random.uniform(1, 8)
        self.offshoot_len_min = random.uniform(4, 6)
        self.offshoot_len_max = random.uniform(4, 15)

        self.growth_stage = 0
        self.canvas_width, self.canvas_height = 100, 100
        self.thinness = 2
        self.canvas = pygame.Surface((self.canvas_width, self.canvas_height), pygame.SRCALPHA)

        init_pos = (self.canvas_width / 2, self.canvas_height)
        init_endpos = (self.canvas_width / 2, self.canvas_height - 4)
        self.branch_positions = [(init_pos, init_endpos)]
        self.branch_shoots_positions = []

        self.offshoot_pos_seed = [random.uniform(-3, 3) for _ in range(20)]
       
        base_flower_colors = [(255, 105, 180), (255, 69, 0), (138, 43, 226), (255, 215, 0)]
        self.base_flower_color = random.choice(base_flower_colors)
        FLOWER_CHANCE = 0.4

        self.leaf_angle_offsets = []
        self.leaf_extra_positions = []
        self.flower_data = []

        for _ in range(20):
            self.leaf_angle_offsets.append({
                'mid': random.uniform(-0.5, 0.5),
                'end': random.uniform(-0.5, 0.5),
                'extra': random.uniform(-1, 1)
            })
            self.leaf_extra_positions.append({
                'show': random.random() < 0.3,
                'position': 0.7
            })
            self.flower_data.append({
                'show_mid': random.random() < FLOWER_CHANCE,
                'color_mid': self._get_flower_color_shade(),
                'size_mid': random.uniform(2.0, 3.5),
                'show_end': random.random() < FLOWER_CHANCE,
                'color_end': self._get_flower_color_shade(),
                'size_end': random.uniform(2.0, 3.5)
            })
       
        self.grow()

    def _get_flower_color_shade(self):
        variation = random.randint(-40, 40)
        r = max(0, min(255, self.base_flower_color[0] + variation))
        g = max(0, min(255, self.base_flower_color[1] + variation))
        b = max(0, min(255, self.base_flower_color[2] + variation))
        return (r, g, b)

    def _get_branch_color(self, branch_index, total_branches):
        base_color = (80, 120, 50)
        tip_color = (140, 190, 90)
        factor = branch_index / max(1, total_branches - 1)
        r = int(base_color[0] + (tip_color[0] - base_color[0]) * factor)
        g = int(base_color[1] + (tip_color[1] - base_color[1]) * factor)
        b = int(base_color[2] + (tip_color[2] - base_color[2]) * factor)
        return (r, g, b)

    def _get_offshoot_color(self, offshoot_index, total_offshoots):
        base_color = (90, 130, 60)
        tip_color = (130, 180, 80)
        factor = offshoot_index / max(1, total_offshoots - 1) if total_offshoots > 1 else 0.5
        r = int(base_color[0] + (tip_color[0] - base_color[0]) * factor)
        g = int(base_color[1] + (tip_color[1] - base_color[1]) * factor)
        b = int(base_color[2] + (tip_color[2] - base_color[2]) * factor)
        return (r, g, b)

    def _new_branch(self, x, y, target_list):
        start_x, start_y = x, y

        if target_list is self.branch_shoots_positions:
            length_min = self.offshoot_len_min
            length_max = self.offshoot_len_max
            angle_min, angle_max = 20, 50
        else:
            length_min = self.main_branch_len_min
            length_max = self.main_branch_len_max
            angle_min, angle_max = 50, 130

        angle = random.uniform(math.radians(angle_min), math.radians(angle_max))
        length = random.uniform(length_min, length_max)

        if target_list is self.branch_shoots_positions and random.randint(0, 1) == 1:
            angle = math.pi - angle

        x_trans = math.cos(angle) * length
        y_trans = -1 * math.sin(angle) * length

        target_list.append(((start_x, start_y), (start_x + x_trans, start_y + y_trans)))

    def _draw_leaf(self, surface, x, y, angle, size=1, leaf_color=(34, 139, 34)):
        cos_a, sin_a = math.cos(angle), math.sin(angle)
        points = []
       
        for i in range(8):
            t = i / 7.0 * math.pi * 2
            if t <= math.pi:
                r = size * (1 - 0.3 * abs(t - math.pi/2) / (math.pi/2))
            else:
                r = size * 0.7 * (1 - 0.5 * abs(t - 3*math.pi/2) / (math.pi/2))
            
            px = r * math.cos(t)
            py = r * math.sin(t) * 2
            rotated_x = px * cos_a - py * sin_a
            rotated_y = px * sin_a + py * cos_a
            points.append((x + rotated_x, y + rotated_y))
        
        if len(points) >= 3:
            pygame.draw.polygon(surface, leaf_color, points)

    def _draw_flower(self, surface, x, y, size, color):
        num_petals = 5
        petal_color = color
        center_color = (255, 223, 0)

        for i in range(num_petals):
            angle = (i / num_petals) * 2 * math.pi
            px = x + math.cos(angle) * size
            py = y + math.sin(angle) * size
            pygame.draw.circle(surface, petal_color, (int(px), int(py)), int(size))

        pygame.draw.circle(surface, center_color, (int(x), int(y)), int(size * 0.6))

    def _draw_offshoot(self, color, width, i):
        grow_mult = 1 + (len(self.branch_shoots_positions) - i) / len(self.branch_shoots_positions)
        trans_x = (self.branch_shoots_positions[i][1][0] - self.branch_shoots_positions[i][0][0]) * grow_mult
        trans_y = (self.branch_shoots_positions[i][1][1] - self.branch_shoots_positions[i][0][1]) * grow_mult

        mid_x = self.branch_shoots_positions[i][0][0] + trans_x / 2
        mid_y = self.branch_shoots_positions[i][0][1] + trans_y / 2
        end_x = self.branch_shoots_positions[i][0][0] + trans_x
        end_y = self.branch_shoots_positions[i][0][1] + trans_y + self.offshoot_pos_seed[i]
       
        pygame.draw.line(self.canvas, color, self.branch_shoots_positions[i][0], (mid_x, mid_y), width)
        second_width = max(1, int(width / 1.7))
        pygame.draw.line(self.canvas, color, (mid_x, mid_y), (end_x, end_y), second_width)
       
        leaf_color = (max(0, min(255, color[0] - 20)), max(0, min(255, color[1] + 40)), max(0, min(255, color[2] - 10)))
       
        if i < len(self.leaf_angle_offsets):
            leaf_angle1 = math.atan2(trans_y, trans_x) + self.leaf_angle_offsets[i]['mid']
            self._draw_leaf(self.canvas, mid_x, mid_y, leaf_angle1, 0.8, leaf_color)
           
            leaf_angle2 = math.atan2(trans_y + self.offshoot_pos_seed[i], trans_x) + self.leaf_angle_offsets[i]['end']
            self._draw_leaf(self.canvas, end_x, end_y, leaf_angle2, 1.0, leaf_color)
           
            if self.leaf_extra_positions[i]['show']:
                extra_x = self.branch_shoots_positions[i][0][0] + trans_x * self.leaf_extra_positions[i]['position']
                extra_y = self.branch_shoots_positions[i][0][1] + trans_y * self.leaf_extra_positions[i]['position']
                extra_angle = leaf_angle1 + self.leaf_angle_offsets[i]['extra']
                self._draw_leaf(self.canvas, extra_x, extra_y, extra_angle, 0.6, leaf_color)

        if i < len(self.flower_data):
            if self.flower_data[i]['show_mid']:
                self._draw_flower(self.canvas, mid_x, mid_y, self.flower_data[i]['size_mid'], self.flower_data[i]['color_mid'])
            if self.flower_data[i]['show_end']:
                self._draw_flower(self.canvas, end_x, end_y, self.flower_data[i]['size_end'], self.flower_data[i]['color_end'])

    def grow(self):
        if self.growth_stage < self.growth_cap:
            tip_x, tip_y = self.branch_positions[self.growth_stage][1]
            self._new_branch(tip_x, tip_y, self.branch_positions)
            
            if random.random() > 0.3:
                self._new_branch(tip_x, tip_y, self.branch_shoots_positions)
            else:
                self.branch_shoots_positions.append(None)
           
            self.growth_stage += 1

    def draw(self, target_surface):
        self.canvas.fill((0, 0, 0, 0))

        total_branches = len(self.branch_positions)
        for i in range(total_branches):
            color = self._get_branch_color(i, total_branches)
            width = max(1, int((total_branches - i) / self.thinness))
            pygame.draw.line(self.canvas, color, self.branch_positions[i][0], self.branch_positions[i][1], width)
 
        total_offshoots = sum(1 for x in self.branch_shoots_positions if x is not None)
        offshoot_count = 0
        for i in range(len(self.branch_shoots_positions)):
            if self.branch_shoots_positions[i] is not None:
                color = self._get_offshoot_color(offshoot_count, total_offshoots)
                width = max(1, int((len(self.branch_shoots_positions) - i) / 2 / self.thinness))
                self._draw_offshoot(color, width, i)
                offshoot_count += 1
       
        scaled_canvas = pygame.transform.scale_by(self.canvas, self.scale)
        blit_rect = scaled_canvas.get_rect()
        blit_rect.centerx = self.pos_x
        blit_rect.bottom = self.pos_y
        target_surface.blit(scaled_canvas, blit_rect)
        return blit_rect

def load_plants():
    c.execute("SELECT id FROM notes")
    notes = c.fetchall()
    for note in notes:
        note_id = note[0]
        if note_id not in plant_objects:
            plant_objects[note_id] = Plant(x=0, y=0)

def main():
    global current_screen_index, notes_state, note_title, note_body, note_focus, active_note, search_active, search_text, scroll_offset, notes_list_scroll
    global growth_animation_active, plant_to_grow, growth_stages_remaining, last_growth_time
    clock = pygame.time.Clock()
    running = True

    load_plants()

    while running:
        if growth_animation_active:
            current_time = pygame.time.get_ticks()
            # check if 350ms have passed
            if current_time - last_growth_time > 350:
                if growth_stages_remaining > 0 and plant_to_grow:
                    plant_to_grow.grow()
                    growth_stages_remaining -= 1
                    last_growth_time = current_time # reset timer for next stage
                
                # all stages grown, deactivate animation
                if growth_stages_remaining == 0:
                    growth_animation_active = False
                    plant_to_grow = None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                conn.commit()
                conn.close()
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mx, my = event.pos

                    home_click_handled = False
                    if screens[current_screen_index] == "home":
                        for note_id, rect in home_plant_rects.items():
                            if rect and rect.collidepoint((mx, my)):
                                c.execute("SELECT * FROM notes WHERE id=?", (note_id,))
                                active_note = c.fetchone()
                                
                                if note_id in plant_objects:
                                    plant = plant_objects[note_id]
                                    growth_amount = random.randint(3, 5)
                                    trigger_growth_animation(plant, growth_amount)

                                current_screen_index = 1
                                notes_state = "view"
                                scroll_offset = 0
                                home_click_handled = True
                                break

                    if home_click_handled:
                        pass
                    elif prev_button_rect.collidepoint((mx, my)):
                        handle_prev_button()
                    elif next_button_rect.collidepoint((mx, my)):
                        if screens[current_screen_index] == "note" and notes_state in ["view", "editor"]:
                            notes_state = "list"
                            active_note = None
                            scroll_offset = 0
                            notes_list_scroll = 0
                        else:
                            current_screen_index = (current_screen_index + 1) % len(screens)
                    elif newnote_button_rect.collidepoint((mx, my)):
                        current_screen_index = 1
                        notes_state = "editor"
                        note_title = ""
                        note_body = ""
                        note_focus = "title"
                        active_note = None
                    elif hamburger_rect.collidepoint((mx, my)):
                        current_screen_index = 0
                        notes_state = "list"
                        active_note = None
                        scroll_offset = 0
                        notes_list_scroll = 0
                        search_active = False
                        note_title = ""
                        note_body = ""
                        note_focus = "title"
                    elif searchbar_rect.collidepoint((mx, my)):
                        search_active = True
                    elif screens[current_screen_index] == "note" and notes_state == "editor":
                        if title_textbox_rect.collidepoint((mx, my)):
                            note_focus = "title"
                        elif desc_textbox_rect.collidepoint((mx, my)):
                            note_focus = "body"
                    else:
                        if screens[current_screen_index] == "note":
                            if notes_state == "list":
                                notes = fetch_notes(search_text)
                                notes_list_top = bg_rect.top + 30
                                notes_list_left = bg_rect.left + 20
                                notes_list_width = bg_rect.width - 40
                                note_height = 60
                                note_spacing = 10
                                start_y = notes_list_top - (notes_list_scroll * (note_height + note_spacing))
                                
                                for i, (note_id, title) in enumerate(notes):
                                    y_pos = start_y + i * (note_height + note_spacing)
                                    note_rect = pygame.Rect(notes_list_left + 10, y_pos, notes_list_width - 20, note_height)
                                    if note_rect.collidepoint((mx, my)):
                                        c.execute("SELECT * FROM notes WHERE id=?", (note_id,))
                                        active_note = c.fetchone()
                                        notes_state = "view"
                                        scroll_offset = 0
                                        if note_id in plant_objects:
                                            plant = plant_objects[note_id]
                                            growth_amount = random.randint(3, 5)
                                            trigger_growth_animation(plant, growth_amount)

                            elif notes_state == "view" and (delete_button_rect or edit_button_rect):
                                if delete_button_rect and delete_button_rect.collidepoint((mx, my)):
                                    delete_note(active_note[0])
                                    notes_state = "list"
                                    active_note = None
                                    scroll_offset = 0
                                    notes_list_scroll = 0
                                
                                if edit_button_rect and edit_button_rect.collidepoint((mx, my)):
                                    notes_state = "editor"
                                    note_title = active_note[1]
                                    note_body = active_note[2]
                                    note_focus = "title"
                                    scroll_offset = 0

                        search_active = False
                
                elif event.button == 4:
                    if screens[current_screen_index] == "note":
                        if notes_state == "view":
                            handle_scroll("up")
                        elif notes_state == "list":
                            handle_notes_list_scroll("up")
                
                elif event.button == 5:
                    if screens[current_screen_index] == "note":
                        if notes_state == "view":
                            handle_scroll("down")
                        elif notes_state == "list":
                            handle_notes_list_scroll("down")

            elif event.type == pygame.KEYDOWN:
                if search_active:
                    if event.key == pygame.K_BACKSPACE:
                        search_text = search_text[:-1]
                        notes_list_scroll = 0
                    elif event.key == pygame.K_RETURN:
                        search_active = False
                    else:
                        search_text += event.unicode
                        notes_list_scroll = 0
                elif notes_state == "editor":
                    if note_focus == "title":
                        if event.key == pygame.K_BACKSPACE:
                            note_title = note_title[:-1]
                        elif event.key == pygame.K_RETURN:
                            note_focus = "body"
                        else:
                            note_title += event.unicode
                    elif note_focus == "body":
                        if event.key == pygame.K_BACKSPACE:
                            note_body = note_body[:-1]
                        elif event.key == pygame.K_RETURN:
                            if active_note:
                                c.execute("UPDATE notes SET title=?, body=? WHERE id=?", 
                                         (note_title, note_body, active_note[0]))
                            else:
                                c.execute("INSERT INTO notes (title, body) VALUES (?, ?)", (note_title, note_body))
                                new_note_id = c.lastrowid
                                plant_objects[new_note_id] = Plant(x=0, y=0)
                            conn.commit()
                            notes_state = "list"
                            active_note = None
                        else:
                            note_body += event.unicode
                elif screens[current_screen_index] == "note":
                    if notes_state == "view":
                        if event.key == pygame.K_UP:
                            handle_scroll("up")
                        elif event.key == pygame.K_DOWN:
                            handle_scroll("down")
                    elif notes_state == "list":
                        if event.key == pygame.K_UP:
                            handle_notes_list_scroll("up")
                        elif event.key == pygame.K_DOWN:
                            handle_notes_list_scroll("down")

        draw_screen()
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()