import arcade, random, time
from arcade.types import XYWH
from arcade.hitbox import HitBox

WIDTH, HEIGHT = 1400, 750
TITLE = "IDK"
BG_FILE = "images/Noche de Halloween en Laranja.png"
BAT_SHEET = "sprites/32x32-bat-sprite.png"
COIN_FILE = "sprites/pumpkin.png"

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


COIN_MIN_COUNT = 3
COIN_MAX_COUNT = 8
COIN_MIN_Y = 250
COIN_MAX_Y = 600
COIN_SPACING_MIN = 80
COIN_SPACING_MAX = 80
COIN_SCALE = 0.3
COIN_SCROLL_SPEED = 2
COIN_SPAWN_DELAY = 2.5

walk_textures = [
    arcade.load_texture(f"sprites/enemy_running/0_Golem_Running_00{i}.png")
    for i in range(9)
]

class player(arcade.Sprite):
    def __init__(self, scale):
        super().__init__(filename=None, scale=scale)
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
        self.center_x = 200
        self.center_y = GROUND_Y
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
        self.hit_box = HitBox(self.texture.hit_box_points)

    def update_animation(self, dt: float = 1/60):
        if not self._frames:
            return
        self._frame_timer += dt
        if self._frame_timer >= self._frame_dur:
            self._frame_timer -= self._frame_dur
            self._frame_idx = (self._frame_idx + 1) % len(self._frames)
            self.texture = self._frames[self._frame_idx]
            self.hit_box = HitBox(self.texture.hit_box_points)

class Bat(arcade.Sprite):
    def __init__(self, scale):
        super().__init__(filename=None, scale=scale)
        sheet = arcade.load_spritesheet(BAT_SHEET)
        w, h = sheet.image.size
        fw, fh = w // 4, h // 4
        grid = sheet.get_texture_grid(size=(fw, fh), columns=4, count=16)
        self._frames = grid[12:16]
        self.texture = self._frames[0]
        self.hit_box = HitBox(self.texture.hit_box_points)
        self._frame_idx = 0
        self._frame_timer = 0.0
        self._frame_dur = 0.08
        self.vx = -random.uniform(SPEED_MIN+10, SPEED_MAX+10)
        self.center_x = WIDTH + 100
        self.center_y = random.randint(GROUND_Y + 80, HEIGHT - 60)

    def update_animation(self, dt: float = 1/60):
        self.center_x += self.vx
        self._frame_timer += dt
        if self._frame_timer >= self._frame_dur:
            self._frame_timer -= self._frame_dur
            self._frame_idx = (self._frame_idx + 1) % len(self._frames)
            self.texture = self._frames[self._frame_idx]
            self.hit_box = HitBox(self.texture.hit_box_points)

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

    
        self.bats = arcade.SpriteList()
        self.last_bat_time = time.time()
        self.next_bat_gap = random.uniform(0.8, 1.6)

        
        self.coin_tex = arcade.load_texture(COIN_FILE)
        self.coins = arcade.SpriteList()
        self.last_coin_spawn = time.time()
        self.coin_score = 0  

    def game_over(self):
        self.close()

    def spawn_coin_batch(self):
        self.coins = arcade.SpriteList()
        num_coins = random.randint(COIN_MIN_COUNT, COIN_MAX_COUNT)
        y = random.randint(COIN_MIN_Y, COIN_MAX_Y)
        start_x = WIDTH + 100
        spacing = random.randint(COIN_SPACING_MIN, COIN_SPACING_MAX)
        for i in range(num_coins):
            coin = arcade.Sprite(path_or_texture=self.coin_tex, scale=COIN_SCALE)
            coin.center_x = start_x + i * spacing
            coin.center_y = y
            self.coins.append(coin)
        self.last_coin_spawn = time.time()

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

       
        for coin in self.coins:
            coin.center_x -= COIN_SCROLL_SPEED
        if len(self.coins) == 0 or self.coins[-1].center_x < -100:
            if time.time() - self.last_coin_spawn > COIN_SPAWN_DELAY:
                self.spawn_coin_batch()

        
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

    
        if now - self.last_bat_time >= self.next_bat_gap:
            self.bats.append(Bat(scale=2.0))
            self.last_bat_time = now
            self.next_bat_gap = random.uniform(0.8, 1.6)
        self.bats.update_animation(dt)
        for b in list(self.bats):
            if b.right < -50:
                self.bats.remove(b)

    
        if arcade.check_for_collision_with_list(self.player, self.bats):
            self.game_over()
            return
        for x, y, frame, speed, _ in self.walkers:
            tex = walk_textures[frame]
            s = arcade.Sprite(path_or_texture=tex, scale=SCALE_GLOBAL)
            s.center_x, s.center_y = x, y
            if arcade.check_for_collision(self.player, s):
                self.game_over()
                return


        hit_coins = arcade.check_for_collision_with_list(self.player, self.coins)
        for coin in hit_coins:
            coin.remove_from_sprite_lists()
            self.coin_score += 1  

    def on_draw(self):
        self.clear()
        self.backgrounds.draw()
        self.coins.draw()
        for x, y, frame, speed, _ in self.walkers:
            tex = walk_textures[frame]
            w, h = int(tex.width * SCALE_GLOBAL), int(tex.height * SCALE_GLOBAL)
            arcade.draw_texture_rect(tex, XYWH(x, y, w, h))
        self.bats.draw()
        self.psprite.draw()

       
        arcade.draw_text(
            f"Coins: {self.coin_score}",
            20, HEIGHT - 40,
            arcade.color.YELLOW_ORANGE,
            24,
            bold=True
        )

if __name__ == "__main__":
    Jetpack(WIDTH, HEIGHT, TITLE)
    arcade.run()