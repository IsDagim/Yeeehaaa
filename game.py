import arcade, random, time
from arcade.types import XYWH

WIDTH, HEIGHT = 1400, 750
TITLE = "Jetpack + Walkers"
BG_FILE = "images/Noche de Halloween en Laranja.png"

GRAVITY = -1400.0
THRUST_ACC = 2200.0
MAX_UP_V = 800.0
MAX_DN_V = -900.0
GROUND_Y = 150
CEILING_Y = 560

SPEED_MIN, SPEED_MAX = 2, 3
SPAWN_DELAY_MIN, SPAWN_DELAY_MAX = 2.5, 4.5
SCALE_GLOBAL = 0.2
FRAME_RATE = 0.1
MAX_WALKERS = 6
WALKER_Y = GROUND_Y

walk_textures = [
    arcade.load_texture(f"sprites/enemy_running/0_Golem_Running_00{i}.png")
    for i in range(9)
]

class player(arcade.Sprite):
    def __init__(self, scale):
        super().__init__(filename=None, scale=scale)
        self.center_x = 200
        self.center_y = GROUND_Y
        self.mode = None
        walk = arcade.load_spritesheet('sprites/Vampires1_Walk_full.png')
        walkGrid = walk.get_texture_grid(size=(64,64), columns=6, count=24)
        self.walk_texture = walkGrid[18:]
        fly = arcade.load_spritesheet('sprites/Vampires1_Run_full.png')
        flyGrid = fly.get_texture_grid(size=(64,64), columns=6, count=24)
        self.fly_texture = flyGrid[18:]
        self._frames = []
        self._frame_idx = 0
        self._frame_timer = 0.0
        self._frame_dur = 0.11
        self.set_mode('walk')
        self.vy = 0.0

    def set_mode(self, mode):
        if mode == self.mode:
            return
        self.mode = mode
        if mode == 'walk':
            self._frames = self.walk_texture
            self._frame_dur = 0.11
        else:
            self._frames = self.fly_texture
            self._frame_dur = 0.30
        self._frame_idx = 0
        self._frame_timer = 0.0
        self.texture = self._frames[self._frame_idx]

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
        self.bg = arcade.Sprite(path_or_texture=tex, scale=scale)
        self.bg1 = arcade.Sprite(path_or_texture=tex, scale=scale)
        self.bg.center_x = self.sprite_w / 2
        self.bg1.center_x = self.sprite_w + self.sprite_w / 2
        self.bg.center_y = self.bg1.center_y = self.height / 2
        self.backgrounds = arcade.SpriteList()
        self.backgrounds.extend([self.bg, self.bg1])
        self.player = player(2.0)
        self.psprite = arcade.SpriteList()
        self.psprite.append(self.player)
        self.acent = False
        self.walkers = []
        self.last_spawn_time = time.time()
        self.next_gap = random.uniform(SPAWN_DELAY_MIN, SPAWN_DELAY_MAX)
        self.frame_time = 0.0

    def on_key_press(self, key, mods):
        if key == arcade.key.SPACE:
            self.acent = True
            self.player.set_mode('fly')

    def on_key_release(self, key, mods):
        if key == arcade.key.SPACE:
            self.acent = False

    def on_update(self, dt: float):
        for s in self.backgrounds:
            s.center_x -= 2
        if self.bg.right <= 0:
            self.bg.left = self.bg1.right
        if self.bg1.right <= 0:
            self.bg1.left = self.bg.right
        self.player.vy += GRAVITY * dt
        if self.acent:
            self.player.vy += THRUST_ACC * dt
        if self.player.vy > MAX_UP_V:
            self.player.vy = MAX_UP_V
        if self.player.vy < MAX_DN_V:
            self.player.vy = MAX_DN_V
        self.player.center_y += self.player.vy * dt
        if self.player.center_y > CEILING_Y:
            self.player.center_y = CEILING_Y
            if self.player.vy > 0:
                self.player.vy = 0
        if self.player.center_y <= GROUND_Y:
            self.player.center_y = GROUND_Y
            if self.player.vy < 0:
                self.player.vy = 0
            self.player.set_mode('fly' if self.acent else 'walk')
        else:
            self.player.set_mode('fly')
        self.player.update_animation(dt)
        self.frame_time += dt
        if self.frame_time >= FRAME_RATE:
            self.frame_time = 0.0
            for w in self.walkers:
                w[2] = (w[2] + 1) % len(walk_textures)
        for w in self.walkers:
            w[0] += w[3]
        for w in list(self.walkers):
            if w[0] < -100:
                self.walkers.remove(w)
        now = time.time()
        if len(self.walkers) < MAX_WALKERS and now - self.last_spawn_time >= self.next_gap:
            x = WIDTH + 100
            y = WALKER_Y
            speed = -random.uniform(SPEED_MIN, SPEED_MAX)
            self.walkers.append([x, y, random.randrange(len(walk_textures)), speed, now])
            self.last_spawn_time = now
            self.next_gap = random.uniform(SPAWN_DELAY_MIN, SPAWN_DELAY_MAX)

    def on_draw(self):
        self.clear()
        self.backgrounds.draw()
        for x, y, frame, speed, _ in self.walkers:
            tex = walk_textures[frame]
            w, h = int(tex.width * SCALE_GLOBAL), int(tex.height * SCALE_GLOBAL)
            arcade.draw_texture_rect(tex, XYWH(x, y, w, h))
        self.psprite.draw()

if __name__ == "__main__":
    Jetpack(WIDTH, HEIGHT, TITLE)
    arcade.run()
















