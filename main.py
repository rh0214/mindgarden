import pygame
import sys

# Initialize pygame
pygame.init()

# Resolution
SCREEN_WIDTH = 440
SCREEN_HEIGHT = 782
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("MindGarden")

# Colors
GREEN = (162, 217, 140)

# Screens
screens = ["home", "tree", "note"]
current_screen_index = 0

# Load images
prev_button_img = pygame.image.load("assets/previousbutton.png").convert_alpha()
next_button_img = pygame.image.load("assets/nextbutton.png").convert_alpha()
newnote_button_img = pygame.image.load("assets/newnote.png").convert_alpha()
hamburger_img = pygame.image.load("assets/menu.png").convert_alpha()
searchbar_img = pygame.image.load("assets/searchbar.png").convert_alpha()

# Button sizes (hard-coded per request)
prev_next_w = (103/220) * SCREEN_WIDTH   # exact width
prev_next_h = prev_next_w * (22/103)
searchbar_w = (185/220) * SCREEN_WIDTH
searchbar_h = (searchbar_w) * (22/185)
hamburger_w = (20/220) * SCREEN_WIDTH
hamburger_h = hamburger_w * (22/20)
newnote_w = (210/220) * SCREEN_WIDTH
newnote_h = newnote_w * (39/210)

# Scale buttons
prev_button_img = pygame.transform.scale(prev_button_img, (prev_next_w, prev_next_h))
next_button_img = pygame.transform.scale(next_button_img, (prev_next_w, prev_next_h))
newnote_button_img = pygame.transform.scale(newnote_button_img,(newnote_w, newnote_h))
hamburger_img = pygame.transform.scale(hamburger_img, (hamburger_w, hamburger_h))
searchbar_img = pygame.transform.scale(searchbar_img, (searchbar_w, searchbar_h))

# Button rects
margin = 11
newnote_button_rect = newnote_button_img.get_rect(
    midbottom=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - margin)
)
prev_button_rect = prev_button_img.get_rect(
    bottomleft=(margin, newnote_button_rect.top  - (margin - 5))
)
next_button_rect = next_button_img.get_rect(
    bottomright=(SCREEN_WIDTH - margin, newnote_button_rect.top - (margin - 5))
)
hamburger_rect = hamburger_img.get_rect(topleft=(margin, margin))
searchbar_rect = searchbar_img.get_rect(
    midleft=(hamburger_rect.right + (margin -2), hamburger_rect.centery)
)

def draw_screen():
    screen.fill(GREEN)

    # Current screen text
    font = pygame.font.SysFont(None, 60)  # scaled for higher res
    text = font.render(screens[current_screen_index], True, (255, 255, 255))
    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(text, text_rect)

    # UI
    screen.blit(prev_button_img, prev_button_rect)
    screen.blit(next_button_img, next_button_rect)
    screen.blit(newnote_button_img, newnote_button_rect)

    # Top bar
    screen.blit(hamburger_img, hamburger_rect)
    screen.blit(searchbar_img, searchbar_rect)

def main():
    
    global current_screen_index
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if prev_button_rect.collidepoint((mx, my)):
                    current_screen_index = (current_screen_index - 1) % len(screens)
                elif next_button_rect.collidepoint((mx, my)):
                    current_screen_index = (current_screen_index + 1) % len(screens)
                elif newnote_button_rect.collidepoint((mx, my)):
                    print("New note clicked!")
                elif hamburger_rect.collidepoint((mx, my)):
                    print("Hamburger clicked!")
                elif searchbar_rect.collidepoint((mx, my)):
                    print("Search clicked!")

        draw_screen()
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
