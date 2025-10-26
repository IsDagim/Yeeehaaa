import arcade, random, time
from arcade.types import XYWH

WIDTH, HEIGHT = 1400, 750
TITLE = "Jetpack + Walkers"
BG_FILE = "/Users/abyssiniaatnafe/coding_comp/Yeeehaaa/images/Noche de Halloween en Laranja.png"

walk_textures = [
    arcade.load_texture(f"/Users/abyssiniaatnafe/coding_comp/Yeeehaaa/sprites/enemy_running/0_Golem_Running_00{i}.png")
    for i in range(9)
]

y_aixs = 61
SPEED_MIN, SPEED_MAX = 2, 3
SPAWN_DELAY_MIN, SPAWN_DELAY_MAX = 2.5, 4.5
SCALE_GLOBAL = 0.2
FRAME_RATE = 0.1
MAX_WALKERS = 6

class Jetpack(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title, update_rate=1 / 60)
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
        self.walkers = []
        self.last_spawn_time = time.time()
        self.next_gap = random.uniform(SPAWN_DELAY_MIN, SPAWN_DELAY_MAX)
        self.frame_time = 0.0

    def on_update(self, dt: float):
        for s in self.backgrounds:
            s.center_x -= 2
        if self.bg.right <= 0:
            self.bg.left = self.bg1.right
        if self.bg1.right <= 0:
            self.bg1.left = self.bg.right
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
            y = y_aixs
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

if __name__ == "__main__":
    Jetpack(WIDTH, HEIGHT, TITLE)
    arcade.run()















