import arcade
WIDTH, HEIGHT = 1400, 750
TITLE = "IDk"
BG_FILE = "images/Noche de Halloween en Laranja.png"

GRAVITY    = -1400.0
THRUST_ACC = 2200.0
MAX_UP_V   = 800.0
MAX_DN_V   = -900.0
GROUND_Y   = 150
CEILING_Y  = 560

class player(arcade.Sprite):  # keep Sprite
    def __init__(self, scale):
        
        super().__init__(filename=None, scale=scale)
        self.center_x = 200
        self.center_y = GROUND_Y
        self.mode = None

        walk = arcade.load_spritesheet('sprites/Vampires1_Walk_full.png')
        walkGrid=walk.get_texture_grid(size=(64,64), columns=6, count=24)
        self.walk_texture = walkGrid[18:]  # last row (6 frames)

        fly = arcade.load_spritesheet('sprites/Vampires1_Run_full.png')
        flyGrid=fly.get_texture_grid(size=(64,64), columns=6, count=24)
        self.fly_texture = flyGrid[18:]    # last row (6 frames)

        # animation state
        self._frames = []          # active frame list (Textures)
        self._frame_idx = 0
        self._frame_timer = 0.0
        self._frame_dur = 0.11     # seconds per frame (walk default)

        self.set_mode('walk')
        self.vy = 0.0

    def set_mode(self, mode):
        if mode == self.mode:
            return
        self.mode = mode
        if mode == 'walk':
            self._frames = self.walk_texture
            self._frame_dur = 0.11   # 110 ms
        else:  # 'fly'
            self._frames = self.fly_texture
            self._frame_dur = 0.30   # 300 ms (adjust to taste)

        self._frame_idx = 0
        self._frame_timer = 0.0
        self.texture = self._frames[self._frame_idx]

    # Sprite has update_animation hook; we implement it
    def update_animation(self, dt: float = 1/60):
        if not self._frames:
            return
        self._frame_timer += dt
        if self._frame_timer >= self._frame_dur:
            self._frame_timer -= self._frame_dur
            self._frame_idx = (self._frame_idx + 1) % len(self._frames)
            self.texture = self._frames[self._frame_idx]

class Jetpack(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title, update_rate=1/60)
        arcade.set_background_color(arcade.color.BLACK)

        tex = arcade.load_texture(BG_FILE)
        scale = max(self.width / tex.width, self.height / tex.height)
        self.sprite_w = tex.width * scale
        self.bg  = arcade.Sprite(path_or_texture=tex, scale=scale)
        self.bg1 = arcade.Sprite(path_or_texture=tex, scale=scale)
        self.bg.center_x  = self.sprite_w / 2
        self.bg1.center_x = self.sprite_w + self.sprite_w / 2
        self.bg.center_y = self.bg1.center_y = self.height / 2
        self.backgrounds = arcade.SpriteList()
        self.backgrounds.extend([self.bg, self.bg1])

        self.player = player(2.0)
        self.psprite = arcade.SpriteList()
        self.psprite.append(self.player)
        self.acent = False  # track Space

    def on_key_press(self, key, mods):
        if key == arcade.key.SPACE:
            self.acent = True
            self.player.set_mode('fly')

    def on_key_release(self, key, mods):
        if key == arcade.key.SPACE:
            self.acent = False

    def on_update(self, dt: float):
        # Scroll background
        for s in self.backgrounds:
            s.center_x -= 2
        if self.bg.right <= 0:
            self.bg.left = self.bg1.right
        if self.bg1.right <= 0:
            self.bg1.left = self.bg.right
        
        # --- Jetpack physics ---
        self.player.vy += GRAVITY * dt
        if self.acent:
            self.player.vy += THRUST_ACC * dt

        # Clamp velocity
        if self.player.vy > MAX_UP_V:  self.player.vy = MAX_UP_V
        if self.player.vy < MAX_DN_V:  self.player.vy = MAX_DN_V

        # Integrate position
        self.player.center_y += self.player.vy * dt

        # Ceiling
        if self.player.center_y > CEILING_Y:
            self.player.center_y = CEILING_Y
            if self.player.vy > 0: self.player.vy = 0

        # Ground
        if self.player.center_y <= GROUND_Y:
            self.player.center_y = GROUND_Y
            if self.player.vy < 0: self.player.vy = 0
            self.player.set_mode('fly' if self.acent else 'walk')
        else:
            self.player.set_mode('fly')

        self.player.update_animation(dt)

    def on_draw(self):
        self.clear()
        self.backgrounds.draw()
        self.psprite.draw()   # minimal change: draw the SpriteList you created

if __name__ == "__main__":
    Jetpack(WIDTH, HEIGHT, TITLE)
    arcade.run()



















