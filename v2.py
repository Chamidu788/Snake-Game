import turtle
import random
import math
import colorsys

# Constants
WIDTH = 800
HEIGHT = 600
FOOD_SIZE = 12
SEGMENT_SIZE = 20
GRADIENT_COLORS = [(46, 204, 113), (52, 152, 219), (155, 89, 182), (52, 73, 94)]

class SnakeGame:
    def __init__(self):
        self.score = 0
        self.highest_score = 0
        self.snake = []
        self.food_pos = None
        self.snake_direction = "up"
        self.game_started = False
        self.paused = False
        self.food_hue = 0.0
        
        self.speed_levels = {
            "Slow": 180,
            "Normal": 130,
            "Fast": 80,
            "Ultra": 50
        }
        self.current_speed = "Normal"
        
        self.setup_screen()
        self.create_objects()
        self.setup_events()
        self.reset_game()
        self.add_credits()

    def setup_screen(self):
        self.screen = turtle.Screen()
        self.screen.setup(WIDTH, HEIGHT)
        self.screen.title("Neon Snake")
        self.screen.bgcolor("#1a1a1a")
        self.screen.tracer(0)
        
        self.bg_pattern = turtle.Turtle()
        self.bg_pattern.hideturtle()
        self.bg_pattern.penup()
        self.create_background_pattern()

    def add_credits(self):
        self.credits = turtle.Turtle()
        self.credits.penup()
        self.credits.hideturtle()
        self.credits.color("#666666")
        self.credits.goto(0, -HEIGHT/2 + 10)
        self.credits.write("Created by Chamindu Kavishka", 
                          align="center", 
                          font=("Arial", 10, "italic"))

    def create_background_pattern(self):
        self.bg_pattern.clear()
        self.bg_pattern.penup()
        self.bg_pattern.color("#2c3e50")
        
        for x in range(-WIDTH//2, WIDTH//2, 40):
            for y in range(-HEIGHT//2, HEIGHT//2, 40):
                self.bg_pattern.goto(x, y)
                self.bg_pattern.dot(2)

    def create_objects(self):
        self.pen = turtle.Turtle()
        self.pen.penup()
        self.pen.shape("square")
        self.pen.hideturtle()
        
        self.food = turtle.Turtle()
        self.food.shape("circle")
        self.food.shapesize(FOOD_SIZE/20)
        self.food.penup()
        self.food.hideturtle()
        
        self.food_glow = turtle.Turtle()
        self.food_glow.shape("circle")
        self.food_glow.penup()
        self.food_glow.hideturtle()
        
        self.score_display = turtle.Turtle()
        self.score_display.color("#ecf0f1")
        self.score_display.penup()
        self.score_display.hideturtle()
        self.score_display.goto(0, HEIGHT/2 - 40)
        
        self.message_display = turtle.Turtle()
        self.message_display.color("#ecf0f1")
        self.message_display.penup()
        self.message_display.hideturtle()
        
        self.instructions = turtle.Turtle()
        self.instructions.color("#bdc3c7")
        self.instructions.penup()
        self.instructions.hideturtle()
        self.instructions.goto(0, -HEIGHT/2 + 30)

    def update_food_color(self):
        self.food_hue += 0.01
        if self.food_hue > 1.0:
            self.food_hue = 0.0
            
        rgb = colorsys.hsv_to_rgb(self.food_hue, 1.0, 1.0)
        color = f"#{int(rgb[0]*255):02x}{int(rgb[1]*255):02x}{int(rgb[2]*255):02x}"
        
        # Update main food color
        self.food.color(color)
        
        # Create glow effect with larger circles
        self.food_glow.clear()
        self.food_glow.goto(self.food_pos)
        
        # Create multiple circles with decreasing intensity
        for i in range(3):
            size = FOOD_SIZE * (1.5 - i * 0.2)
            rgb_glow = colorsys.hsv_to_rgb(self.food_hue, 0.3, 0.5)  # Less saturated and darker
            glow_color = f"#{int(rgb_glow[0]*255):02x}{int(rgb_glow[1]*255):02x}{int(rgb_glow[2]*255):02x}"
            self.food_glow.color(glow_color)
            self.food_glow.shapesize(size/20)
            self.food_glow.stamp()

    def interpolate_color(self, color1, color2, fraction):
        return tuple(int(c1 + (c2 - c1) * fraction) for c1, c2 in zip(color1, color2))

    def get_segment_color(self, index, total_segments):
        gradient_position = index / total_segments
        color_index = int(gradient_position * (len(GRADIENT_COLORS) - 1))
        next_color_index = min(color_index + 1, len(GRADIENT_COLORS) - 1)
        
        fraction = gradient_position * (len(GRADIENT_COLORS) - 1) - color_index
        color = self.interpolate_color(GRADIENT_COLORS[color_index], GRADIENT_COLORS[next_color_index], fraction)
        return f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"

    def draw_snake(self):
        self.pen.clearstamps()
        
        for i, segment in enumerate(self.snake):
            self.pen.goto(segment[0], segment[1])
            self.pen.color(self.get_segment_color(i, len(self.snake)))
            
            for size in [1.1, 1.0]:
                self.pen.shapesize(size, size)
                self.pen.stamp()

    def move_snake(self):
        if self.paused or not self.game_started:
            turtle.ontimer(self.move_snake, self.speed_levels[self.current_speed])
            return

        self.update_food_color()

        new_head = self.snake[-1].copy()
        new_head[0] += {
            "up": (0, SEGMENT_SIZE),
            "down": (0, -SEGMENT_SIZE),
            "left": (-SEGMENT_SIZE, 0),
            "right": (SEGMENT_SIZE, 0)
        }[self.snake_direction][0]
        new_head[1] += {
            "up": (0, SEGMENT_SIZE),
            "down": (0, -SEGMENT_SIZE),
            "left": (-SEGMENT_SIZE, 0),
            "right": (SEGMENT_SIZE, 0)
        }[self.snake_direction][1]

        if (new_head in self.snake or 
            new_head[0] < -WIDTH/2 or new_head[0] > WIDTH/2 or 
            new_head[1] < -HEIGHT/2 or new_head[1] > HEIGHT/2):
            self.game_over()
            return

        self.snake.append(new_head)
        
        if self.get_distance(new_head, self.food_pos) < SEGMENT_SIZE:
            self.score += 10
            self.food_pos = self.get_random_food_pos()
            self.food.goto(self.food_pos)
            self.update_score()
            self.spawn_food_effect()
        else:
            self.snake.pop(0)

        self.draw_snake()
        self.screen.update()
        turtle.ontimer(self.move_snake, self.speed_levels[self.current_speed])

    def spawn_food_effect(self):
        effect = turtle.Turtle()
        effect.penup()
        effect.hideturtle()
        effect.goto(self.food_pos)
        
        def pulse(size, intensity):
            if size > 30:
                effect.clear()
                effect.reset()
                return
            
            effect.clear()
            rgb = colorsys.hsv_to_rgb(self.food_hue, intensity, 1.0)
            color = f"#{int(rgb[0]*255):02x}{int(rgb[1]*255):02x}{int(rgb[2]*255):02x}"
            effect.color(color)
            effect.dot(size)
            self.screen.update()
            turtle.ontimer(lambda: pulse(size + 2, intensity * 0.9), 50)
        
        pulse(FOOD_SIZE, 1.0)

    def get_random_food_pos(self):
        while True:
            x = random.randint(-WIDTH//2 + SEGMENT_SIZE, WIDTH//2 - SEGMENT_SIZE)
            x = x - (x % SEGMENT_SIZE)
            y = random.randint(-HEIGHT//2 + SEGMENT_SIZE, HEIGHT//2 - SEGMENT_SIZE)
            y = y - (y % SEGMENT_SIZE)
            if [x, y] not in self.snake:
                return (x, y)

    def get_distance(self, pos1, pos2):
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

    def update_score(self):
        self.score_display.clear()
        self.score_display.write(
            f"Score: {self.score}  |  High Score: {self.highest_score}  |  Speed: {self.current_speed}", 
            align="center", 
            font=("Arial", 16, "bold")
        )

    def show_message(self, message, y_pos=0, color="#ecf0f1", size=24):
        self.message_display.clear()
        self.message_display.color(color)
        self.message_display.goto(0, y_pos)
        self.message_display.write(message, align="center", font=("Arial", size, "bold"))

    def show_instructions(self):
        self.instructions.clear()
        self.instructions.write(
            "Arrow Keys: Move  |  P: Pause  |  Speed (1-4): Slow/Normal/Fast/Ultra  |  Press SPACE to Start", 
            align="center", 
            font=("Arial", 12)
        )

    def game_over(self):
        if self.score > self.highest_score:
            self.highest_score = self.score
        self.show_message("GAME OVER!", color="#e74c3c")
        self.game_started = False
        turtle.ontimer(self.reset_game, 2000)

    def reset_game(self):
        self.snake = [[0, 0], [0, SEGMENT_SIZE], [0, SEGMENT_SIZE * 2]]
        self.snake_direction = "up"
        self.score = 0
        self.food_pos = self.get_random_food_pos()
        self.food.goto(self.food_pos)
        self.food.showturtle()
        self.update_score()
        self.show_instructions()
        if not self.game_started:
            self.show_message("Press SPACE to Start!", y_pos=50, size=20, color="#2ecc71")
        self.screen.update()

    def start_game(self):
        if not self.game_started:
            self.game_started = True
            self.message_display.clear()
            self.move_snake()

    def toggle_pause(self):
        if self.game_started:
            self.paused = not self.paused
            if self.paused:
                self.show_message("PAUSED", y_pos=50, size=20, color="#f1c40f")
            else:
                self.message_display.clear()

    def set_speed(self, speed):
        self.current_speed = speed
        self.update_score()

    def setup_events(self):
        self.screen.listen()
        self.screen.onkey(lambda: self.set_direction("up"), "Up")
        self.screen.onkey(lambda: self.set_direction("down"), "Down")
        self.screen.onkey(lambda: self.set_direction("left"), "Left")
        self.screen.onkey(lambda: self.set_direction("right"), "Right")
        self.screen.onkey(self.start_game, "space")
        self.screen.onkey(self.toggle_pause, "p")
        self.screen.onkey(lambda: self.set_speed("Slow"), "1")
        self.screen.onkey(lambda: self.set_speed("Normal"), "2")
        self.screen.onkey(lambda: self.set_speed("Fast"), "3")
        self.screen.onkey(lambda: self.set_speed("Ultra"), "4")

    def set_direction(self, direction):
        if self.game_started and not self.paused:
            opposites = {"up": "down", "down": "up", "left": "right", "right": "left"}
            if self.snake_direction != opposites[direction]:
                self.snake_direction = direction

def main():
    game = SnakeGame()
    turtle.done()

if __name__ == "__main__":
    main()