# Multi-Animation LED Matrix Loop
# Prof. John Gallaugher & GPT-4o — May 2025

import time, board, displayio
from adafruit_matrixportal.matrix import Matrix
import adafruit_imageload

# ==== Configuration ====
matrix_width = 32
matrix_height = 32
animation_speed = 0.1        # Time between frames
play_time = 3.0              # Duration per animation
transition_frames = 5        # Duration of transition effect
image_path = "graphics/"     # Folder containing .bmp files
bitmap_names = ["octopus", "ghost", "parrot", "girl-earing-half", "mona-half"]

# ==== Set up display ====
matrix = Matrix(width=matrix_width, height=matrix_height, bit_depth=6)
display = matrix.display

# Main display group
group = displayio.Group()
display.root_group = group

def play_animation(bitmap_name, duration):
    bmp_file_path = "/" + image_path + bitmap_name + ".bmp"

    # Load bitmap and palette
    image_bit, image_pal = adafruit_imageload.load(
        bmp_file_path,
        bitmap=displayio.Bitmap,
        palette=displayio.Palette
    )

    # Check dimensions
    if image_bit.width % matrix_width != 0:
        raise ValueError(f"❌ {bitmap_name}.bmp width = {image_bit.width}, must be multiple of {matrix_width}")
    if image_bit.height != matrix_height:
        raise ValueError(f"❌ {bitmap_name}.bmp height = {image_bit.height}, must be {matrix_height}")

    total_frames = image_bit.width // matrix_width

    # Remove previous sprite (if any)
    while len(group) > 0:
        group.pop()

    # Add new animation grid
    image_grid = displayio.TileGrid(
        bitmap=image_bit,
        pixel_shader=image_pal,
        width=1,
        height=1,
        tile_width=matrix_width,
        tile_height=matrix_height,
        x=0,
        y=0
    )
    group.append(image_grid)

    # Start animation
    frame = 0
    start_time = time.monotonic()

    while time.monotonic() - start_time < duration:
        image_grid[0] = frame
        frame = (frame + 1) % total_frames
        print(f"[{bitmap_name}] Frame {frame}")
        time.sleep(animation_speed)

def transition_to_black():
    # Remove old sprite
    while len(group) > 0:
        group.pop()

    # Add black frame
    black_bitmap = displayio.Bitmap(1, 1, 1)
    black_palette = displayio.Palette(1)
    black_palette[0] = 0x000000
    black_grid = displayio.TileGrid(black_bitmap, pixel_shader=black_palette)
    group.append(black_grid)

    for _ in range(transition_frames):
        time.sleep(animation_speed)

# ==== Run the loop ====
print("✅ Matrix Portal Animation Loop Starting!")

while True:
    for bitmap_name in bitmap_names:
        play_animation(bitmap_name, play_time)
        transition_to_black()
