import arcade


WIDTH, HEIGHT = 1400, 750
TITLE = "IDk"
BG_FILE = "images/Noche de Halloween en Laranja.png"

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

    def on_update(self, dt: float):
        for s in self.backgrounds:
            s.center_x -= 2
        if self.bg.right <= 0:
            self.bg.left = self.bg1.right
        if self.bg1.right <= 0:
            self.bg1.left = self.bg.right

    def on_draw(self):
        self.clear()
        self.backgrounds.draw()

if __name__ == "__main__":
    Jetpack(WIDTH, HEIGHT, TITLE)
    arcade.run()


        




















