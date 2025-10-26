import arcade

SHEET_PATH = "sprites/Vampires1_Walk_full.png"
COLUMNS, ROWS = 6, 4
COUNT = COLUMNS * ROWS  # 24

sheet = arcade.load_spritesheet(SHEET_PATH)

# Figure out each frame size from the full image
full_w, full_h = sheet.image.size  # PIL.Image
frame_w, frame_h = full_w // COLUMNS, full_h // ROWS

# Slice to textures (optionally pass margin=(l, r, b, t) if needed)
textures = sheet.get_texture_grid(size=(frame_w, frame_h),
                                  columns=COLUMNS,
                                  count=COUNT)

# Use them on a sprite
player = arcade.Sprite(center_x=200, center_y=200)
player.textures = textures
player.texture = textures[0]

# Example animation tick:
current = 0
def on_update(dt):
    global current
    current = (current + 1) % COUNT
    player.texture = player.textures[current]

arcade.open_window(800, 600, "Sprite Sheet Example")
arcade.run()