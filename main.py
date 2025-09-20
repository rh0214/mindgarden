import pygame
import sys
import os
import random
from PIL import Image

SCREEN_WIDTH = 720
SCREEN_HEIGHT = 1280
FPS = 2
GRASS_HEIGHT_RATIO = 0.08184
NUM_GRASS = 20
DEFAULT_FRAME_DELAY_MS = 100
GREEN_BACKGROUND = (145, 204, 87)
ASSETS_FOLDER = os.path.join(os.path.dirname(__file__), "assets")
FLIP_CHANCE = 0.2 

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Green Field with Animated Grass")
clock = pygame.time.Clock()

def make_vertical_gradient(width, height, base_color, darken_amount=30):
    surf = pygame.Surface((width, height))
    for y in range(height):
        f = y / max(1, (height - 1))
        alpha = int(darken_amount * f)
        color = (
            max(0, base_color[0] - alpha),
            max(0, base_color[1] - alpha),
            max(0, base_color[2] - alpha),
        )
        pygame.draw.line(surf, color, (0, y), (width, y))
    return surf

GRADIENT_SURFACE = make_vertical_gradient(SCREEN_WIDTH, SCREEN_HEIGHT, GREEN_BACKGROUND, darken_amount=30)
_frames_cache = {}

def get_scaled_frames_for_height(gif_path, desired_height, flip=False):
    key = (os.path.abspath(gif_path), desired_height, flip)
    if key in _frames_cache:
        return _frames_cache[key]
    frames = []
    try:
        gif = Image.open(gif_path)
    except Exception as e:
        print(f"Error opening GIF {gif_path}: {e}")
        _frames_cache[key] = frames
        return frames
    frame_index = 0
    while True:
        try:
            gif.seek(frame_index)
            pil_frame = gif.convert("RGBA")
            orig_w, orig_h = pil_frame.size
            scale_factor = desired_height / orig_h
            new_w = max(1, int(orig_w * scale_factor))
            new_h = max(1, int(orig_h * scale_factor))
            pil_resized = pil_frame.resize((new_w, new_h), Image.NEAREST)
            raw_data = pil_resized.tobytes()
            surf = pygame.image.frombuffer(raw_data, pil_resized.size, "RGBA").convert_alpha()
            if flip:
                surf = pygame.transform.flip(surf, True, False)
            frames.append(surf)
            frame_index += 1
        except EOFError:
            break
        except Exception as e:
            print(f"Error while extracting frame {frame_index} from {gif_path}: {e}")
            break
    _frames_cache[key] = frames
    return frames

class AnimatedGrass:
    def __init__(self, frames, x, y, frame_delay=DEFAULT_FRAME_DELAY_MS):
        self.frames = frames or []
        self.x = x
        self.y = y
        self.current_frame = 0
        self.timer = 0
        self.frame_delay = frame_delay
        if self.frames:
            self.width = self.frames[0].get_width()
            self.height = self.frames[0].get_height()
        else:
            self.width = 0
            self.height = 0
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self, dt):
        if len(self.frames) > 1:
            self.timer += dt
            if self.timer >= self.frame_delay:
                self.timer = 0
                self.current_frame = (self.current_frame + 1) % len(self.frames)

    def draw(self, surf):
        if self.frames:
            surf.blit(self.frames[self.current_frame], (self.x, self.y))

def create_random_grass_field(num_grass=NUM_GRASS, grass_gif_files=None):
    grass_sprites = []
    base_grass_height = max(8, int(SCREEN_HEIGHT * GRASS_HEIGHT_RATIO))
    for _ in range(num_grass):
        if not grass_gif_files:
            continue
        gif_path = random.choice(grass_gif_files)
        desired_height = int(base_grass_height * random.uniform(0.7, 1.5))
        flip = random.random() < FLIP_CHANCE  # flip less frequently
        frames = get_scaled_frames_for_height(gif_path, desired_height, flip=flip)
        if not frames:
            continue
        fw, fh = frames[0].get_width(), frames[0].get_height()
        placed = False
        for _ in range(30):
            x = random.randint(0, max(0, SCREEN_WIDTH - fw))
            y = random.randint(0, max(0, SCREEN_HEIGHT - fh))
            new_rect = pygame.Rect(x, y, fw, fh)
            if not any(new_rect.colliderect(g.rect) for g in grass_sprites):
                grass_sprites.append(AnimatedGrass(frames, x, y))
                placed = True
                break
        if not placed:
            grass_sprites.append(AnimatedGrass(frames, x, y))
    return grass_sprites

def main():
    if not os.path.exists(ASSETS_FOLDER):
        print(f"Assets folder not found at: {ASSETS_FOLDER}")
        grass_files = []
    else:
        grass_files = [
            os.path.join(ASSETS_FOLDER, f)
            for f in os.listdir(ASSETS_FOLDER)
            if f.lower().endswith(".gif")
        ]
    grass_sprites = create_random_grass_field(num_grass=NUM_GRASS, grass_gif_files=grass_files)
    running = True
    while running:
        dt = clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
        for g in grass_sprites:
            g.update(dt)
        screen.fill(GREEN_BACKGROUND)
        screen.blit(GRADIENT_SURFACE, (0, 0))
        for g in grass_sprites:
            g.draw(screen)
        pygame.display.flip()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
