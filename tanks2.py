import pygame
import sys
import math

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

# Frame rate (FPS)
FPS = 60
clock = pygame.time.Clock()

class Projectile:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 10
        self.radius = 5

    def update(self):
        angle_rad = (abs(self.angle) + 90) * math.pi / 180
        self.x += self.speed * math.cos(angle_rad)
        self.y -= self.speed * math.sin(angle_rad)

    def draw(self, screen):
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.radius)

class Tank:
    def __init__(self, x, y, image_path):
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

        # Update the rect (collision and position) based on the image size
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def draw(self, screen):
        # Rotate the tank's image based on the current angle
        rotated_image = pygame.transform.rotate(self.original_image, -self.angle)
        new_rect = rotated_image.get_rect(center=self.rect.center)
        screen.blit(rotated_image, new_rect.topleft)
        for projectile in self.projectiles:
            projectile.draw(screen)
        
    def deg_to_rad(self, deg):
        rads = (abs(deg) + 90) * math.pi / 180
        if rads > 2*math.pi:
            rads -= 2*math.pi
        return rads

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
        if len(self.projectiles) < 5:
            self.projectiles.append(Projectile(self.x, self.y, self.angle))

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

        # Shoot projectiles
        if keys[pygame.K_SPACE]:
            green_tank.shoot()
        if keys[pygame.K_z]:
            red_tank.shoot()

        # Update projectiles
        green_tank.update_projectiles()
        red_tank.update_projectiles()

        # Fill the background
        screen.fill(WHITE)

        # Draw tanks and projectiles
        green_tank.draw(screen)
        red_tank.draw(screen)

        # Update the display
        pygame.display.flip()

        # Set the frame rate
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    game_loop()