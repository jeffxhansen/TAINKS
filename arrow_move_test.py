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

SHRINK_FACTOR = 5

# Frame rate (FPS)
FPS = 60
clock = pygame.time.Clock()

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
        self.rotation_speed = 5  # Degrees per frame
        self.angle = 0  # Tank's initial angle (0 points upward)

        # Update the rect (collision and position) based on the image size
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def draw(self, screen):
        # Rotate the tank's image based on the current angle
        rotated_image = pygame.transform.rotate(self.original_image, -self.angle)
        new_rect = rotated_image.get_rect(center=self.rect.center)
        screen.blit(rotated_image, new_rect.topleft)

    def move(self, keys, forward_key, backward_key, left_key, right_key):
        target_angle = self.angle
        moving = True
        
        plain_movement = True
        
        # Move up, down, left, or right
        if keys[forward_key] and keys[left_key]:
            self.y -= self.speed / math.sqrt(2) if plain_movement else 0
            self.x -= self.speed / math.sqrt(2) if plain_movement else 0
            target_angle = -45  # Switched angle
        elif keys[forward_key] and keys[right_key]:
            self.y -= self.speed / math.sqrt(2) if plain_movement else 0
            self.x += self.speed / math.sqrt(2) if plain_movement else 0
            target_angle = 45  # Switched angle
        elif keys[backward_key] and keys[left_key]:
            self.y += self.speed / math.sqrt(2) if plain_movement else 0
            self.x -= self.speed / math.sqrt(2) if plain_movement else 0
            target_angle = -135  # Switched angle
        elif keys[backward_key] and keys[right_key]:
            self.y += self.speed / math.sqrt(2) if plain_movement else 0
            self.x += self.speed / math.sqrt(2) if plain_movement else 0
            target_angle = 135  # Switched angle
        elif keys[forward_key]:
            self.y -= self.speed if plain_movement else 0
            target_angle = 0
        elif keys[backward_key]:
            self.y += self.speed if plain_movement else 0
            target_angle = 180
        elif keys[left_key]:
            self.x -= self.speed if plain_movement else 0
            target_angle = -90
        elif keys[right_key]:
            self.x += self.speed if plain_movement else 0
            target_angle = 90
        else:
            moving = False
            
        # change the x based on self.speed / cosine of the angle
        # change the y based on self.speed / sine of the angle
        if moving and not plain_movement:
            self.x += self.speed * math.sin(math.radians(self.angle))
            self.y += self.speed * math.cos(math.radians(self.angle))
        
            
        # if self.angle != target_angle and moving:
        #     direction = 1 if target_angle > self.angle else -1
        #     self.angle += direction * self.rotation_speed
        #     if abs(self.angle - target_angle) < self.rotation_speed:
        #         self.angle = target_angle
                
        self.angle = target_angle
        
        # Update tank's rect position
        self.rect = self.image.get_rect(center=(self.x, self.y))

# Main game loop
def game_loop():
    # Create two tank instances using images
    green_tank = Tank(600, 400, 'entities/green_tank.png')  # Image for green tank
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

        # Check for collision and bump back if necessary
        # Shrink the collision rects vertically
        green_tank_collision_rect = green_tank.rect.inflate(0, -green_tank.height // 3)
        red_tank_collision_rect = red_tank.rect.inflate(0, -red_tank.height // 3)

        if green_tank_collision_rect.colliderect(red_tank_collision_rect):
            # Bump green tank back
            if keys[pygame.K_UP]:
                green_tank.y += green_tank.speed
            if keys[pygame.K_DOWN]:
                green_tank.y -= green_tank.speed
            if keys[pygame.K_LEFT]:
                green_tank.x += green_tank.speed
            if keys[pygame.K_RIGHT]:
                green_tank.x -= green_tank.speed

            # Bump red tank back
            if keys[pygame.K_w]:
                red_tank.y += red_tank.speed
            if keys[pygame.K_s]:
                red_tank.y -= red_tank.speed
            if keys[pygame.K_a]:
                red_tank.x += red_tank.speed
            if keys[pygame.K_d]:
                red_tank.x -= red_tank.speed

            # Update rect positions after bumping back
            green_tank.rect = green_tank.image.get_rect(center=(green_tank.x, green_tank.y))
            red_tank.rect = red_tank.image.get_rect(center=(red_tank.x, red_tank.y))

        # Fill the background
        screen.fill(WHITE)

        # Draw tanks
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
