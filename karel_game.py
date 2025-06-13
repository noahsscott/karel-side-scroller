"""
Karel's Code Quest - A Side-Scrolling Platformer Game
Stanford CIP Final Project

This is a single-file pygame implementation designed to run in the CIP browser environment.
Karel, the beloved Stanford CS robot, embarks on a coding adventure through various levels.
"""

import pygame
import sys

# Game Constants
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480
FPS = 60
GAME_TITLE = "Karel's Code Quest"

# Karel Constants
KAREL_SIZE = 32
KAREL_SPEED = 5
KAREL_START_X = 50
KAREL_START_Y = WINDOW_HEIGHT - 100

# Physics Constants
GRAVITY = 0.8
JUMP_VELOCITY = -15
TERMINAL_VELOCITY = 12
GROUND_HEIGHT = 50
GROUND_LEVEL = WINDOW_HEIGHT - GROUND_HEIGHT

# Color Palette (simple scheme for CIP compatibility)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
KAREL_BLUE = (0, 100, 200)  # Karel's signature color
GROUND_GREEN = (0, 150, 0)  # Ground color

class Platform:
    """
    Platform class representing solid surfaces Karel can land on.
    """
    
    def __init__(self, x, y, width, height):
        """Initialize platform with position and dimensions."""
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
    
    def draw(self, screen):
        """Draw the platform as a green rectangle."""
        pygame.draw.rect(screen, GROUND_GREEN, self.rect)

class Karel:
    """
    Karel character class representing the player.
    A blue 32x32 rectangle with a centered white 'K' label.
    """
    
    def __init__(self, x, y):
        """Initialize Karel at the given position."""
        self.x = x
        self.y = y
        self.width = KAREL_SIZE
        self.height = KAREL_SIZE
        self.speed = KAREL_SPEED
        
        # Physics variables
        self.velocity_y = 0
        self.on_ground = False
        
        # Create rectangle for collision detection
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
    
    def move_left(self):
        """Move Karel left while respecting screen boundaries."""
        self.x -= self.speed
        # Boundary check - don't go past left edge
        if self.x < 0:
            self.x = 0
        self.rect.x = self.x
    
    def move_right(self):
        """Move Karel right while respecting screen boundaries."""
        self.x += self.speed
        # Boundary check - don't go past right edge
        if self.x > WINDOW_WIDTH - self.width:
            self.x = WINDOW_WIDTH - self.width
        self.rect.x = self.x
    
    def jump(self):
        """Make Karel jump if on ground."""
        if self.on_ground:
            self.velocity_y = JUMP_VELOCITY
            self.on_ground = False
    
    def apply_gravity(self):
        """Apply gravity physics to Karel."""
        if not self.on_ground:
            # Apply gravity
            self.velocity_y += GRAVITY
            
            # Limit to terminal velocity
            if self.velocity_y > TERMINAL_VELOCITY:
                self.velocity_y = TERMINAL_VELOCITY
    
    def check_platform_collision(self, platforms):
        """Check if Karel is colliding with any platform."""
        karel_bottom = self.y + self.height
        karel_top = self.y
        self.on_ground = False
        
        # Check collision with all platforms (including ground)
        for platform in platforms:
            # Check if Karel is horizontally overlapping with platform
            horizontal_overlap = (self.x + self.width > platform.x and 
                                self.x < platform.x + platform.width)
            
            if horizontal_overlap:
                # Landing on top of platform (falling down)
                if (self.velocity_y > 0 and 
                    karel_bottom >= platform.y and 
                    karel_bottom <= platform.y + platform.height):
                    
                    # Karel is landing on this platform
                    self.y = platform.y - self.height
                    self.velocity_y = 0
                    self.on_ground = True
                    break
                
                # Hitting platform from below (jumping up)
                elif (self.velocity_y < 0 and 
                      karel_top <= platform.y + platform.height and 
                      karel_top >= platform.y):
                    
                    # Karel hit platform from below, stop upward movement
                    self.y = platform.y + platform.height
                    self.velocity_y = 0
                    break
        
        # Check ground collision as fallback
        if not self.on_ground and karel_bottom >= GROUND_LEVEL:
            self.y = GROUND_LEVEL - self.height
            self.velocity_y = 0
            self.on_ground = True
    
    def update(self, keys_pressed, platforms):
        """Update Karel's position based on keyboard input and physics."""
        # Handle horizontal movement
        if keys_pressed[pygame.K_LEFT]:
            self.move_left()
        if keys_pressed[pygame.K_RIGHT]:
            self.move_right()
        
        # Handle jumping
        if keys_pressed[pygame.K_SPACE]:
            self.jump()
        
        # Apply physics
        self.apply_gravity()
        
        # Update vertical position
        self.y += self.velocity_y
        
        # Check platform collision
        self.check_platform_collision(platforms)
        
        # Update collision rectangle
        self.rect.x = self.x
        self.rect.y = self.y
    
    def draw(self, screen):
        """Draw Karel as a blue rectangle with white 'K' label."""
        # Draw blue rectangle
        pygame.draw.rect(screen, KAREL_BLUE, self.rect)
        
        # Draw white 'K' label centered on Karel
        try:
            font = pygame.font.Font(None, 24)
            k_text = font.render('K', True, WHITE)
            # Center the 'K' on Karel
            text_rect = k_text.get_rect(center=(self.x + self.width//2, self.y + self.height//2))
            screen.blit(k_text, text_rect)
        except pygame.error as e:
            print(f"WARNING: Karel label rendering error - {e}")

class KarelGame:
    """
    Main game class that handles initialization, game loop, and cleanup.
    Designed for Stanford CIP browser environment compatibility.
    """
    
    def __init__(self):
        """Initialize the game window and pygame systems."""
        self.screen = None
        self.clock = None
        self.running = False
        
        # Initialize pygame with error handling
        if not self._initialize_pygame():
            sys.exit(1)
        
        # Create Karel character
        self.karel = Karel(KAREL_START_X, KAREL_START_Y)
        
        # Create platforms for the level
        self.platforms = [
            Platform(200, 400, 100, 20),  # Platform 1
            Platform(350, 320, 80, 20),   # Platform 2  
            Platform(480, 240, 120, 20),  # Platform 3
            Platform(600, 160, 100, 20),  # Platform 4 (highest)
            Platform(0, GROUND_LEVEL, WINDOW_WIDTH, GROUND_HEIGHT)  # Ground platform
        ]
    
    def _initialize_pygame(self):
        """
        Initialize pygame systems with comprehensive error handling.
        Returns True if successful, False otherwise.
        """
        try:
            # Initialize pygame
            pygame.init()
            
            # Check if pygame initialized successfully
            if not pygame.get_init():
                print("ERROR: Pygame failed to initialize")
                return False
            
            # Create the game window
            self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
            pygame.display.set_caption(GAME_TITLE)
            
            # Initialize game clock for FPS control
            self.clock = pygame.time.Clock()
            
            print(f"Game initialized successfully: {WINDOW_WIDTH}x{WINDOW_HEIGHT}")
            print(f"Running at {FPS} FPS")
            return True
            
        except pygame.error as e:
            print(f"ERROR: Pygame initialization failed - {e}")
            return False
        except Exception as e:
            print(f"ERROR: Unexpected error during initialization - {e}")
            return False
    
    def handle_events(self):
        """
        Process all pygame events.
        Handle window close events and basic input.
        """
        for event in pygame.event.get():
            # Handle window close button
            if event.type == pygame.QUIT:
                self.running = False
            
            # Handle ESC key to quit (useful for CIP environment)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
    
    def update(self):
        """
        Update game logic.
        Handle Karel movement and other game mechanics.
        """
        # Get currently pressed keys for smooth movement
        keys_pressed = pygame.key.get_pressed()
        
        # Update Karel's position based on input and platforms
        self.karel.update(keys_pressed, self.platforms)
    
    def draw(self):
        """
        Render the current game state to the screen.
        Draw Karel, platforms, and game instructions.
        """
        # Clear screen with black background
        self.screen.fill(BLACK)
        
        # Draw all platforms
        for platform in self.platforms:
            platform.draw(self.screen)
        
        # Draw Karel character
        self.karel.draw(self.screen)
        
        # Draw game instructions
        try:
            font = pygame.font.Font(None, 24)
            instruction_text = font.render("Arrow Keys: Move | Spacebar: Jump | ESC: Quit", True, WHITE)
            
            # Position instructions at top of screen
            instruction_rect = instruction_text.get_rect(center=(WINDOW_WIDTH//2, 30))
            self.screen.blit(instruction_text, instruction_rect)
            
        except pygame.error as e:
            print(f"WARNING: Text rendering error - {e}")
        
        # Update display
        pygame.display.flip()
    
    def run(self):
        """
        Main game loop.
        Handles events, updates game state, and renders at consistent FPS.
        """
        self.running = True
        print(f"Starting {GAME_TITLE}...")
        print("Game loop running - close window or press ESC to quit")
        
        try:
            while self.running:
                # Handle all events (input, window close, etc.)
                self.handle_events()
                
                # Update game logic
                self.update()
                
                # Render current frame
                self.draw()
                
                # Maintain consistent FPS
                self.clock.tick(FPS)
                
        except Exception as e:
            print(f"ERROR: Game loop error - {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """
        Clean up pygame resources before exit.
        Ensures proper shutdown in CIP environment.
        """
        print("Shutting down game...")
        pygame.quit()
        print("Game shutdown complete")

def main():
    """
    Entry point for Karel's Code Quest.
    Creates and runs the game instance.
    """
    print("=" * 50)
    print("Karel's Code Quest - Stanford CIP Final Project")
    print("=" * 50)
    
    # Create and run the game
    game = KarelGame()
    game.run()

# Run the game when script is executed directly
if __name__ == "__main__":
    main()