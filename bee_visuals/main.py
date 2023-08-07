import pygame
import random
import math

# Define constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
BEE_SIZE = 20
BEE_COUNT = 50
BEE_SPEED = 2

# Define colors
WHITE = (255, 255, 255)

# Tree class
class Tree(pygame.sprite.Sprite):
    def __init__(self, x, y, color, quality):
        super().__init__()
        self.image = pygame.Surface((BEE_SIZE * 2, BEE_SIZE * 2))
        self.image.fill(color)  # Use the provided color for the tree
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.color = color  # Store the tree's color
        self.quality = quality

# Bee class
class Bee(pygame.sprite.Sprite):
    def __init__(self, id):
        super().__init__()
        self.id=id
        self.image = pygame.Surface((BEE_SIZE, BEE_SIZE))
        self.image.fill(WHITE)  # Replace this with your bee image
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(100, SCREEN_WIDTH-100), random.randint(100, SCREEN_HEIGHT-100))
        self.angle = random.uniform(0, 2 * math.pi)  # Initial movement angle
        self.speed = BEE_SPEED
        self.at_tree = False
        self.prev_tree_color = None
        self.tree_color = None  # To store the color of the tree the bee is interacting with
        self.tree_quality = None  # To store the quality score of the tree the bee is interacting with
        self.advertising_state = 0  # Counter to track the advertising state
        self.state = "FORAGING"

    def update(self):
        if self.state == "FORAGING":
        # if not self.at_tree:
            self.random_walk()
            # if self.prev_tree_color != self.tree_color:
            #     self.draw_border(self.tree_color)

        elif self.state == "RETURNING":
            # Move back to the center
            dx = (SCREEN_WIDTH // 2) - self.rect.centerx
            dy = (SCREEN_HEIGHT // 2) - self.rect.centery
            distance = math.hypot(dx, dy)
            if distance > 0:
                dx = (dx / distance) * self.speed
                dy = (dy / distance) * self.speed
            self.rect.move_ip(dx, dy)

            # If bee is back at the center, reset its color and state
            if distance < 5:
                self.at_tree = False
                # self.image.fill(WHITE)
                self.advertising_state = self.tree_quality  # Set advertising state based on the tree quality
                self.state = "ADVERTISING"

        elif self.state == "ADVERTISING":
            self.random_walk()

            if self.advertising_state <= 0:
                self.state = "FORAGING"
                self.draw_border(self.tree_color)
                # print(f"Bee {self.id} finished Advertising, returning to forage")
            else:
                self.advertising_state -= 1
                self.draw_border()

        self.prev_tree_color = self.tree_color

    def interact_with_tree(self, tree_color, tree_quality):
        self.state = "RETURNING"
        self.at_tree = True
        self.tree_color = tree_color
        self.tree_quality = tree_quality
        self.image.fill(tree_color)  # Change bee color to tree color

    def interact_with_other_bee(self, other_bee):
        # Opinion exchange behavior during advertising state
        if self.state == "ADVERTISING":
            if other_bee.state == "FORAGING":
                # print(f"Bee {self.id} interacting with Bee {other_bee.id}, setting to colour {self.tree_color}")
                other_bee.image.fill(self.tree_color)
                # other_bee.draw_border(border_color=(100, 30, 199))

    def draw_border(self, border_color=(255,255,0), thickness=3):
        # Draw colored border around the bee sprite during advertising state
        pygame.draw.rect(self.image, border_color, self.image.get_rect(), thickness)

    def random_walk(self):
        self.angle += random.uniform(-math.pi / 4, math.pi / 4)  # Change the angle slightly
        self.angle %= 2 * math.pi  # Wrap the angle within 0 to 2*pi

        dx = self.speed * math.cos(self.angle)
        dy = self.speed * math.sin(self.angle)

        self.rect.move_ip(dx, dy)
        # Keep the bee inside the screen bounds
        self.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

# Beehive class
class Beehive(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()  # Call the parent class constructor
        self.image = pygame.Surface((BEE_SIZE * 2, BEE_SIZE * 2))
        self.image.fill((255, 0, 0))  # Replace this with your beehive image
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Bee Colony Simulation")

    all_sprites = pygame.sprite.Group()
    bees = pygame.sprite.Group()
    trees = pygame.sprite.Group()

    beehive = Beehive()
    all_sprites.add(beehive)

    # Add trees at the corners of the screen
    tree1 = Tree(50, 50, (0, 255, 0), 50)  # Green
    tree2 = Tree(SCREEN_WIDTH - 50, 50, (255, 100, 40), 20)  # Red
    tree3 = Tree(50, SCREEN_HEIGHT - 50, (125, 125, 250), 100)  # Blue
    tree4 = Tree(SCREEN_WIDTH - 50, SCREEN_HEIGHT - 50, (128, 109, 0), 50)  # Yellow

    all_sprites.add(tree1, tree2, tree3, tree4)
    trees.add(tree1, tree2, tree3, tree4)

    for i in range(BEE_COUNT):
        bee = Bee(i)
        all_sprites.add(bee)
        bees.add(bee)

    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Check for collisions between bees and trees
        for bee in bees:
            collisions = pygame.sprite.spritecollide(bee, trees, False)
            if collisions:
                tree_color = collisions[0].color  # Get the color of the tree the bee interacts with
                tree_quality = collisions[0].quality  # Get the quality of the tree the bee interacts with
                bee.interact_with_tree(tree_color, tree_quality)

        # Check for collisions between bees
        for bee in bees:
            collisions = pygame.sprite.spritecollide(bee, bees, False)
            for other_bee in collisions:
                if other_bee != bee:
                    bee.interact_with_other_bee(other_bee)

        # Update
        all_sprites.update()

        # Draw
        screen.fill((0, 0, 0))
        all_sprites.draw(screen)
        pygame.display.flip()

        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
