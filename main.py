import pygame
import sys
from PIL import Image
import os
import random

# Initialize Pygame
pygame.init()

# Set up display with 9:16 aspect ratio (portrait mode)
SCREEN_WIDTH = 608  # 1080 * 9/16 = 607.5, rounded to 608
SCREEN_HEIGHT = 1080
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Green Field with Animated Grass")

# Green color updated to #79d03d
GREEN_BACKGROUND = (121, 208, 61)  # RGB values for #79d03d

# Clock for controlling frame rate
clock = pygame.time.Clock()
FPS = 60


class AnimatedGrass:
    def __init__(self, gif_path, x, y, scale=1.0):
        """
        Initialize animated grass from a GIF file
        gif_path: path to your grass GIF file
        x, y: position on screen
        scale: size multiplier
        """
        self.x = x
        self.y = y
        self.scale = scale
        self.frames = []
        self.current_frame = 0
        self.frame_timer = 0
        self.frame_delay = 100  # milliseconds between frames
        
        # Load GIF frames
        self.load_gif_frames(gif_path)
    
    def load_gif_frames(self, gif_path):
        """Load all frames from a GIF file"""
        try:
            print(f"Attempting to load: {gif_path}")
            
            # Check if file exists
            if not os.path.exists(gif_path):
                print(f"File does not exist: {gif_path}")
                raise FileNotFoundError(f"File not found: {gif_path}")
            
            # Open GIF with PIL
            gif = Image.open(gif_path)
            print(f"Successfully opened {gif_path}")
            
            # Extract all frames
            frame_count = 0
            while True:
                try:
                    frame = gif.copy().convert('RGBA')
                    
                    if self.scale != 1.0:
                        new_size = (int(frame.width * self.scale), int(frame.height * self.scale))
                        frame = frame.resize(new_size)
                    
                    pygame_surface = pygame.image.fromstring(frame.tobytes(), frame.size, 'RGBA')
                    self.frames.append(pygame_surface)
                    
                    frame_count += 1
                    gif.seek(frame_count)
                    
                except EOFError:
                    break  # End of frames
            
            print(f"Loaded {len(self.frames)} frames from {gif_path}")
                    
        except FileNotFoundError:
            print(f"Warning: GIF file '{gif_path}' not found. Creating placeholder.")
            placeholder = pygame.Surface((40, 60), pygame.SRCALPHA)
            pygame.draw.polygon(placeholder, (34, 139, 34), [(20, 60), (15, 30), (10, 0), (25, 5), (30, 0), (25, 30)])
            self.frames = [placeholder]
        except Exception as e:
            print(f"Error loading GIF '{gif_path}': {e}")
            placeholder = pygame.Surface((40, 60), pygame.SRCALPHA)
            pygame.draw.polygon(placeholder, (34, 139, 34), [(20, 60), (15, 30), (10, 0), (25, 5), (30, 0), (25, 30)])
            self.frames = [placeholder]
    
    def update(self, dt):
        """Update animation frame"""
        if len(self.frames) > 1:
            self.frame_timer += dt
            if self.frame_timer >= self.frame_delay:
                self.current_frame = (self.current_frame + 1) % len(self.frames)
                self.frame_timer = 0
    
    def draw(self, screen):
        """Draw current frame to screen"""
        if self.frames:
            screen.blit(self.frames[self.current_frame], (self.x, self.y))


def create_random_grass_field(num_grass=25, grass_gif_files=None):
    """Create a field of randomly placed grass sprites"""
    if not grass_gif_files:
        grass_gif_files = ["placeholder.gif"]  # fallback
    
    grass_sprites = []
    for i in range(num_grass):
        x = random.randint(10, SCREEN_WIDTH - 60)
        y = random.randint(50, SCREEN_HEIGHT - 30)
        scale = random.uniform(0.8, 1.8)
        grass_file = random.choice(grass_gif_files)
        grass_sprites.append(AnimatedGrass(grass_file, x, y, scale))
    return grass_sprites


def main():
    # Load all GIF files automatically from assets folder
    assets_folder = "assets"
    grass_files = [os.path.join(assets_folder, f) for f in os.listdir(assets_folder) if f.lower().endswith(".gif")]
    
    if not grass_files:
        print("⚠️ No GIFs found in assets folder. Using placeholders.")
    
    # Create randomly placed grass field
    grass_sprites = create_random_grass_field(
        num_grass=30,
        grass_gif_files=grass_files
    )
    
    running = True
    while running:
        dt = clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
        
        for grass in grass_sprites:
            grass.update(dt)
        
        screen.fill(GREEN_BACKGROUND)
        
        for grass in grass_sprites:
            grass.draw(screen)
        
        for y in range(SCREEN_HEIGHT):
            alpha = int(30 * (y / SCREEN_HEIGHT))
            color = (max(0, GREEN_BACKGROUND[0] - alpha), 
                     max(0, GREEN_BACKGROUND[1] - alpha), 
                     max(0, GREEN_BACKGROUND[2] - alpha))
            pygame.draw.line(screen, color, (0, y), (SCREEN_WIDTH, y))
        
        for grass in grass_sprites:
            grass.draw(screen)
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    print("Pygame Grass Field Program")
    print("Instructions:")
    print("1. Put your grass GIFs inside the 'assets' folder")
    print("2. Program auto-loads all .gif files in that folder")
    print("3. Press ESC to exit")
    main()
