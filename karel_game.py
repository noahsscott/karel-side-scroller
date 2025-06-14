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

# World Settings (Side-Scroller)
WORLD_WIDTH = 3200               # Total world width (Mario-style level)
WORLD_HEIGHT = WINDOW_HEIGHT     # Keep same height

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

# Goal Flag System Constants
GOAL_FLAG_WIDTH = 20                 # Goal flag width
GOAL_FLAG_HEIGHT = 40                # Goal flag height
GOAL_FLAG_X = 3100                   # Goal flag x position (near level end)
GOAL_BASE_COLOR = (255, 0, 0)        # Red (0% beepers)
GOAL_MAX_COLOR = (0, 255, 0)         # Green (100% beepers)

# Particle System Constants
PARTICLE_COUNT = 5                   # Particles per beeper collection
PARTICLE_LIFETIME = 30               # Frames particles last
PARTICLE_SPEED = 3                   # Particle movement speed

# Screen Effects Constants
SHAKE_DURATION = 20                  # Frames screen shakes
SHAKE_INTENSITY = 5                  # Shake pixel range
WIN_SCREEN_DURATION = 180            # 3 seconds at 60fps

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

class Particle:
    """
    Simple particle for beeper collection effects.
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vel_x = (pygame.time.get_ticks() % 7 - 3) * PARTICLE_SPEED / 3
        self.vel_y = -(pygame.time.get_ticks() % 5 + 2) * PARTICLE_SPEED / 2
        self.lifetime = PARTICLE_LIFETIME
        self.max_lifetime = PARTICLE_LIFETIME
    
    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.vel_y += 0.2  # Gravity
        self.lifetime -= 1
        return self.lifetime > 0
    
    def draw(self, screen, camera):
        if self.lifetime > 0:
            screen_x, screen_y = camera.get_screen_pos(self.x, self.y)
            alpha = self.lifetime / self.max_lifetime
            color = (100, 150, 255)  # Blue particles
            size = max(1, int(3 * alpha))
            pygame.draw.circle(screen, color, (int(screen_x), int(screen_y)), size)

class GoalFlag:
    """
    Dynamic goal flag that changes height and color based on beeper collection.
    
    Features:
    - Height varies based on beeper collection percentage
    - Color transitions from red (0%) to rainbow (100%)
    - Clear 'GOAL' text label
    - Positioned at level end for clear target
    """
    
    def __init__(self):
        """Initialize goal flag at level end position."""
        self.x = GOAL_FLAG_X
        self.base_y = GROUND_LEVEL - GOAL_FLAG_HEIGHT - 10  # Above ground level
        self.width = GOAL_FLAG_WIDTH
        self.height = GOAL_FLAG_HEIGHT
        self.reached = False
    
    def get_flag_color(self, beeper_percentage):
        """
        Calculate flag color based on beeper collection percentage.
        Red (0%) -> Yellow (25%) -> Green (50%) -> Cyan (75%) -> Blue (100%)
        """
        if beeper_percentage <= 0.25:
            # Red to Yellow
            t = beeper_percentage / 0.25
            return (255, int(255 * t), 0)
        elif beeper_percentage <= 0.5:
            # Yellow to Green
            t = (beeper_percentage - 0.25) / 0.25
            return (int(255 * (1-t)), 255, 0)
        elif beeper_percentage <= 0.75:
            # Green to Cyan
            t = (beeper_percentage - 0.5) / 0.25
            return (0, 255, int(255 * t))
        else:
            # Cyan to Blue
            t = (beeper_percentage - 0.75) / 0.25
            return (0, int(255 * (1-t)), 255)
    
    def get_flag_height(self, beeper_percentage):
        """
        Calculate flag height based on beeper collection percentage.
        Minimum 50% height, maximum 150% height.
        """
        min_height = GOAL_FLAG_HEIGHT * 0.5
        max_height = GOAL_FLAG_HEIGHT * 1.5
        return min_height + (max_height - min_height) * beeper_percentage
    
    def check_victory(self, karel):
        """
        Check if Karel has reached the goal flag.
        """
        if self.reached:
            return False
        
        karel_rect = pygame.Rect(karel.x, karel.y, karel.width, karel.height)
        flag_rect = pygame.Rect(self.x, self.base_y, self.width, self.height)
        
        if karel_rect.colliderect(flag_rect):
            self.reached = True
            print("🎉 LEVEL COMPLETE!")
            return True
        
        return False
    
    def draw(self, screen, beeper_percentage):
        """Draw goal flag with dynamic color and height."""
        flag_height = self.get_flag_height(beeper_percentage)
        flag_color = self.get_flag_color(beeper_percentage)
        flag_y = self.base_y - (flag_height - GOAL_FLAG_HEIGHT)
        
        # Draw flag rectangle
        flag_rect = pygame.Rect(self.x, flag_y, self.width, flag_height)
        pygame.draw.rect(screen, flag_color, flag_rect)
        pygame.draw.rect(screen, BLACK, flag_rect, 2)  # Black border
        
        # Draw 'GOAL' text
        try:
            font = pygame.font.Font(None, 16)
            goal_text = font.render('GOAL', True, WHITE)
            text_rect = goal_text.get_rect(center=(self.x + self.width//2, flag_y + flag_height//2))
            screen.blit(goal_text, text_rect)
        except pygame.error:
            pass

class Camera:
    """
    Mario-style camera system for side-scrolling gameplay.
    
    Features:
    - Smooth following with forward bias
    - No backward scrolling (classic Mario style)
    - Vertical centering around Karel
    - World boundary constraints
    """
    
    def __init__(self):
        """Initialize camera at world start."""
        self.x = 0  # Camera world position
        self.y = 0  # Vertical offset (usually 0)
        self.target_x = 0  # Smooth following target
        self.follow_speed = 0.1  # Camera smoothness (0.1 = slow, 1.0 = instant)
        
    def update(self, karel):
        """
        Update camera position to follow Karel with Mario-style behavior.
        Keep Karel more centered for better visibility.
        """
        # Calculate ideal camera position (Karel centered)
        ideal_camera_x = karel.x - WINDOW_WIDTH // 2  # Karel at center
        
        # Mario-style: Camera never moves backward
        if ideal_camera_x > self.target_x:
            self.target_x = ideal_camera_x
        
        # Smooth camera movement toward target
        self.x += (self.target_x - self.x) * self.follow_speed
        
        # Constrain camera to world boundaries
        self.x = max(0, min(self.x, WORLD_WIDTH - WINDOW_WIDTH))
        
        # Keep camera vertically centered
        self.y = 0
    
    def get_screen_pos(self, world_x, world_y, shake_x=0, shake_y=0):
        """Convert world coordinates to screen coordinates with optional shake."""
        screen_x = world_x - self.x + shake_x
        screen_y = world_y - self.y + shake_y
        return screen_x, screen_y
    
    def is_visible(self, world_x, world_y, width=32, height=32):
        """Check if an object at world position is visible on screen."""
        screen_x, screen_y = self.get_screen_pos(world_x, world_y)
        return (screen_x + width > 0 and screen_x < WINDOW_WIDTH and
                screen_y + height > 0 and screen_y < WINDOW_HEIGHT)

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
        
        # Check world boundary collision (can move to edge of world)
        if self.x > WORLD_WIDTH - self.width:
            self.x = WORLD_WIDTH - self.width
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
        Ground gaps allow Karel to fall through.
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
        
        # No fallback ground collision - Karel can fall through gaps!
        # This creates the Mario-style gap jumping challenge
    
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
        
        # Check if Karel fell into a gap (below screen)
        if self.y > WINDOW_HEIGHT + 100:  # Give some buffer
            # Reset Karel to starting position (Mario-style)
            self.x = KAREL_START_X
            self.y = KAREL_START_Y
            self.velocity_y = 0
            self.on_ground = False
            print("Karel fell! Respawn at start.")
            return True  # Signal screen shake
        return False
        
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
        self.game_won = False
        self.win_timer = 0
        self.particles = []
        self.screen_shake = 0
        self.camera_shake_x = 0
        self.camera_shake_y = 0
        
        # Initialize pygame with error handling
        if not self._initialize_pygame():
            sys.exit(1)
        
        # Load background image (optional)
        self._load_background_image()
        
        # Create camera system
        self.camera = Camera()
        
        # Create Karel character
        self.karel = Karel(KAREL_START_X, KAREL_START_Y)
        
        # Load extended level data
        self._create_level_data()
        
        # Create goal flag at level end
        self.goal_flag = GoalFlag()
        
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
    
    def _create_level_data(self):
        """
        Create extended Mario-style level layout across the 3200px world.
        Hand-placed platforms, walls, beepers, and ground gaps for strategic gameplay.
        """
        # Create ground segments with strategic gaps (Mario-style)
        self.platforms = [
            # Ground segments with gaps for jumping challenges
            Platform(0, GROUND_LEVEL, 400, GROUND_HEIGHT),        # Start ground (0-400)
            Platform(500, GROUND_LEVEL, 300, GROUND_HEIGHT),      # Gap 1: 400-500 (100px gap), ground 500-800
            Platform(900, GROUND_LEVEL, 300, GROUND_HEIGHT),      # Gap 2: 800-900 (100px gap), ground 900-1200
            Platform(1350, GROUND_LEVEL, 250, GROUND_HEIGHT),     # Gap 3: 1200-1350 (150px gap), ground 1350-1600
            Platform(1750, GROUND_LEVEL, 200, GROUND_HEIGHT),     # Gap 4: 1600-1750 (150px gap), ground 1750-1950
            Platform(2100, GROUND_LEVEL, 300, GROUND_HEIGHT),     # Gap 5: 1950-2100 (150px gap), ground 2100-2400  
            Platform(2600, GROUND_LEVEL, 600, GROUND_HEIGHT),     # Gap 6: 2400-2600 (200px gap), ground 2600-3200
            
            # Early section platforms (0-800px)
            Platform(200, 400, 100, 20),    # Starting area platform
            Platform(350, 320, 80, 20),     # Mid-low platform
            Platform(480, 240, 120, 20),    # Higher platform
            Platform(650, 160, 100, 20),    # Early high platform
            
            # Mid section platforms (800-1600px) 
            Platform(800, 350, 120, 20),    # Landing platform
            Platform(1000, 280, 80, 20),    # Jump challenge
            Platform(1200, 200, 100, 20),   # High route
            Platform(1400, 320, 150, 20),   # Large rest platform
            
            # Advanced section platforms (1600-2400px)
            Platform(1700, 240, 80, 20),    # Precision jumps
            Platform(1850, 180, 60, 20),    # Small platform
            Platform(2000, 240, 80, 20),    # Mirror jump
            Platform(2200, 160, 120, 20),   # High platform sequence
            Platform(2400, 300, 100, 20),   # Descent platform
            
            # Final section platforms (2400-3200px)
            Platform(2600, 220, 100, 20),   # Final challenges
            Platform(2800, 160, 80, 20),    # High finale
            Platform(3000, 280, 150, 20),   # Final large platform
        ]
        
        # No walls - clean platforming focus
        self.walls = []
        
        # Optional beepers for score (not required for victory)
        self.beepers = [
            # Strategic beepers on platforms and over gaps
            Beeper(150, GROUND_LEVEL - 20),          # Ground start
            Beeper(220, 400 - 25),                   # Platform 1
            Beeper(450, GROUND_LEVEL - 100),         # Above first gap - risky!
            Beeper(670, 160 - 25),                   # High platform
            Beeper(850, GROUND_LEVEL - 100),         # Above second gap - risky!
            Beeper(1050, 280 - 25),                  # Mid platform
            Beeper(1500, 220 - 25),                  # Platform beeper
            Beeper(2000, GROUND_LEVEL - 100),        # Above big gap - very risky!
            Beeper(2800, 280 - 25),                  # Near end
            Beeper(3050, 280 - 25),                  # Victory platform
        ]
    
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
            
            # Handle ESC key to quit and R key to restart
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_r and self.game_won and self.win_timer <= 60:
                    # Restart game
                    self.restart_game()
    
    def update(self):
        """
        Update game logic.
        Handle Karel movement, physics, wall collision, and beeper collection.
        """
        # Get currently pressed keys for smooth movement
        keys_pressed = pygame.key.get_pressed()
        
        # Update Karel's position based on input, platforms, and walls
        if self.karel.update(keys_pressed, self.platforms, self.walls):
            # Karel fell - trigger screen shake
            self.screen_shake = SHAKE_DURATION
        
        # Update camera to follow Karel (with shake)
        self.camera.update(self.karel)
        
        # Update screen shake
        if self.screen_shake > 0:
            import random
            self.camera_shake_x = random.randint(-SHAKE_INTENSITY, SHAKE_INTENSITY)
            self.camera_shake_y = random.randint(-SHAKE_INTENSITY, SHAKE_INTENSITY)
            self.screen_shake -= 1
        else:
            self.camera_shake_x = 0
            self.camera_shake_y = 0
        
        # Check beeper collection with particle effects
        for beeper in self.beepers:
            if beeper.check_collection(self.karel):
                self.score += beeper.points
                # Create particles
                for _ in range(PARTICLE_COUNT):
                    self.particles.append(Particle(beeper.x, beeper.y))
        
        # Update particles
        self.particles = [p for p in self.particles if p.update()]
        
        # Check victory condition
        if not self.game_won:
            if self.goal_flag.check_victory(self.karel):
                self.game_won = True
                self.win_timer = WIN_SCREEN_DURATION
        
        # Update win screen timer
        if self.game_won and self.win_timer > 0:
            self.win_timer -= 1
    
    def draw_grid(self):
        """Draw Karel's signature grid background with plus signs."""
        # Calculate grid range based on camera position
        start_x = int(self.camera.x // GRID_SIZE) * GRID_SIZE
        end_x = start_x + WINDOW_WIDTH + GRID_SIZE
        
        # Draw plus signs at grid intersections (camera-relative)
        for world_x in range(start_x, end_x + 1, GRID_SIZE):
            for world_y in range(0, WINDOW_HEIGHT + 1, GRID_SIZE):
                screen_x, screen_y = self.camera.get_screen_pos(world_x, world_y)
                
                # Only draw if on screen
                if 0 <= screen_x <= WINDOW_WIDTH:
                    # Draw plus sign at each intersection
                    plus_size = 3
                    # Horizontal line of plus
                    pygame.draw.line(self.screen, GRID_COLOR, 
                                   (screen_x - plus_size, screen_y), (screen_x + plus_size, screen_y), 1)
                    # Vertical line of plus
                    pygame.draw.line(self.screen, GRID_COLOR, 
                                   (screen_x, screen_y - plus_size), (screen_x, screen_y + plus_size), 1)
    
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
        
        # Draw all platforms (only visible ones for performance) with screen shake
        for platform in self.platforms:
            if self.camera.is_visible(platform.x, platform.y, platform.width, platform.height):
                screen_x, screen_y = self.camera.get_screen_pos(platform.x, platform.y, self.camera_shake_x, self.camera_shake_y)
                screen_rect = pygame.Rect(screen_x, screen_y, platform.width, platform.height)
                pygame.draw.rect(self.screen, GROUND_GREEN, screen_rect)
        
        # Draw all walls (only visible ones)
        for wall in self.walls:
            if self.camera.is_visible(wall.x, wall.y, wall.width, wall.height):
                screen_x, screen_y = self.camera.get_screen_pos(wall.x, wall.y)
                screen_rect = pygame.Rect(screen_x, screen_y, wall.width, wall.height)
                pygame.draw.rect(self.screen, WALL_RED, screen_rect)
                
                # Draw 'W' text
                try:
                    font = pygame.font.Font(None, 24)
                    w_text = font.render('W', True, WHITE)
                    text_rect = w_text.get_rect(center=(screen_x + wall.width//2, screen_y + wall.height//2))
                    self.screen.blit(w_text, text_rect)
                except pygame.error:
                    pass
        
        # Draw all beepers (only visible and uncollected ones) with screen shake
        for beeper in self.beepers:
            if not beeper.collected and self.camera.is_visible(beeper.x, beeper.y, BEEPER_RADIUS*2, BEEPER_RADIUS*2):
                screen_x, screen_y = self.camera.get_screen_pos(beeper.x, beeper.y, self.camera_shake_x, self.camera_shake_y)
                pygame.draw.circle(self.screen, BEEPER_YELLOW, (int(screen_x), int(screen_y)), beeper.radius)
                
                # Draw 'B' text
                try:
                    font = pygame.font.Font(None, 16)
                    b_text = font.render('B', True, BLACK)
                    text_rect = b_text.get_rect(center=(int(screen_x), int(screen_y)))
                    self.screen.blit(b_text, text_rect)
                except pygame.error:
                    pass
        
        # Draw goal flag (if visible)
        if self.camera.is_visible(self.goal_flag.x, self.goal_flag.base_y, GOAL_FLAG_WIDTH, GOAL_FLAG_HEIGHT * 1.5):
            screen_x, screen_y = self.camera.get_screen_pos(self.goal_flag.x, self.goal_flag.base_y, self.camera_shake_x, self.camera_shake_y)
            
            # Calculate beeper percentage
            beepers_collected = sum(1 for b in self.beepers if b.collected)
            total_beepers = len(self.beepers)
            beeper_percentage = beepers_collected / total_beepers if total_beepers > 0 else 0
            
            # Draw goal flag with dynamic properties
            flag_height = self.goal_flag.get_flag_height(beeper_percentage)
            flag_color = self.goal_flag.get_flag_color(beeper_percentage)
            flag_y = screen_y - (flag_height - GOAL_FLAG_HEIGHT)
            
            flag_rect = pygame.Rect(screen_x, flag_y, GOAL_FLAG_WIDTH, flag_height)
            pygame.draw.rect(self.screen, flag_color, flag_rect)
            pygame.draw.rect(self.screen, BLACK, flag_rect, 2)
            
            # Draw 'GOAL' text
            try:
                font = pygame.font.Font(None, 16)
                goal_text = font.render('GOAL', True, WHITE)
                text_rect = goal_text.get_rect(center=(screen_x + GOAL_FLAG_WIDTH//2, flag_y + flag_height//2))
                self.screen.blit(goal_text, text_rect)
            except pygame.error:
                pass
        
        # Draw particles
        for particle in self.particles:
            particle.draw(self.screen, self.camera)
        
        # Draw Karel character with screen shake
        screen_x, screen_y = self.camera.get_screen_pos(self.karel.x, self.karel.y, self.camera_shake_x, self.camera_shake_y)
        screen_rect = pygame.Rect(screen_x, screen_y, self.karel.width, self.karel.height)
        pygame.draw.rect(self.screen, KAREL_BLUE, screen_rect)
        
        # Draw Karel's 'K' text
        try:
            font = pygame.font.Font(None, 24)
            k_text = font.render('K', True, WHITE)
            text_rect = k_text.get_rect(center=(screen_x + self.karel.width//2, screen_y + self.karel.height//2))
            self.screen.blit(k_text, text_rect)
        except pygame.error:
            pass
        
        # Draw UI elements
        try:
            # Score and progress display in top-left corner
            score_font = pygame.font.Font(None, 28)
            beepers_collected = sum(1 for b in self.beepers if b.collected)
            total_beepers = len(self.beepers)
            score_text = score_font.render(f"Score: {self.score} | Beepers: {beepers_collected}/{total_beepers}", True, BLACK)
            self.screen.blit(score_text, (10, 10))
            
            # Game title at top center
            title_font = pygame.font.Font(None, 36)
            if self.game_won:
                title_text = title_font.render("🎉 VICTORY! Code Quest Complete! 🎉", True, BLACK)
            else:
                title_text = title_font.render("Karel's Code Quest", True, BLACK)
            title_rect = title_text.get_rect(center=(WINDOW_WIDTH//2, 25))
            self.screen.blit(title_text, title_rect)
            
            # Instructions at bottom
            instruction_font = pygame.font.Font(None, 20)
            if self.game_won and self.win_timer > 0:
                # Win screen display
                instruction_text = instruction_font.render(f"LEVEL COMPLETE! Final Score: {self.score}", True, BLACK)
                if self.win_timer < 60:  # Last second
                    restart_text = instruction_font.render("Press R to Restart", True, BLACK)
                    restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT - 40))
                    self.screen.blit(restart_text, restart_rect)
            else:
                instruction_text = instruction_font.render("Arrow Keys: Move, Spacebar: Jump, Reach GOAL Flag to Win!", True, BLACK)
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
    
    def restart_game(self):
        """
        Restart the game to initial state.
        """
        self.score = 0
        self.game_won = False
        self.win_timer = 0
        self.particles = []
        self.screen_shake = 0
        self.camera_shake_x = 0
        self.camera_shake_y = 0
        
        # Reset Karel
        self.karel = Karel(KAREL_START_X, KAREL_START_Y)
        
        # Reset camera
        self.camera = Camera()
        
        # Reset beepers
        for beeper in self.beepers:
            beeper.collected = False
        
        # Reset goal flag
        self.goal_flag = GoalFlag()
    
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