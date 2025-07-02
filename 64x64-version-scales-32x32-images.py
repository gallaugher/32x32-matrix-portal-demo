# Multi-Animation LED Matrix Loop - 64x64 Version
# Scaled for 64x64 HUB75 displays - CircuitPython 9.x/10.x compatible
# Prof. John Gallaugher & GPT-4o — July 2025

import time, board, displayio
from adafruit_matrixportal.matrix import Matrix
import adafruit_imageload

# ==== Configuration ====
matrix_width = 64
matrix_height = 64
animation_speed = 0.1  # Time between frames
play_time = 3.0  # Duration per animation
transition_frames = 5  # Duration of transition effect
image_path = "graphics/"  # Folder containing .bmp files
bitmap_names = ["octopus", "ghost", "parrot", "girl-earing-half", "mona-half"]

# ==== Set up display ====
# Note: For 64x64 displays, ensure the Address E line jumper is soldered!
# Check your matrix datasheet - usually pin 8, sometimes pin 16
matrix = Matrix(
    width=matrix_width,
    height=matrix_height,
    bit_depth=4,  # Reduced bit depth to minimize flashing
    alt_addr_pins=None  # Usually not needed, but set if your matrix requires it
)
display = matrix.display

# Main display group
group = displayio.Group()
display.root_group = group


def scale_bitmap_2x(source_bitmap, source_palette):
    """Scale a 32x32 bitmap to 64x64 by making each pixel into a 2x2 block"""
    # Create new 64x64 bitmap with same palette
    scaled_bitmap = displayio.Bitmap(64, 64, len(source_palette))

    # Copy each pixel as a 2x2 block
    for y in range(32):
        for x in range(32):
            pixel_value = source_bitmap[x, y]
            # Map each source pixel to a 2x2 area in the scaled bitmap
            scaled_bitmap[x * 2, y * 2] = pixel_value
            scaled_bitmap[x * 2 + 1, y * 2] = pixel_value
            scaled_bitmap[x * 2, y * 2 + 1] = pixel_value
            scaled_bitmap[x * 2 + 1, y * 2 + 1] = pixel_value

    return scaled_bitmap


def play_animation(bitmap_name, duration):
    bmp_file_path = "/" + image_path + bitmap_name + ".bmp"

    # Load bitmap and palette
    image_bit, image_pal = adafruit_imageload.load(
        bmp_file_path,
        bitmap=displayio.Bitmap,
        palette=displayio.Palette
    )

    # Detect if this is a 32x32 bitmap (legacy) or 64x64 bitmap
    if image_bit.height == 32:
        # Handle 32x32 bitmaps - scale to 64x64
        if image_bit.width % 32 != 0:
            raise ValueError(
                f"❌ {bitmap_name}.bmp width = {image_bit.width}, must be multiple of 32 for 32px high bitmaps")

        original_frames = image_bit.width // 32
        print(f"📈 Scaling 32x32 bitmap to 64x64 (true 2x scaling)")

        # Create scaled bitmap for each frame
        scaled_width = original_frames * 64
        scaled_bitmap = displayio.Bitmap(scaled_width, 64, len(image_pal))

        # Scale each frame
        for frame in range(original_frames):
            # Extract source frame
            source_x_start = frame * 32

            # Scale frame pixel by pixel
            for y in range(32):
                for x in range(32):
                    pixel_value = image_bit[source_x_start + x, y]
                    # Map to scaled position
                    dest_x_start = frame * 64
                    scaled_bitmap[dest_x_start + x * 2, y * 2] = pixel_value
                    scaled_bitmap[dest_x_start + x * 2 + 1, y * 2] = pixel_value
                    scaled_bitmap[dest_x_start + x * 2, y * 2 + 1] = pixel_value
                    scaled_bitmap[dest_x_start + x * 2 + 1, y * 2 + 1] = pixel_value

        # Use scaled bitmap
        final_bitmap = scaled_bitmap
        frame_width = 64
        frame_height = 64
        total_frames = original_frames

    elif image_bit.height == 64:
        # Handle 64x64 bitmaps - use as-is
        if image_bit.width % 64 != 0:
            raise ValueError(
                f"❌ {bitmap_name}.bmp width = {image_bit.width}, must be multiple of 64 for 64px high bitmaps")

        final_bitmap = image_bit
        frame_width = 64
        frame_height = 64
        total_frames = image_bit.width // 64

        print(f"📐 Using 64x64 bitmap full screen")

    else:
        raise ValueError(f"❌ {bitmap_name}.bmp height = {image_bit.height}, must be 32 or 64 pixels")

    # Remove previous sprite (if any)
    while len(group) > 0:
        group.pop()

    # Create single tile grid for the final bitmap
    image_grid = displayio.TileGrid(
        bitmap=final_bitmap,
        pixel_shader=image_pal,
        width=1,
        height=1,
        tile_width=frame_width,
        tile_height=frame_height,
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
        print(f"[{bitmap_name}] Frame {frame}/{total_frames}")
        time.sleep(animation_speed)


def transition_to_black():
    # More efficient black screen transition to reduce flashing
    # Remove old sprite efficiently
    while len(group) > 0:
        group.pop()

    # Brief pause without complex bitmap creation
    for _ in range(transition_frames):
        time.sleep(animation_speed)


# ==== Run the loop ====
print("✅ 64x64 Matrix Portal Animation Loop Starting!")
print(f"📐 Display: {matrix_width}x{matrix_height}")
print(f"🎨 Bit depth: 4 (optimized for smooth playback)")
print("📈 32x32 bitmaps will be scaled 2x to fill screen")
print("⚠️  Ensure Address E line jumper is soldered for 64x64 displays!")

while True:
    for bitmap_name in bitmap_names:
        try:
            play_animation(bitmap_name, play_time)
            transition_to_black()
        except Exception as e:
            print(f"❌ Error with {bitmap_name}: {e}")
            transition_to_black()  # Clear display on error
            continue