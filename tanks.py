import pygame
import random
import sys
import math
import time

# Initialize Pygame
pygame.init()

# Set up the game window
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Two-Player Tank Game")

# Define colors (for background, etc.)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

SHRINK_FACTOR = 5

PROJ_REFRESH_SEC = 0.2

EXPLOSION_STOP = 40
EXPLOSION_INCREMENT = 7

# Frame rate (FPS)
FPS = 60
clock = pygame.time.Clock()

class Projectile:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 7
        self.radius = 7
        
        self.is_exploding = False
        self.exploding_frames = 0

    def update(self):
        
        if not self.is_exploding:
            angle_rad = (abs(self.angle) + 90) * math.pi / 180
            self.x += self.speed * math.cos(angle_rad)
            self.y -= self.speed * math.sin(angle_rad)
        else:
            self.radius += EXPLOSION_INCREMENT
            if self.radius >= EXPLOSION_STOP:
                self.radius = 0
                self.is_exploding = False

    def draw(self, screen):
        if not self.is_exploding:
            # Calculate the points of the triangle
            angle_rad = (abs(self.angle) + 90) * math.pi / 180
            len_factor = 2.5
            point1 = (self.x + self.radius * len_factor * math.cos(angle_rad), self.y - self.radius * len_factor * math.sin(angle_rad))  # Make the projectile longer
            point2 = (self.x + self.radius * math.cos(angle_rad + 2 * math.pi / 3), self.y - self.radius * math.sin(angle_rad + 2 * math.pi / 3))
            point3 = (self.x + self.radius * math.cos(angle_rad - 2 * math.pi / 3), self.y - self.radius * math.sin(angle_rad - 2 * math.pi / 3))
            
            # Draw the triangle
            pygame.draw.polygon(screen, BLACK, [point1, point2, point3])
        else:
            pygame.draw.circle(screen, (255, 165, 0), (int(self.x), int(self.y)), self.radius)
        
    def explode(self):
        self.is_exploding = True
        self.radius = 10
        
    

class Tank:
    def __init__(self, x, y, image_path, is_ai=False):
        # Load the tank image
        self.original_image = pygame.image.load(image_path).convert_alpha()  # Load the image with transparency
        self.original_image = pygame.transform.scale(self.original_image, (self.original_image.get_width() // SHRINK_FACTOR, self.original_image.get_height() // SHRINK_FACTOR))  # Scale down the image
        self.width, self.height = self.original_image.get_size()
        self.image = self.original_image
        self.x = x
        self.y = y
        self.speed = 3  # Movement speed
        self.rotation_speed = 7  # Degrees per frame
        self.angle = 0  # Tank's initial angle (0 points upward)
        self.projectiles = []
        self.last_shot_time = 0  # Track the last time a projectile was shot
        
        self.score = 0
        
        self._is_ai = is_ai

        # Update the rect (collision and position) based on the image size
        self.rect = self.image.get_rect(center=(self.x, self.y))
        
    def is_ai(self):
        return self._is_ai

    def draw(self, screen):
        # Rotate the tank's image based on the current angle
        rotated_image = pygame.transform.rotate(self.original_image, -self.angle)
        new_rect = rotated_image.get_rect(center=self.rect.center)
        screen.blit(rotated_image, new_rect.topleft)
        for projectile in self.projectiles:
            projectile.draw(screen)
            
    def add_point(self):
        self.score += 1
        
    def deg_to_rad(self, deg):
        rads = (abs(deg) + 90) * math.pi / 180
        if rads > 2*math.pi:
            rads -= 2*math.pi
        return rads
    
    def rad_to_deg(self, rad):
        degs = rad * 180 / math.pi - 90
        degs = -abs((degs % 360))
        return degs
    
    def move_towards(self, x, y):
        pass
    
    def shoot_towards(self, x, y):
        pass
    
    def move_ai(self, projectiles, tank_locations):
        pass

    def move(self, keys, forward_key, backward_key, left_key, right_key):
        target_angle = self.angle
        moving = True
        
        plain_movement = False
        
        # Move up, down, left, or right
        if keys[forward_key] and keys[left_key]:
            self.y -= self.speed / math.sqrt(2) if plain_movement else 0
            self.x -= self.speed / math.sqrt(2) if plain_movement else 0
            target_angle = -45  # Switched angle
        elif keys[forward_key] and keys[right_key]:
            self.y -= self.speed / math.sqrt(2) if plain_movement else 0
            self.x += self.speed / math.sqrt(2) if plain_movement else 0
            target_angle = 45-360  # Switched angle
        elif keys[backward_key] and keys[left_key]:
            self.y += self.speed / math.sqrt(2) if plain_movement else 0
            self.x -= self.speed / math.sqrt(2) if plain_movement else 0
            target_angle = -135  # Switched angle
        elif keys[backward_key] and keys[right_key]:
            self.y += self.speed / math.sqrt(2) if plain_movement else 0
            self.x += self.speed / math.sqrt(2) if plain_movement else 0
            target_angle = -180-45  # Switched angle
        elif keys[forward_key]:
            self.y -= self.speed if plain_movement else 0
            target_angle = 0
        elif keys[backward_key]:
            self.y += self.speed if plain_movement else 0
            target_angle = -180
        elif keys[left_key]:
            self.x -= self.speed if plain_movement else 0
            target_angle = -90
        elif keys[right_key]:
            self.x += self.speed if plain_movement else 0
            target_angle = -270
        else:
            moving = False
        
        if abs(self.angle - target_angle) > self.rotation_speed and moving:
            
            to_angle, from_angle = target_angle, self.angle
            clockwise_dist = min(
                (to_angle - from_angle) % 360,
                ((to_angle-360) - from_angle) % 360
            )
            counter_clockwise_dist = min(
                (from_angle - to_angle) % 360,
                (from_angle - (to_angle-360)) % 360
            )
            if clockwise_dist < counter_clockwise_dist:
                direction = 1
            else:
                direction = -1
            
            self.angle += (direction * self.rotation_speed % 360)
            if abs(self.angle - target_angle) <= self.rotation_speed:
                self.angle = target_angle
            if self.angle > 0:
                self.angle -= 360
        else:
            self.angle = int(target_angle)
            
        # change the x based on self.speed / cosine of the angle
        # change the y based on self.speed / sine of the angle
        if moving and not plain_movement:
            angle_rad = (abs(self.angle) + 90) * math.pi / 180
            self.x += self.speed * math.cos(angle_rad)
            self.y -= self.speed * math.sin(angle_rad)
        
        # Update tank's rect position
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def shoot(self):
        current_time = time.time()
        if len(self.projectiles) < 5 and (current_time - self.last_shot_time) >= PROJ_REFRESH_SEC:
            self.projectiles.append(Projectile(self.x, self.y, self.angle))
            self.last_shot_time = current_time
            
    def angle_from_loc(self, x, y):
        cx = self.x
        cy = self.y
        dx = x - cx
        dy = cy - y
        theta = math.atan2(dy, dx)
        return theta
            
    def shoot_angle(self, angle_rad):
        current_time = time.time()
        angle = self.rad_to_deg(angle_rad)
        if len(self.projectiles) < 5 and (current_time - self.last_shot_time) >= PROJ_REFRESH_SEC:
            self.projectiles.append(Projectile(self.x, self.y, angle))
            self.last_shot_time = current_time

    def update_projectiles(self):
        for projectile in self.projectiles:
            projectile.update()
        self.projectiles = [p for p in self.projectiles if 0 <= p.x <= WIDTH and 0 <= p.y <= HEIGHT]

# Main game loop
def game_loop():
    # Create two tank instances using images
    green_tank = Tank(400, 400, 'entities/green_tank.png')  # Image for green tank
    red_tank = Tank(100, 100, 'entities/red_tank.png')  # Image for red tank

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Get the state of all keys
        keys = pygame.key.get_pressed()

        # Move green tank (controlled by arrow keys)
        green_tank.move(keys, pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT)

        # Move red tank (controlled by WASD)
        red_tank.move(keys, pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d)
        
        # get the x, y location of where the mouse is clicked
        #if pygame.mouse.get_pressed()[0]:
        # if the space bard is pressed
        if keys[pygame.K_SPACE] or pygame.mouse.get_pressed()[0]:
            x, y = pygame.mouse.get_pos()
            angle_rad = green_tank.angle_from_loc(x, y)
            green_tank.shoot_angle(angle_rad)

        # Update projectiles
        green_tank.update_projectiles()
        red_tank.update_projectiles()
        
        # Check for collisions between projectiles and tanks
        for projectile in green_tank.projectiles:
            if red_tank.rect.collidepoint(projectile.x, projectile.y):
                green_tank.add_point()
                
                projectile.explode()
                
                # set red_tank to a random location
                x, y = random.randint(0, WIDTH), random.randint(0, HEIGHT)
                red_tank.x, red_tank.y = x, y

        for projectile in red_tank.projectiles:
            if green_tank.rect.collidepoint(projectile.x, projectile.y):
                red_tank.add_point()
                
                projectile.explode()
                
                x, y = random.randint(0, WIDTH), random.randint(0, HEIGHT)
                green_tank.x, green_tank.y = x, y

        # Fill the background
        #screen.fill((240, 223, 177))  # light-brownish-yellow
        screen.fill(WHITE)

        # Draw tanks and projectiles
        green_tank.draw(screen)
        red_tank.draw(screen)
        
        # Display scores
        font = pygame.font.Font(None, 36)
        green_score_text = font.render(f"Green Tank: {green_tank.score}", True, (0, 255, 0))
        red_score_text = font.render(f"Red Tank: {red_tank.score}", True, (255, 0, 0))

        screen.blit(green_score_text, (10, 10))
        screen.blit(red_score_text, (WIDTH - red_score_text.get_width() - 10, 10))

        # Update the display
        pygame.display.flip()

        # Set the frame rate
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    game_loop()
