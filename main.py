import pygame
import sys
import os
import sqlite3

# Initialize pygame
pygame.init()

# Resolution
SCREEN_WIDTH = 440
SCREEN_HEIGHT = 782
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("MindGarden")

# Colors
GREEN = (162, 217, 140)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BEIGE = (245, 236, 210)
RED = (200, 50, 50)

# Screens
screens = ["home", "tree", "note"]
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

# Button sizes
prev_next_w = (103 / 220) * SCREEN_WIDTH
prev_next_h = prev_next_w * (22 / 103)
searchbar_w = (185 / 220) * SCREEN_WIDTH
searchbar_h = searchbar_w * (22 / 185)
hamburger_w = (20 / 220) * SCREEN_WIDTH
hamburger_h = hamburger_w * (22 / 20)
newnote_w = (210 / 220) * SCREEN_WIDTH
newnote_h = newnote_w * (39 / 210)

# Scale buttons
prev_button_img = pygame.transform.scale(prev_button_img, (prev_next_w, prev_next_h))
next_button_img = pygame.transform.scale(next_button_img, (prev_next_w, prev_next_h))
newnote_button_img = pygame.transform.scale(newnote_button_img, (newnote_w, newnote_h))
hamburger_img = pygame.transform.scale(hamburger_img, (hamburger_w, hamburger_h))
searchbar_img = pygame.transform.scale(searchbar_img, (searchbar_w, searchbar_h))
searchbar_blank_img = pygame.transform.scale(searchbar_blank_img, (searchbar_w, searchbar_h))

# Button rects
margin = 11
newnote_button_rect = newnote_button_img.get_rect(
    midbottom=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - margin)
)

button_spacing = 15
prev_button_rect = prev_button_img.get_rect(
    midbottom=(SCREEN_WIDTH // 4, newnote_button_rect.top - button_spacing)
)
next_button_rect = next_button_img.get_rect(
    midbottom=(3 * SCREEN_WIDTH // 4, newnote_button_rect.top - button_spacing)
)

hamburger_rect = hamburger_img.get_rect(topleft=(margin, margin))
searchbar_rect = searchbar_img.get_rect(
    midleft=(hamburger_rect.right + (margin - 2), hamburger_rect.centery)
)

# Back button (for viewing a note)
back_button_rect = pygame.Rect(20, 60, 100, 40)

# Fonts
FONT_PATH = os.path.join(BASE_DIR, "assets", "pixelfont.ttf")
title_font = pygame.font.Font(FONT_PATH, 40)
body_font = pygame.font.Font(FONT_PATH, 24)

# Notes screen states
notes_state = "list"  # "list", "editor", "view"
active_note = None
note_title = ""
note_body = ""
note_focus = "title"

# Searchbar state
search_active = False
search_text = ""

# Store delete buttons dynamically
delete_buttons = []

def fetch_notes(query=""):
    if query:
        c.execute("SELECT id, title FROM notes WHERE title LIKE ?", ('%' + query + '%',))
    else:
        c.execute("SELECT id, title FROM notes")
    return c.fetchall()

def delete_note(note_id):
    c.execute("DELETE FROM notes WHERE id=?", (note_id,))
    conn.commit()

def draw_screen():
    global delete_buttons
    delete_buttons = []

    screen.fill(GREEN)

    # Always draw nav + utility buttons
    screen.blit(prev_button_img, prev_button_rect)
    screen.blit(next_button_img, next_button_rect)
    screen.blit(newnote_button_img, newnote_button_rect)
    screen.blit(hamburger_img, hamburger_rect)

    # Searchbar
    if search_active:
        screen.blit(searchbar_blank_img, searchbar_rect)
    else:
        screen.blit(searchbar_img, searchbar_rect)

    if search_text:
        search_surface = body_font.render(search_text, True, BLACK)
        search_rect_draw = search_surface.get_rect(midleft=(searchbar_rect.left + 40, searchbar_rect.centery))
        screen.blit(search_surface, search_rect_draw)

    # Notes area baseline
    notes_top = SCREEN_HEIGHT // 2 + 20

    if screens[current_screen_index] == "home":
        text = title_font.render("Home Screen", True, WHITE)
        screen.blit(text, text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)))

    elif screens[current_screen_index] == "tree":
        text = title_font.render("Tree Screen", True, WHITE)
        screen.blit(text, text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)))

    elif screens[current_screen_index] == "note":
        if notes_state == "list":
            notes = fetch_notes(search_text)
            y = notes_top
            for note_id, title in notes:
                note_rect = pygame.Rect(40, y, 300, 60)
                pygame.draw.rect(screen, BEIGE, note_rect, border_radius=12)

                title_surface = body_font.render(title, True, BLACK)
                screen.blit(title_surface, (note_rect.x + 15, note_rect.y + 15))

                delete_rect = pygame.Rect(note_rect.right + 10, y + 15, 40, 30)
                pygame.draw.rect(screen, RED, delete_rect, border_radius=6)
                x_text = body_font.render("X", True, WHITE)
                x_rect = x_text.get_rect(center=delete_rect.center)
                screen.blit(x_text, x_rect)

                delete_buttons.append((delete_rect, note_id))
                y += 80

        elif notes_state == "editor":
            # Moved editor UI 30px lower
            editor_top = SCREEN_HEIGHT // 3 + 119

            title_rect = pygame.Rect(40, editor_top, 360, 40)
            pygame.draw.rect(screen, BEIGE, title_rect, border_radius=12)
            title_surface = body_font.render(note_title if note_title else "Title...", True, BLACK)
            screen.blit(title_surface, (title_rect.x + 10, title_rect.y + 10))

            body_rect = pygame.Rect(40, editor_top + 60, 360, 180)
            pygame.draw.rect(screen, BEIGE, body_rect, border_radius=12)

            lines = note_body.split("\n") if note_body else ["Body..."]
            y_offset = 10
            for line in lines:
                body_surface = body_font.render(line, True, BLACK)
                screen.blit(body_surface, (body_rect.x + 10, body_rect.y + y_offset))
                y_offset += 25

        elif notes_state == "view" and active_note:
            pygame.draw.rect(screen, BEIGE, back_button_rect, border_radius=8)
            back_text = body_font.render("Back", True, BLACK)
            screen.blit(back_text, (back_button_rect.x + 20, back_button_rect.y + 10))

            title_surface = title_font.render(active_note[1], True, BLACK)
            body_surface = body_font.render(active_note[2], True, BLACK)
            screen.blit(title_surface, (50, notes_top))
            screen.blit(body_surface, (50, notes_top + 50))

def main():
    global current_screen_index, notes_state, note_title, note_body, note_focus, active_note, search_active, search_text
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                conn.commit()
                conn.close()
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if prev_button_rect.collidepoint((mx, my)):
                    current_screen_index = (current_screen_index - 1) % len(screens)
                elif next_button_rect.collidepoint((mx, my)):
                    current_screen_index = (current_screen_index + 1) % len(screens)
                elif newnote_button_rect.collidepoint((mx, my)) and screens[current_screen_index] == "note":
                    notes_state = "editor"
                    note_title = ""
                    note_body = ""
                    note_focus = "title"
                elif hamburger_rect.collidepoint((mx, my)):
                    print("Hamburger clicked!")
                elif searchbar_rect.collidepoint((mx, my)):
                    search_active = True
                else:
                    if screens[current_screen_index] == "note":
                        if notes_state == "list":
                            notes = fetch_notes(search_text)
                            y = SCREEN_HEIGHT // 2 + 10
                            for note_id, title in notes:
                                note_rect = pygame.Rect(40, y, 300, 60)
                                if note_rect.collidepoint((mx, my)):
                                    c.execute("SELECT * FROM notes WHERE id=?", (note_id,))
                                    active_note = c.fetchone()
                                    notes_state = "view"
                                y += 80

                            for rect, note_id in delete_buttons:
                                if rect.collidepoint((mx, my)):
                                    delete_note(note_id)

                        elif notes_state == "view":
                            if back_button_rect.collidepoint((mx, my)):
                                notes_state = "list"
                                active_note = None
                    search_active = False

            elif event.type == pygame.KEYDOWN:
                if search_active:
                    if event.key == pygame.K_BACKSPACE:
                        search_text = search_text[:-1]
                    elif event.key == pygame.K_RETURN:
                        search_active = False
                    else:
                        search_text += event.unicode
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
                            c.execute("INSERT INTO notes (title, body) VALUES (?, ?)", (note_title, note_body))
                            conn.commit()
                            notes_state = "list"
                        else:
                            note_body += event.unicode

        draw_screen()
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
