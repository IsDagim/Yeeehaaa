import arcade, random, time
from arcade.types import XYWH
from arcade.hitbox import HitBox

WIDTH, HEIGHT = 1400, 800
TITLE = "Vampire joyride"
BG_FILE = "sprites/2_game_background.png"
BAT_SHEET = "sprites/32x32-bat-sprite.png"
COIN_FILE = "sprites/coin.png"

GRAVITY = -1400.0
THRUST_ACC = 2200.0
MAX_UP_V = 800.0
MAX_DN_V = -900.0
GROUND_Y = 100
CEILING_Y = 560

SPEED_MIN, SPEED_MAX = 2, 3
SPAWN_DELAY_MIN, SPAWN_DELAY_MAX = 2.5, 4.5
SCALE_GLOBAL = 0.2
FRAME_RATE = 0.1
MAX_WALKERS = 6
WALKER_Y = GROUND_Y+30

BIG_SPAWN_DELAY_MIN = SPAWN_DELAY_MIN * 2.5
BIG_SPAWN_DELAY_MAX = SPAWN_DELAY_MAX * 2.5
BIG_SCALE = SCALE_GLOBAL * 2.0
MAX_BIG_WALKERS = 3
BIG_SPEED_MIN = SPEED_MIN * 2.0
BIG_SPEED_MAX = SPEED_MAX * 2.2

COIN_MIN_COUNT = 3
COIN_MAX_COUNT = 8
COIN_MIN_Y = 250
COIN_MAX_Y = 600
COIN_SPACING_MIN = 80
COIN_SPACING_MAX = 80
COIN_SCALE = 0.3
COIN_SCROLL_SPEED = 5
COIN_SPAWN_DELAY = 2.5

GAME_OVER_IMG = "sprites/startscreen.png"  
heal_sound = arcade.load_sound("sounds/healing-magic-4-378668.mp3")
arcade.play_sound(heal_sound)

speed_timer=0
walk_textures = [
    arcade.load_texture(f"sprites/enemy_running/0_Golem_Running_{i}.png")
    for i in range(11)
]

walk_textures2 = [
    arcade.load_texture(f"sprites/big_boy/Background-{i}.png")
    for i in range(9)
]


class player(arcade.Sprite):
    def __init__(self, scale):
        super().__init__(filename=None, scale=scale)
        self.mode = None
        walk = arcade.load_spritesheet('sprites/Vampires1_Walk_full.png')
        walkGrid = walk.get_texture_grid(size=(64, 64), columns=6, count=24)
        self.walk_texture = walkGrid[18:]
        fly = arcade.load_spritesheet('sprites/Vampires1_Run_full.png')
        flyGrid = fly.get_texture_grid(size=(64, 64), columns=6, count=24)
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

    def update_animation(self, dt: float = 1 / 60):
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
        super().__init__(filename=None, scale=3.0)
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
        self.vx = -random.uniform(SPEED_MIN + 10, SPEED_MAX + 10)
        self.center_x = WIDTH + 100
        self.center_y = random.randint(GROUND_Y + 80, HEIGHT - 60)

    def update_animation(self, dt: float = 1 / 60):
        self.center_x += self.vx
        self._frame_timer += dt
        if self._frame_timer >= self._frame_dur:
            self._frame_timer -= self._frame_dur
            self._frame_idx = (self._frame_idx + 1) % len(self._frames)
            self.texture = self._frames[self._frame_idx]
            self.hit_box = HitBox(self.texture.hit_box_points)


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

        self.player = player(2.5)
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

        self.big_walkers = []
        self.last_big_spawn_time = time.time()
        self.next_big_gap = random.uniform(BIG_SPAWN_DELAY_MIN, BIG_SPAWN_DELAY_MAX)

        self.coin_tex = arcade.load_texture(COIN_FILE)
        self.coins = arcade.SpriteList()
        self.last_coin_spawn = time.time()
        self.coin_score = 0

        self.start_time = time.time()
        self.time_score = 0
        self.coin_text = arcade.Text(
            f"Coins: {self.coin_score}",
            20,
            HEIGHT - 40,
            arcade.color.YELLOW_ORANGE,
            24,
            bold=True,
        )
        self.score_text = arcade.Text(
            f"Score: {self.time_score}",
            20,
            HEIGHT - 80,
            arcade.color.WHITE,
            24,
            bold=True,
        )

        self.max_health = 100
        self.health = self.max_health
        self.last_decay_time = time.time()
        self.last_walker_hit = 0.0
        self.walker_hit_cooldown = 0.6

        self.can_replenish = False
        self.glow_alpha = 0
        self.coin_sound = arcade.load_sound("sounds/515736__lilmati__retro-coin-06.wav")
        self.pain_sound = arcade.load_sound("sounds/463347__whisperbandnumber1__fight-grunt-2.wav")
        self.gameover_sound = arcade.load_sound("sounds/game-over-417465.mp3")
        self.heal_sound = arcade.load_sound("sounds/healing-magic-4-378668.mp3")
        
        self.state = "playing"
        self.game_over_tex = None
        self.final_score_text = None

    def health_bar(self):
        bar_w, bar_h = 300, 25
        margin = 20
        cy = HEIGHT - 40
        cx_full = WIDTH - margin - bar_w / 2
        ratio = max(0.0, min(1.0, self.health / self.max_health))
        color = arcade.color.APPLE_GREEN if ratio > 0.6 else arcade.color.GOLD if ratio > 0.3 else arcade.color.RED
        arcade.draw_rect_filled(XYWH(cx_full, cy, bar_w, bar_h), arcade.color.DIM_GRAY)
        fill_w = bar_w * ratio
        cx_fill = WIDTH - margin - fill_w / 2
        arcade.draw_rect_filled(XYWH(cx_fill, cy, fill_w, bar_h), color)
        arcade.draw_rect_outline(XYWH(cx_full, cy, bar_w, bar_h), arcade.color.BLACK, 3)

    def draw_replenish_icon(self):
       
        if not self.can_replenish:
            return
       
        self.glow_alpha = (self.glow_alpha + 4) % 510
        alpha = 255 - abs(self.glow_alpha - 255)
        x, y = WIDTH - 170, HEIGHT - 80
        arcade.draw_text(
            "r to replenish",
            x,
            y,
            (255, 255, 255, int(alpha)),
            22,
            bold=True,
            anchor_x="center",
        )

    def game_over(self):
        self.state = "game_over"
        arcade.play_sound(self.gameover_sound) 

        self.game_over_tex = arcade.load_texture(GAME_OVER_IMG)
        self.final_score_text = arcade.Text(
            f"Final Score: {self.time_score}",
            self.width / 2,
            self.height / 2 - 100,
            arcade.color.WHITE,
            36,
            bold=True,
            anchor_x="center",
        )


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
            self.player.set_mode("fly")
        if key == arcade.key.R and self.can_replenish:
            self.health = self.max_health
            self.coin_score -= 7
            arcade.play_sound(self.heal_sound)
            self.can_replenish = False

    def on_key_release(self, key, mods):
        if key == arcade.key.SPACE:
            self.acent = False

    def on_update(self, dt: float):
        if getattr(self, "state", "playing") == "game_over":
            return

        global speed_timer, SPEED_MIN, SPEED_MAX
        for s in self.backgrounds:
            s.center_x -= 5
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
        self.player.vy = max(min(self.player.vy, MAX_UP_V), MAX_DN_V)
        self.player.center_y += self.player.vy * dt
        if self.player.center_y > CEILING_Y:
            self.player.center_y = CEILING_Y
            self.player.vy = 0
        if self.player.center_y <= GROUND_Y:
            self.player.center_y = GROUND_Y
            self.player.vy = 0
            self.player.set_mode("fly" if self.acent else "walk")
        else:
            self.player.set_mode("fly")
        self.player.update_animation(dt)

        now = time.time()
       
        self.frame_time += dt
        if self.frame_time >= FRAME_RATE:
            self.frame_time = 0.0
            for w in self.walkers:
                w[2] = (w[2] + 1) % len(walk_textures)
            for bw in self.big_walkers:
                bw[2] = (bw[2] + 1) % len(walk_textures2)

        for w in self.walkers:
            w[0] += w[3]
        self.walkers = [w for w in self.walkers if w[0] >= -100]
        for bw in self.big_walkers:
            bw[0] += bw[3]
        self.big_walkers = [bw for bw in self.big_walkers if bw[0] >= -200]

        if len(self.walkers) < MAX_WALKERS and now - self.last_spawn_time >= self.next_gap:
            x = WIDTH + 100
            y = WALKER_Y
            speed = -random.uniform(SPEED_MIN, SPEED_MAX)
            self.walkers.append([x, y, random.randrange(len(walk_textures)), speed, now])
            self.last_spawn_time = now
            self.next_gap = random.uniform(SPAWN_DELAY_MIN, SPAWN_DELAY_MAX)

        if len(self.big_walkers) < MAX_BIG_WALKERS and now - self.last_big_spawn_time >= self.next_big_gap:
            x, y = WIDTH + 100, WALKER_Y+45
            speed = -random.uniform(BIG_SPEED_MIN, BIG_SPEED_MAX)
            self.big_walkers.append([x, y, random.randrange(len(walk_textures2)), speed, now])
            self.last_big_spawn_time = now
            self.next_big_gap = random.uniform(BIG_SPAWN_DELAY_MIN, BIG_SPAWN_DELAY_MAX)

        if now - self.last_bat_time >= self.next_bat_gap:
            self.bats.append(Bat(scale=2.0))
            self.last_bat_time = now
            self.next_bat_gap = random.uniform(0.8, 1.6)
        self.bats.update_animation(dt)
        for b in list(self.bats):
            if b.right < -50:
                self.bats.remove(b)


        bat_hits = arcade.check_for_collision_with_list(self.player, self.bats)
        if bat_hits:
            self.health -= self.max_health * 0.20
            arcade.play_sound(self.pain_sound)  
            for b in bat_hits:
                b.remove_from_sprite_lists()
            if self.health <= 0:
                self.game_over()
                return


        for x, y, frame, speed, _ in self.walkers:
            tex = walk_textures[frame]
            s = arcade.Sprite(path_or_texture=tex, scale=SCALE_GLOBAL)
            s.center_x, s.center_y = x, y
            if arcade.check_for_collision(self.player, s):
                if now - self.last_walker_hit >= self.walker_hit_cooldown:
                    self.health -= self.max_health * 0.25
                    self.last_walker_hit = now
                    arcade.play_sound(self.pain_sound)  
                    if self.health <= 0:
                        self.game_over()
                        return
                break


        for x, y, frame, speed, _ in self.big_walkers:
            tex = walk_textures2[frame]
            s = arcade.Sprite(path_or_texture=tex, scale=BIG_SCALE)
            s.center_x, s.center_y = x, y
            if arcade.check_for_collision(self.player, s):
                self.game_over()
                return

        hit_coins = arcade.check_for_collision_with_list(self.player, self.coins)
        for coin in hit_coins:
            coin.remove_from_sprite_lists()
            self.coin_score += 1
            arcade.play_sound(self.coin_sound)


        if now - self.last_decay_time >= 5:
            self.health -= 10
            if self.health <= 0:
                self.game_over()
                return
            self.last_decay_time = now

        if self.coin_score >= 7:
            self.can_replenish = True

        self.time_score = int((time.time() - self.start_time) * 10)
        if self.time_score>speed_timer+100:
            SPEED_MIN+=5
            SPEED_MAX+=5
            speed_timer=self.time_score

    def on_draw(self):
        self.clear()

       
        if getattr(self, "state", "playing") == "game_over":
            if self.game_over_tex:
               
                arcade.draw_texture_rect(
                    self.game_over_tex,
                    XYWH(self.width / 2, self.height / 2, self.width, self.height)
                )
            else:
                arcade.draw_lrtb_rectangle_filled(0, self.width, self.height, 0, arcade.color.BLACK)
                arcade.draw_text(
                    "GAME OVER",
                    self.width / 2,
                    self.height / 2 + 40,
                    arcade.color.WHITE,
                    64,
                    bold=True,
                    anchor_x="center",
                )

            if self.final_score_text:
                self.final_score_text.draw()
            return  

       
        self.backgrounds.draw()
        self.coins.draw()
        self.health_bar()
        self.draw_replenish_icon()
        self.bats.draw()
        self.psprite.draw()

        for x, y, frame, speed, _ in self.walkers:
            tex = walk_textures[frame]
            arcade.draw_texture_rect(tex, XYWH(x, y, tex.width * SCALE_GLOBAL, tex.height * SCALE_GLOBAL))
        for x, y, frame, speed, _ in self.big_walkers:
            tex = walk_textures2[frame]
            arcade.draw_texture_rect(tex, XYWH(x, y, tex.width * BIG_SCALE, tex.height * BIG_SCALE))

        self.coin_text.text = f"Coins: {self.coin_score}"
        self.score_text.text = f"Score: {self.time_score}"
        self.coin_text.draw()
        self.score_text.draw()



if __name__ == "__main__":
    Jetpack(WIDTH, HEIGHT, TITLE)
    arcade.run()



if __name__ == "__main__":
    Jetpack(WIDTH, HEIGHT, TITLE)
    arcade.run()
