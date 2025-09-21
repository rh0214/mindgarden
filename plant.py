import pygame
import random
import math

pygame.init()
screen = pygame.display.set_mode((500, 400))
pygame.display.set_caption("MindGarden")
growth_stage = 0

GROWTH_CAP = 13
width, height = 100, 100
thinness = 2
canvas = pygame.Surface((width,height))
init_pos, init_endpos = (50, 100), (50, 96)
branch_positions = [(init_pos, init_endpos)]
branch_shoots_positions = []

# offshoot random y coordinate offset
offshoot_pos_seed = random.choices(range(-3, 3), k=20)

base_flower_colors = [(255, 105, 180), (255, 69, 0), (138, 43, 226), (255, 215, 0)]
base_flower_color = random.choice(base_flower_colors)
FLOWER_CHANCE = 0.4 # chance for flower on offshoot

def get_flower_color_shade(base_color):
    # random base color for flowers
    variation = random.randint(-40, 40)
    r = max(0, min(255, base_color[0] + variation))
    g = max(0, min(255, base_color[1] + variation))
    b = max(0, min(255, base_color[2] + variation))
    return (r, g, b)

# seeded random values
leaf_angle_offsets = []
leaf_extra_positions = []
flower_data = []

for i in range(20):
    leaf_angle_offsets.append({
        'mid': random.uniform(-0.5, 0.5),
        'end': random.uniform(-0.5, 0.5),
        'extra': random.uniform(-1, 1)
    })
    leaf_extra_positions.append({
        'show': random.random() < 0.3,
        'position': 0.7
    })
    flower_data.append({
        'show_mid': random.random() < FLOWER_CHANCE,
        'color_mid': get_flower_color_shade(base_flower_color),
        'size_mid': random.uniform(1.2, 2.8),
        'show_end': random.random() < FLOWER_CHANCE,
        'color_end': get_flower_color_shade(base_flower_color),
        'size_end': random.uniform(1.2, 2.8)
    })

# color calculation for main branches
def get_branch_color(branch_index, total_branches):
    base_color = (80, 120, 50)
    tip_color = (140, 190, 90)
    factor = branch_index / max(1, total_branches - 1)
    r = int(base_color[0] + (tip_color[0] - base_color[0]) * factor)
    g = int(base_color[1] + (tip_color[1] - base_color[1]) * factor)
    b = int(base_color[2] + (tip_color[2] - base_color[2]) * factor)
    return (r, g, b)

# offshoot colors
def get_offshoot_color(offshoot_index, total_offshoots):
    base_color = (90, 130, 60)
    tip_color = (130, 180, 80)
    factor = offshoot_index / max(1, total_offshoots - 1) if total_offshoots > 1 else 0.5
    r = int(base_color[0] + (tip_color[0] - base_color[0]) * factor)
    g = int(base_color[1] + (tip_color[1] - base_color[1]) * factor)
    b = int(base_color[2] + (tip_color[2] - base_color[2]) * factor)
    return (r, g, b)

def new_branch(x, y, list):
    start_x = x
    start_y = y

    if list == branch_shoots_positions:
        length_min, length_max = 5, 10
        angle_min, angle_max = 20, 50
    else:
        length_min, length_max = 2, 4
        angle_min, angle_max = 50, 130

    angle = random.uniform(math.radians(angle_min), math.radians(angle_max))
    length = random.uniform(length_min, length_max)

    if list == branch_shoots_positions:
        if random.randint(0, 1) == 1:
            angle = 3.14 - angle

    x_trans = math.cos(angle) * length
    y_trans = -1 * math.sin(angle) * length

    list.append(((start_x, start_y), (start_x + x_trans, start_y + y_trans)))

def draw_leaf(surface, x, y, angle, size=1, leaf_color=(34, 139, 34)):
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
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

def draw_flower(surface, x, y, size, color):
    num_petals = 5
    petal_color = color
    center_color = (255, 223, 0)  # yellow center for the flower

    for i in range(num_petals):
        angle = (i / num_petals) * 2 * math.pi
        px = x + math.cos(angle) * size
        py = y + math.sin(angle) * size
        pygame.draw.circle(surface, petal_color, (int(px), int(py)), int(size))

    pygame.draw.circle(surface, center_color, (int(x), int(y)), int(size * 0.6))

def update_plant():
    canvas.fill((0, 0, 0, 0))
    canvas.set_colorkey((0,0,0))

    total_branches = len(branch_positions)
    for i in range(total_branches):
        color = get_branch_color(i, total_branches)
        width = int((total_branches - i) / thinness)
        width = max(1, width)
        pygame.draw.line(canvas, color, branch_positions[i][0], branch_positions[i][1], width)

    total_offshoots = len([x for x in branch_shoots_positions if x is not None])
    offshoot_count = 0
    for i in range(len(branch_shoots_positions)):
        if branch_shoots_positions[i] is not None:
            color = get_offshoot_color(offshoot_count, total_offshoots)
            width = int((len(branch_shoots_positions) - i) / 2 / thinness)
            width = max(1, width)
            draw_offshoot(color, width, i)
            offshoot_count += 1
        else:
            continue

    factor = 4
    scaled_canvas = pygame.transform.scale_by(canvas, factor)
    screen.blit(scaled_canvas, (0,0))

def draw_offshoot(color, width, i):
    growmult = 1 + (len(branch_shoots_positions) - i) / len(branch_shoots_positions)
    trans_x = (branch_shoots_positions[i][1][0] - branch_shoots_positions[i][0][0]) * growmult
    trans_y = (branch_shoots_positions[i][1][1] - branch_shoots_positions[i][0][1]) * growmult

    mid_x = branch_shoots_positions[i][0][0] + trans_x / 2
    mid_y = branch_shoots_positions[i][0][1] + trans_y / 2
    end_x = branch_shoots_positions[i][0][0] + trans_x
    end_y = branch_shoots_positions[i][0][1] + trans_y + offshoot_pos_seed[i]
    
    pygame.draw.line(canvas, color, branch_shoots_positions[i][0], (mid_x, mid_y), width)
    second_width = max(1, int(width / 1.7))
    pygame.draw.line(canvas, color, branch_shoots_positions[i][0], (end_x, end_y), second_width)
    
    leaf_r = max(0, min(255, color[0] - 20))
    leaf_g = max(0, min(255, color[1] + 40))
    leaf_b = max(0, min(255, color[2] - 10))
    leaf_color = (leaf_r, leaf_g, leaf_b)
    
    if i < len(leaf_angle_offsets):
        leaf_angle1 = math.atan2(trans_y, trans_x) + leaf_angle_offsets[i]['mid']
        draw_leaf(canvas, mid_x, mid_y, leaf_angle1, 0.8, leaf_color)
        
        leaf_angle2 = math.atan2(trans_y + offshoot_pos_seed[i], trans_x) + leaf_angle_offsets[i]['end']
        draw_leaf(canvas, end_x, end_y, leaf_angle2, 1.0, leaf_color)
        
        if leaf_extra_positions[i]['show']:
            extra_x = branch_shoots_positions[i][0][0] + trans_x * leaf_extra_positions[i]['position']
            extra_y = branch_shoots_positions[i][0][1] + trans_y * leaf_extra_positions[i]['position']
            extra_angle = leaf_angle1 + leaf_angle_offsets[i]['extra']
            draw_leaf(canvas, extra_x, extra_y, extra_angle, 0.6, leaf_color)

    # check for and draw flowers at mid/end points
    if i < len(flower_data) and flower_data[i]['show_mid']:
        draw_flower(canvas, mid_x, mid_y, flower_data[i]['size_mid'], flower_data[i]['color_mid'])
    
    if i < len(flower_data) and flower_data[i]['show_end']:
        draw_flower(canvas, end_x, end_y, flower_data[i]['size_end'], flower_data[i]['color_end'])

new_branch(branch_positions[growth_stage][1][0], branch_positions[growth_stage][1][1], branch_positions)
growth_stage += 1
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if growth_stage < GROWTH_CAP:
                    new_branch(branch_positions[growth_stage][1][0], branch_positions[growth_stage][1][1], branch_positions)
                    if random.randint(0, 1) == 1:
                        new_branch(branch_positions[growth_stage][1][0], branch_positions[growth_stage][1][1], branch_shoots_positions)
                    else:
                        branch_shoots_positions.append(None)
                    growth_stage += 1
    
    screen.fill((20, 20, 40))
    update_plant()
    pygame.display.flip()

pygame.quit()