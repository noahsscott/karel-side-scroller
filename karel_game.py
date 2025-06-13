"""
Karel's Code Quest - A Side-Scrolling Platformer Game
Stanford CIP Final Project

This is a single-file pygame implementation designed to run in the CIP browser environment.
Karel, the beloved Stanford CS robot, embarks on a coding adventure through various levels.

DAY 1 FEATURES:
- 640x480 game window with authentic Karel world aesthetic
- Karel character with smooth left/right movement and jumping
- Realistic physics system with gravity and collision detection  
- Multi-platform level with 4 different height platforms
- Karel-style grid background with plus signs
- Optional background image support
- Stable 60fps performance

CONTROLS:
- Left/Right Arrow Keys: Move Karel horizontally
- Spacebar: Jump (only when on ground)
- ESC: Quit game

ARCHITECTURE:
- Karel class: Player character with physics and rendering
- Platform class: Reusable collision surfaces  
- KarelGame class: Main game loop and system management
"""

import pygame
import sys

# ============================================================================
# GAME CONFIGURATION AND CONSTANTS
# ============================================================================

# Window and Performance Settings
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480
FPS = 60
GAME_TITLE = "Karel's Code Quest"

# Karel Character Settings
KAREL_SIZE = 32
KAREL_SPEED = 5
KAREL_START_X = 50
KAREL_START_Y = WINDOW_HEIGHT - 100

# Physics System Constants
GRAVITY = 0.8                # Downward acceleration per frame
JUMP_VELOCITY = -15          # Initial upward velocity when jumping
TERMINAL_VELOCITY = 12       # Maximum falling speed
GROUND_HEIGHT = 50           # Height of ground platform
GROUND_LEVEL = WINDOW_HEIGHT - GROUND_HEIGHT

# Visual Style Settings
GRID_SIZE = 25               # Size of Karel world grid squares
BACKGROUND_IMAGE_PATH = "background.png"  # Optional background image

# Color Palette (Authentic Karel World Aesthetic)
KAREL_BACKGROUND = (240, 240, 240)  # Light gray background
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
KAREL_BLUE = (0, 100, 255)          # Karel's signature blue
GROUND_GREEN = (0, 200, 0)          # Platform green
GRID_COLOR = BLACK                   # Grid plus signs
BEEPER_YELLOW = (255, 255, 0)       # Beeper color
WALL_RED = (200, 0, 0)              # Wall color

# Beeper System Constants
BEEPER_RADIUS = 8                    # Beeper visual size
BEEPER_COLLECTION_DISTANCE = 20     # Distance for Karel to collect beeper
BEEPER_POINTS = 10                  # Points awarded per beeper

# Wall System Constants
WALL_SIZE = 32                       # Wall width and height

# ============================================================================
# GAME OBJECT CLASSES
# ============================================================================

class Platform:
    """
    Platform class representing solid surfaces Karel can land on.
    Used for both level platforms and the ground.
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

class Beeper:
    """
    Beeper class representing collectible items in Karel's world.
    
    Features:
    - Yellow circle with black 'B' text
    - Strategic placement on platforms
    - Collection detection with Karel
    - Score value when collected
    """
    
    def __init__(self, x, y):
        """Initialize beeper at the given position."""
        self.x = x
        self.y = y
        self.radius = BEEPER_RADIUS
        self.collected = False
        self.points = BEEPER_POINTS
    
    def check_collection(self, karel):
        """
        Check if Karel is close enough to collect this beeper.
        Returns True if collected, False otherwise.
        """
        if self.collected:
            return False
        
        # Calculate distance between Karel center and beeper center
        karel_center_x = karel.x + karel.width // 2
        karel_center_y = karel.y + karel.height // 2
        
        distance = ((karel_center_x - self.x) ** 2 + (karel_center_y - self.y) ** 2) ** 0.5
        
        if distance < BEEPER_COLLECTION_DISTANCE:
            self.collected = True
            print('Beep collected!')  # Sound effect placeholder
            return True
        
        return False
    
    def draw(self, screen):
        """Draw beeper as yellow circle with black 'B' text."""
        if not self.collected:
            # Draw yellow circle
            pygame.draw.circle(screen, BEEPER_YELLOW, (int(self.x), int(self.y)), self.radius)
            
            # Draw black 'B' text centered on beeper
            try:
                font = pygame.font.Font(None, 16)
                b_text = font.render('B', True, BLACK)
                text_rect = b_text.get_rect(center=(int(self.x), int(self.y)))
                screen.blit(b_text, text_rect)
            except pygame.error as e:
                print(f"WARNING: Beeper label rendering error - {e}")

class Wall:
    """
    Wall class representing solid obstacles Karel must navigate around.
    
    Features:
    - Red 32x32 rectangle with white 'W' text
    - Solid collision from all directions
    - Can act as platforms (Karel can land on top)
    - Creates navigation challenges and puzzle elements
    """
    
    def __init__(self, x, y):
        """Initialize wall at the given position."""
        self.x = x
        self.y = y
        self.width = WALL_SIZE
        self.height = WALL_SIZE
        self.rect = pygame.Rect(x, y, self.width, self.height)
    
    def draw(self, screen):
        """Draw wall as red rectangle with white 'W' text."""
        # Draw red rectangle
        pygame.draw.rect(screen, WALL_RED, self.rect)
        
        # Draw white 'W' text centered on wall
        try:
            font = pygame.font.Font(None, 24)
            w_text = font.render('W', True, WHITE)
            text_rect = w_text.get_rect(center=(self.x + self.width//2, self.y + self.height//2))
            screen.blit(w_text, text_rect)
        except pygame.error as e:
            print(f"WARNING: Wall label rendering error - {e}")

class Karel:
    """
    Karel character class representing the player.
    
    Features:
    - Blue 32x32 rectangle with white 'K' label
    - Smooth horizontal movement with boundary checking
    - Physics-based jumping and gravity
    - Platform collision detection (top and bottom)
    - Prevents double jumping and infinite jump exploits
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
    
    def move_left(self, walls):
        """Move Karel left while respecting boundaries and walls."""
        # Save original position
        original_x = self.x
        
        # Try to move left
        self.x -= self.speed
        self.rect.x = self.x
        
        # Check boundary collision
        if self.x < 0:
            self.x = 0
            self.rect.x = self.x
            return
        
        # Check wall collisions
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                # Collision detected - revert movement
                self.x = original_x
                self.rect.x = self.x
                return
    
    def move_right(self, walls):
        """Move Karel right while respecting boundaries and walls."""
        # Save original position
        original_x = self.x
        
        # Try to move right
        self.x += self.speed
        self.rect.x = self.x
        
        # Check boundary collision
        if self.x > WINDOW_WIDTH - self.width:
            self.x = WINDOW_WIDTH - self.width
            self.rect.x = self.x
            return
        
        # Check wall collisions
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                # Collision detected - revert movement
                self.x = original_x
                self.rect.x = self.x
                return
    
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
    
    def check_platform_collision(self, platforms, walls):
        """
        Check if Karel is colliding with any platform or wall.
        Handles both top and bottom collisions with proper edge case handling.
        Walls act as platforms for landing but also block movement.
        """
        karel_bottom = self.y + self.height
        karel_top = self.y
        self.on_ground = False
        
        # Combine platforms and walls for collision detection
        all_obstacles = list(platforms) + list(walls)
        
        # Check collision with all obstacles (platforms and walls)
        for obstacle in all_obstacles:
            # Check if Karel is horizontally overlapping with obstacle
            horizontal_overlap = (self.x + self.width > obstacle.x and 
                                self.x < obstacle.x + obstacle.width)
            
            if horizontal_overlap:
                # Landing on top of obstacle (falling down)
                if (self.velocity_y >= 0 and 
                    karel_bottom >= obstacle.y and 
                    karel_bottom <= obstacle.y + obstacle.height + self.velocity_y):
                    
                    # Karel is landing on this obstacle
                    self.y = obstacle.y - self.height
                    self.velocity_y = 0
                    self.on_ground = True
                    break
                
                # Hitting obstacle from below (jumping up)
                elif (self.velocity_y < 0 and 
                      karel_top <= obstacle.y + obstacle.height and 
                      karel_top >= obstacle.y + self.velocity_y):
                    
                    # Karel hit obstacle from below, stop upward movement
                    self.y = obstacle.y + obstacle.height
                    self.velocity_y = 0
                    break
        
        # Check ground collision as fallback
        if not self.on_ground and karel_bottom >= GROUND_LEVEL:
            self.y = GROUND_LEVEL - self.height
            self.velocity_y = 0
            self.on_ground = True
    
    def update(self, keys_pressed, platforms, walls):
        """Update Karel's position based on keyboard input, physics, and obstacles."""
        # Handle horizontal movement
        if keys_pressed[pygame.K_LEFT]:
            self.move_left(walls)
        if keys_pressed[pygame.K_RIGHT]:
            self.move_right(walls)
        
        # Handle jumping
        if keys_pressed[pygame.K_SPACE]:
            self.jump()
        
        # Apply physics
        self.apply_gravity()
        
        # Update vertical position
        self.y += self.velocity_y
        
        # Check platform and wall collision
        self.check_platform_collision(platforms, walls)
        
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

# ============================================================================
# MAIN GAME CLASS
# ============================================================================

class KarelGame:
    """
    Main game class that handles initialization, game loop, and cleanup.
    
    Responsibilities:
    - Pygame system initialization and window creation
    - Game loop management (60fps with proper timing)
    - Event handling (input, window close)
    - Game state updates (Karel movement, physics)
    - Rendering (background, platforms, Karel, UI)
    - Optional background image loading
    - Clean resource cleanup on exit
    
    Designed for Stanford CIP browser environment compatibility.
    """
    
    def __init__(self):
        """Initialize the game window and pygame systems."""
        self.screen = None
        self.clock = None
        self.running = False
        self.background_image = None
        self.score = 0
        
        # Initialize pygame with error handling
        if not self._initialize_pygame():
            sys.exit(1)
        
        # Load background image (optional)
        self._load_background_image()
        
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
        
        # Create beepers strategically placed above platforms
        self.beepers = [
            # Ground level beepers
            Beeper(150, GROUND_LEVEL - 20),
            Beeper(300, GROUND_LEVEL - 20),
            
            # Platform 1 beepers (200, 400, 100, 20) - place above platform
            Beeper(220, 400 - 25),
            Beeper(270, 400 - 25),
            
            # Platform 2 beepers (350, 320, 80, 20) - place above platform
            Beeper(370, 320 - 25),
            Beeper(400, 320 - 25),
            
            # Platform 3 beeper (480, 240, 120, 20) - place above platform
            Beeper(520, 240 - 25),
            
            # Platform 4 beeper (600, 160, 100, 20) - highest platform
            Beeper(650, 160 - 25),
        ]
        
        # Create walls strategically placed to create navigation challenges
        self.walls = [
            # Wall 1: Ground level obstacle - forces jumping over
            Wall(320, GROUND_LEVEL - WALL_SIZE),
            
            # Wall 2: Platform 2 obstacle - blocks direct path  
            Wall(380, 320 - WALL_SIZE),
            
            # Wall 3: Platform 3 maze element
            Wall(500, 240 - WALL_SIZE),
            
            # Wall 4: Additional challenge near Platform 1
            Wall(250, 400 - WALL_SIZE),
            
            # Wall 5: High wall creating vertical challenge
            Wall(550, 320 - WALL_SIZE),
        ]
        
        # Adjust beeper positions to avoid all obstacle conflicts
        self._resolve_beeper_obstacle_conflicts()
    
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
            
            return True
            
        except pygame.error as e:
            print(f"ERROR: Pygame initialization failed - {e}")
            return False
        except Exception as e:
            print(f"ERROR: Unexpected error during initialization - {e}")
            return False
    
    def _load_background_image(self):
        """
        Load background image if available.
        Falls back to procedural background if image not found.
        """
        try:
            self.background_image = pygame.image.load(BACKGROUND_IMAGE_PATH)
            # Scale to fit window if needed
            if self.background_image.get_size() != (WINDOW_WIDTH, WINDOW_HEIGHT):
                self.background_image = pygame.transform.scale(
                    self.background_image, (WINDOW_WIDTH, WINDOW_HEIGHT))
            pass  # Background image loaded successfully
        except (pygame.error, FileNotFoundError):
            # Background image not found - use procedural background
            self.background_image = None
    
    def _check_beeper_obstacle_collision(self, beeper_x, beeper_y):
        """
        Check if a beeper position conflicts with any wall or platform.
        Returns True if there's a collision, False otherwise.
        """
        # Create temporary beeper area (using collection distance as buffer)
        beeper_area = pygame.Rect(
            beeper_x - BEEPER_COLLECTION_DISTANCE // 2,
            beeper_y - BEEPER_COLLECTION_DISTANCE // 2,
            BEEPER_COLLECTION_DISTANCE,
            BEEPER_COLLECTION_DISTANCE
        )
        
        # Check collision with all walls
        for wall in self.walls:
            if beeper_area.colliderect(wall.rect):
                return True
        
        # Check collision with platforms (beeper should be above, not inside)
        for platform in self.platforms:
            # Check if beeper center is inside platform
            if (beeper_x >= platform.x and beeper_x <= platform.x + platform.width and
                beeper_y >= platform.y and beeper_y <= platform.y + platform.height):
                return True
        
        return False
    
    def _resolve_beeper_obstacle_conflicts(self):
        """
        Identify and resolve conflicts between beepers and all obstacles (walls and platforms).
        Moves beepers to nearby safe positions when conflicts are detected.
        """
        conflicts_resolved = 0
        
        for beeper in self.beepers:
            if self._check_beeper_obstacle_collision(beeper.x, beeper.y):
                conflicts_resolved += 1
                # Try to find a safe position nearby
                original_x, original_y = beeper.x, beeper.y
                
                # Try moving left or right in small increments
                for offset in [-40, 40, -60, 60, -80, 80]:
                    new_x = original_x + offset
                    # Make sure it's still on screen and not conflicting
                    if (0 <= new_x <= WINDOW_WIDTH and 
                        not self._check_beeper_obstacle_collision(new_x, beeper.y)):
                        beeper.x = new_x
                        break
                else:
                    # If horizontal movement doesn't work, try vertical adjustment
                    for y_offset in [-30, 30]:
                        new_y = original_y + y_offset
                        if (new_y > 0 and new_y < WINDOW_HEIGHT and
                            not self._check_beeper_obstacle_collision(beeper.x, new_y)):
                            beeper.y = new_y
                            break
    
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
        Handle Karel movement, physics, wall collision, and beeper collection.
        """
        # Get currently pressed keys for smooth movement
        keys_pressed = pygame.key.get_pressed()
        
        # Update Karel's position based on input, platforms, and walls
        self.karel.update(keys_pressed, self.platforms, self.walls)
        
        # Check beeper collection
        for beeper in self.beepers:
            if beeper.check_collection(self.karel):
                self.score += beeper.points
    
    def draw_grid(self):
        """Draw Karel's signature grid background with plus signs."""
        # Draw plus signs at grid intersections
        for x in range(0, WINDOW_WIDTH + 1, GRID_SIZE):
            for y in range(0, WINDOW_HEIGHT + 1, GRID_SIZE):
                # Draw plus sign at each intersection
                plus_size = 3
                # Horizontal line of plus
                pygame.draw.line(self.screen, GRID_COLOR, 
                               (x - plus_size, y), (x + plus_size, y), 1)
                # Vertical line of plus
                pygame.draw.line(self.screen, GRID_COLOR, 
                               (x, y - plus_size), (x, y + plus_size), 1)
    
    def draw(self):
        """
        Render the current game state to the screen.
        Draw background, Karel, platforms, and UI elements.
        """
        # Draw background (image if available, otherwise procedural)
        if self.background_image:
            # Use background image
            self.screen.blit(self.background_image, (0, 0))
        else:
            # Use procedural Karel world background
            self.screen.fill(KAREL_BACKGROUND)
            self.draw_grid()
        
        # Draw all platforms
        for platform in self.platforms:
            platform.draw(self.screen)
        
        # Draw all walls
        for wall in self.walls:
            wall.draw(self.screen)
        
        # Draw all beepers
        for beeper in self.beepers:
            beeper.draw(self.screen)
        
        # Draw Karel character
        self.karel.draw(self.screen)
        
        # Draw UI elements
        try:
            # Score display in top-left corner
            score_font = pygame.font.Font(None, 28)
            score_text = score_font.render(f"Score: {self.score}", True, BLACK)
            self.screen.blit(score_text, (10, 10))
            
            # Game title at top center
            title_font = pygame.font.Font(None, 36)
            title_text = title_font.render("Karel's Code Quest", True, BLACK)
            title_rect = title_text.get_rect(center=(WINDOW_WIDTH//2, 25))
            self.screen.blit(title_text, title_rect)
            
            # Instructions at bottom
            instruction_font = pygame.font.Font(None, 20)
            instruction_text = instruction_font.render("Arrow Keys: Move, Spacebar: Jump, Collect Beepers, Navigate Walls!", True, BLACK)
            instruction_rect = instruction_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT - 20))
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
        pygame.quit()

# ============================================================================
# ENTRY POINT
# ============================================================================

def main():
    """
    Entry point for Karel's Code Quest.
    Creates and runs the game instance.
    """
    # Create and run the game
    game = KarelGame()
    game.run()

# Run the game when script is executed directly
if __name__ == "__main__":
    main()