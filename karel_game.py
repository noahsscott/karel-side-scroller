"""
Karel's Code Quest - A Side-Scrolling Platformer Game
Stanford CIP Final Project - Complete Day 2 Implementation

This is a single-file pygame implementation designed to run in the CIP browser environment.
Karel, the beloved Stanford CS robot, embarks on a coding adventure through various levels.

🎮 COMPLETE GAME FEATURES:
- 640x480 game window with authentic Karel world aesthetic  
- 60x60 Karel character with walking animation and directional sprites
- Comprehensive physics system with gravity, jumping, and collision detection
- Mario-style side-scrolling camera with forward bias
- Extended 3200px world with strategic platform placement
- Lives system (3 lives) with heart display and respawn mechanics
- Red spike hazards for challenge and consequence
- Beeper collection system with particle effects
- Solid staircase leading to victory flagpole
- Game over and victory states with restart functionality
- Clean UI with score, lives, and contextual messages
- 70px spaced grid background with 2px thick crosses
- Karel PNG image support with 60x60 scaling

🕹️ CONTROLS:
- Left/Right Arrow Keys: Move Karel horizontally (with walking animation)
- Spacebar: Jump (only when on ground)
- R: Restart game (when game over or victory)
- ESC: Quit game

🏗️ ARCHITECTURE:
- Karel class: Animated player character with physics and state management
- Platform class: Reusable collision surfaces for level design
- Hazard class: Red spike obstacles that trigger death/respawn
- Staircase class: Solid step-by-step platforms for level progression
- Flagpole class: Dynamic victory goal with color-changing flag
- Camera class: Mario-style side-scrolling view management
- KarelGame class: Complete game loop with lives, scoring, and state management

🎯 GAMEPLAY:
- Collect beepers for points (optional)
- Avoid red spike hazards that cost lives
- Navigate gaps, platforms, and obstacles
- Climb stairs to reach the victory flagpole
- 3 lives with smart respawn system
- Completion time target: 30-60 seconds for skilled players
"""

import pygame
import sys
import os

# ============================================================================
# GAME CONFIGURATION AND CONSTANTS
# Complete Day 2 Implementation - All Features Integrated
# ============================================================================

# Window and Performance Settings
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480
FPS = 60
GAME_TITLE = "Karel's Code Quest"

# World Settings (Side-Scroller)
WORLD_WIDTH = 3300               # Total world width (extended for full flag visibility)
WORLD_HEIGHT = WINDOW_HEIGHT     # Keep same height

# Karel Character Settings
KAREL_SIZE = 60
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
GRID_SIZE = 70               # Size of Karel world grid squares
BACKGROUND_IMAGE_PATH = "background.png"  # Optional background image
KAREL_IMAGE_PATH = "karel.png"            # Karel character image

# Color Palette (High Contrast, Accessible Design)
KAREL_BACKGROUND = (255, 255, 255)  # White background
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
KAREL_BLUE = (0, 80, 200)           # Higher contrast Karel blue
GROUND_GREEN = (0, 150, 0)          # Higher contrast platform green
GRID_COLOR = (100, 100, 100)        # Softer grid color for less eye strain
BEEPER_YELLOW = (255, 200, 0)       # More orange-yellow for better contrast
WALL_RED = (180, 0, 0)              # Slightly darker red
UI_BACKGROUND = (240, 240, 240)     # Light gray for UI elements
UI_TEXT_DARK = (20, 20, 20)         # Very dark gray for high contrast text
SUCCESS_GREEN = (0, 120, 0)         # Accessible green
WARNING_ORANGE = (255, 140, 0)      # High contrast orange
ERROR_RED = (200, 0, 0)             # High contrast red

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
MAX_PARTICLES = 20                   # Maximum particles on screen (performance limit)

# Screen Effects Constants
SHAKE_DURATION = 3                   # 3-frame camera shake when Karel dies
SHAKE_INTENSITY = 5                  # Shake pixel range
WIN_SCREEN_DURATION = 180            # 3 seconds at 60fps

# Lives System Constants
STARTING_LIVES = 3                   # Number of lives Karel starts with
INVINCIBILITY_DURATION = 120         # 2 seconds at 60fps
RESPAWN_DELAY = 60                   # 1 second delay before respawn
DEATH_THRESHOLD = WINDOW_HEIGHT + 50 # Y position that triggers death

# Hazard System Constants
HAZARD_SIZE = 20                     # Spike hazard size
HAZARD_COLOR = (200, 0, 0)           # Red color for spikes

# Instructions Screen Constants
INSTRUCTION_FONT_SIZE = 28            # Main instruction text size
INSTRUCTION_TITLE_SIZE = 36           # Title text size
INSTRUCTION_SMALL_SIZE = 20           # Small text size

# ============================================================================
# SOUND SYSTEM
# ============================================================================

class SoundManager:
    """
    Sound manager with graceful fallback support for CIP editor compatibility.
    
    Features:
    - Loads .wav files from assets/ folder when available
    - Falls back to console output when audio files are missing
    - Volume controls and mute functionality
    - No crashes from missing audio files or pygame.mixer issues
    """
    
    def __init__(self):
        """Initialize sound manager with fallback support."""
        self.sounds = {}
        self.muted = False
        self.volume = 0.7
        self.mixer_available = False
        self.assets_folder = "assets"
        
        # Try to initialize pygame mixer
        self._init_mixer()
        
        # Define expected sound files
        self.sound_files = {
            'jump': 'jump.wav',
            'beep': 'beep.wav', 
            'death': 'death.wav',
            'victory': 'victory.wav',
            'bg_music': 'bg_music.wav'
        }
        
        # Load all available sounds
        self._load_sounds()
    
    def _init_mixer(self):
        """Initialize pygame mixer with error handling."""
        try:
            pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
            pygame.mixer.init()
            self.mixer_available = True
            print("🔊 Audio system initialized successfully")
        except (pygame.error, Exception) as e:
            self.mixer_available = False
            print(f"🔇 Audio system unavailable: {e}")
            print("🔇 Using console output fallback for sound effects")
    
    def _load_sounds(self):
        """Load all sound files with fallback support."""
        if not self.mixer_available:
            print("🔇 No audio mixer - sound effects will use console output")
            return
        
        # Check if assets folder exists
        if not os.path.exists(self.assets_folder):
            print(f"📁 Assets folder '{self.assets_folder}' not found - using console fallback")
            return
        
        # Try to load each sound file
        for sound_name, filename in self.sound_files.items():
            filepath = os.path.join(self.assets_folder, filename)
            try:
                if os.path.exists(filepath):
                    sound = pygame.mixer.Sound(filepath)
                    sound.set_volume(self.volume)
                    self.sounds[sound_name] = sound
                    print(f"🔊 Loaded sound: {filename}")
                else:
                    print(f"🔇 Sound file not found: {filepath} (using console fallback)")
            except (pygame.error, Exception) as e:
                print(f"🔇 Failed to load {filename}: {e} (using console fallback)")
    
    def play_sound(self, sound_name, fallback_message=None):
        """
        Play a sound with fallback to console output.
        
        Args:
            sound_name: Name of the sound to play
            fallback_message: Message to print if sound unavailable
        """
        if self.muted:
            return
        
        # Try to play actual sound
        if self.mixer_available and sound_name in self.sounds:
            try:
                self.sounds[sound_name].play()
                return
            except (pygame.error, Exception) as e:
                print(f"🔇 Sound playback error: {e}")
        
        # Fallback to console output
        if fallback_message:
            print(fallback_message)
        else:
            # Default fallback messages
            fallback_messages = {
                'jump': '*Jump sound*',
                'beep': '*Beep collected*',
                'death': '*Death sound*',
                'victory': '*Victory fanfare*',
                'bg_music': '*Background music*'
            }
            if sound_name in fallback_messages:
                print(fallback_messages[sound_name])
            else:
                print(f'*{sound_name} sound*')
    
    def play_background_music(self):
        """Play background music if available."""
        if self.muted or not self.mixer_available:
            return
        
        if 'bg_music' in self.sounds:
            try:
                pygame.mixer.music.load(os.path.join(self.assets_folder, self.sound_files['bg_music']))
                pygame.mixer.music.set_volume(self.volume * 0.6)  # Quieter background music
                pygame.mixer.music.play(-1)  # Loop indefinitely
                print("🎵 Background music started")
            except (pygame.error, Exception) as e:
                print(f"🔇 Background music error: {e}")
    
    def stop_background_music(self):
        """Stop background music."""
        if self.mixer_available:
            try:
                pygame.mixer.music.stop()
            except (pygame.error, Exception):
                pass
    
    def toggle_mute(self):
        """Toggle mute state."""
        self.muted = not self.muted
        if self.muted:
            self.stop_background_music()
            print("🔇 Audio muted")
        else:
            self.play_background_music()
            print("🔊 Audio unmuted")
        return self.muted
    
    def set_volume(self, volume):
        """Set volume for all sounds (0.0 to 1.0)."""
        self.volume = max(0.0, min(1.0, volume))
        
        # Update volume for all loaded sounds
        for sound in self.sounds.values():
            try:
                sound.set_volume(self.volume)
            except (pygame.error, Exception):
                pass
        
        # Update music volume
        if self.mixer_available:
            try:
                pygame.mixer.music.set_volume(self.volume * 0.6)
            except (pygame.error, Exception):
                pass

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
    - Mario-style coin bounce animation when collected
    - Gentle bobbing animation when idle
    """
    
    def __init__(self, x, y):
        """Initialize beeper at the given position."""
        self.x = x
        self.y = y
        self.base_y = y  # Original Y position for bobbing animation
        self.radius = BEEPER_RADIUS
        self.collected = False
        self.points = BEEPER_POINTS
        
        # Animation states
        self.collecting = False
        self.collection_timer = 0
        self.collection_duration = 20  # Frames for coin jump animation
        self.bob_timer = 0  # For idle bobbing animation
        
        # Mario coin effect properties
        self.jump_velocity = 0
        self.jump_gravity = 0.8
    
    def update(self):
        """Update beeper animation states."""
        if self.collected:
            return
            
        # Handle collection animation
        if self.collecting:
            self.collection_timer += 1
            
            # Mario coin jump effect
            self.y += self.jump_velocity
            self.jump_velocity += self.jump_gravity
            
            # Check if collection animation is complete
            if self.collection_timer >= self.collection_duration:
                self.collected = True
                return
        else:
            # Gentle bobbing animation when idle (sin wave)
            self.bob_timer += 1
            bob_offset = 2 * pygame.math.Vector2(1, 0).rotate_rad(self.bob_timer * 0.1).y
            self.y = self.base_y + bob_offset
        
    def check_collection(self, karel):
        """
        Check if Karel is close enough to collect this beeper.
        Returns True if collection started, False otherwise.
        """
        if self.collected or self.collecting:
            return False
        
        # Calculate distance between Karel center and beeper center
        karel_center_x = karel.x + karel.width // 2
        karel_center_y = karel.y + karel.height // 2
        
        distance = ((karel_center_x - self.x) ** 2 + (karel_center_y - self.y) ** 2) ** 0.5
        
        if distance < BEEPER_COLLECTION_DISTANCE:
            # Start collection animation
            self.collecting = True
            self.collection_timer = 0
            self.jump_velocity = -8  # Initial upward velocity for jump
            return True
        
        return False
    
    def is_fully_collected(self):
        """Check if beeper is fully collected (animation complete)."""
        return self.collected
    
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
    Enhanced particle system supporting multiple particle types and effects.
    """
    
    # Particle type constants
    TYPE_BEEPER = "beeper"
    TYPE_DUST = "dust"
    TYPE_GLOW = "glow"
    TYPE_COIN = "coin"
    
    def __init__(self, x, y, particle_type="beeper", **kwargs):
        self.x = x
        self.y = y
        self.particle_type = particle_type
        self.lifetime = PARTICLE_LIFETIME
        self.max_lifetime = PARTICLE_LIFETIME
        
        # Initialize particle properties based on type
        if particle_type == self.TYPE_BEEPER:
            self._init_beeper_particle(**kwargs)
        elif particle_type == self.TYPE_DUST:
            self._init_dust_particle(**kwargs)
        elif particle_type == self.TYPE_GLOW:
            self._init_glow_particle(**kwargs)
        elif particle_type == self.TYPE_COIN:
            self._init_coin_particle(**kwargs)
        else:
            self._init_beeper_particle(**kwargs)
    
    def _init_beeper_particle(self, **kwargs):
        """Initialize blue beeper collection particle."""
        import random
        self.vel_x = random.uniform(-2, 2)
        self.vel_y = random.uniform(-4, -1)
        self.color = (100, 150, 255)  # Blue
        self.size = 3
        self.gravity = 0.2
        self.lifetime = 30
        self.max_lifetime = 30
    
    def _init_dust_particle(self, **kwargs):
        """Initialize gray dust puff particle."""
        import random
        self.vel_x = random.uniform(-1.5, 1.5)
        self.vel_y = random.uniform(-2, -0.5)
        self.color = (128, 128, 128)  # Gray
        self.size = random.randint(2, 4)
        self.gravity = 0.1
        self.lifetime = 20
        self.max_lifetime = 20
    
    def _init_glow_particle(self, **kwargs):
        """Initialize golden glow particle."""
        import random
        angle = random.uniform(0, 6.28)  # 2*pi
        speed = random.uniform(0.5, 1.5)
        self.vel_x = speed * pygame.math.Vector2(1, 0).rotate_rad(angle).x
        self.vel_y = speed * pygame.math.Vector2(1, 0).rotate_rad(angle).y
        self.color = (255, 215, 0)  # Gold
        self.size = random.randint(1, 3)
        self.gravity = 0
        self.lifetime = 40
        self.max_lifetime = 40
    
    def _init_coin_particle(self, **kwargs):
        """Initialize yellow coin bounce particle."""
        import random
        self.vel_x = random.uniform(-1, 1)
        self.vel_y = random.uniform(-6, -3)
        self.color = (255, 255, 0)  # Yellow
        self.size = 4
        self.gravity = 0.3
        self.lifetime = 35
        self.max_lifetime = 35
    
    def update(self):
        """Update particle position and properties."""
        self.x += self.vel_x
        self.y += self.vel_y
        
        # Apply gravity if particle type uses it
        if hasattr(self, 'gravity'):
            self.vel_y += self.gravity
        
        # Special behaviors for specific particle types
        if self.particle_type == self.TYPE_GLOW:
            # Glow particles slowly expand and contract
            phase = (self.max_lifetime - self.lifetime) / self.max_lifetime
            self.size = max(1, int(3 * (1 + 0.5 * pygame.math.Vector2(1, 0).rotate_rad(phase * 12.56).y)))
        
        self.lifetime -= 1
        return self.lifetime > 0
    
    def draw(self, screen, camera):
        """Draw particle with alpha blending based on lifetime."""
        if self.lifetime <= 0:
            return
            
        screen_x, screen_y = camera.get_screen_pos(self.x, self.y)
        
        # Calculate alpha for fade effect
        alpha = self.lifetime / self.max_lifetime
        
        # Adjust color based on alpha for fade effect
        r, g, b = self.color
        fade_color = (
            max(0, min(255, int(r * alpha))),
            max(0, min(255, int(g * alpha))),  
            max(0, min(255, int(b * alpha)))
        )
        
        # Draw particle based on type
        if self.particle_type == self.TYPE_GLOW:
            # Draw glow particle with multiple layers for glow effect
            for i in range(3):
                layer_size = max(1, self.size - i)
                layer_alpha = alpha * (0.8 - i * 0.2)
                layer_color = (
                    max(0, min(255, int(r * layer_alpha))),
                    max(0, min(255, int(g * layer_alpha))),
                    max(0, min(255, int(b * layer_alpha)))
                )
                if layer_size > 0:
                    pygame.draw.circle(screen, layer_color, (int(screen_x), int(screen_y)), layer_size)
        else:
            # Standard particle drawing
            size = max(1, int(self.size * alpha))
            pygame.draw.circle(screen, fade_color, (int(screen_x), int(screen_y)), size)

class Hazard:
    """
    Spike hazard that damages Karel on contact.
    
    Features:
    - Red triangular spikes
    - Strategic placement on platforms
    - Collision detection with Karel
    - Triggers death and respawn
    """
    
    def __init__(self, x, y):
        """Initialize hazard at given position."""
        self.x = x
        self.y = y
        self.width = HAZARD_SIZE
        self.height = HAZARD_SIZE
        self.rect = pygame.Rect(x, y, self.width, self.height)
    
    def check_collision(self, karel_rect):
        """Check if Karel is touching this hazard."""
        return karel_rect.colliderect(self.rect)
    
    def draw(self, screen):
        """Draw hazard as red triangular spikes."""
        # Draw three triangular spikes
        spike_width = self.width // 3
        for i in range(3):
            spike_x = self.x + i * spike_width
            spike_points = [
                (spike_x, self.y + self.height),              # Bottom left
                (spike_x + spike_width, self.y + self.height), # Bottom right
                (spike_x + spike_width // 2, self.y)          # Top center
            ]
            pygame.draw.polygon(screen, HAZARD_COLOR, spike_points)
            pygame.draw.polygon(screen, BLACK, spike_points, 1)  # Black outline

class Staircase:
    """
    Simple solid staircase made of individual platform steps.
    
    Features:
    - Each step is a solid platform rectangle
    - No gaps or collision issues
    - Uses standard platform collision system
    - Reliable step-by-step movement
    """
    
    def __init__(self, start_x, start_y, step_width, step_height, num_steps):
        """Initialize staircase as individual platform steps."""
        self.start_x = start_x
        self.start_y = start_y
        self.step_width = step_width
        self.step_height = step_height
        self.num_steps = num_steps
        
        # Create individual platform objects for each step
        self.step_platforms = []
        for i in range(num_steps):
            step_x = start_x + i * step_width
            step_y = start_y - (i + 1) * step_height
            # Each step is a solid platform from its top to the ground
            step_platform = Platform(step_x, step_y, step_width, (i + 1) * step_height + GROUND_HEIGHT)
            self.step_platforms.append(step_platform)
    
    def get_platforms(self):
        """Return list of platform objects for collision detection."""
        return self.step_platforms
    
    def draw(self, screen, camera):
        """Draw the staircase as individual platform steps."""
        for platform in self.step_platforms:
            if camera.is_visible(platform.x, platform.y, platform.width, platform.height):
                screen_x, screen_y = camera.get_screen_pos(platform.x, platform.y)
                screen_rect = pygame.Rect(screen_x, screen_y, platform.width, platform.height)
                pygame.draw.rect(screen, GROUND_GREEN, screen_rect)

class Flagpole:
    """
    Dynamic goal flag that changes height and color based on beeper collection.
    
    Features:
    - Height varies based on beeper collection percentage
    - Color transitions from red (0%) to rainbow (100%)
    - Clear 'GOAL' text label
    - Positioned at level end for clear target
    """
    
    def __init__(self):
        """Initialize flagpole at end position."""
        self.pole_x = 3180  # FLAGPOLE_X (positioned after stairs at 3165)
        self.pole_width = 12  # FLAGPOLE_WIDTH (slightly thicker)
        self.base_height = 280  # FLAGPOLE_BASE_HEIGHT (much taller like Mario)
        self.reached = False
        
        # Calculate pole position (extends from ground up)
        self.pole_y = GROUND_LEVEL - self.base_height
        self.pole_rect = pygame.Rect(self.pole_x, self.pole_y, self.pole_width, self.base_height)
        
        # Glow effect properties
        self.glow_timer = 0
    
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
        Calculate flag position on pole based on beeper collection.
        Higher percentage = flag higher on pole
        """
        # Flag moves from bottom 25% to top 10% of pole
        min_height_ratio = 0.75  # Flag at 75% down pole (25% from bottom)
        max_height_ratio = 0.1   # Flag at 10% down pole (90% from bottom)
        height_ratio = min_height_ratio - (min_height_ratio - max_height_ratio) * beeper_percentage
        return self.pole_y + int(self.base_height * height_ratio)
    
    def check_victory(self, karel):
        """
        Check if Karel has reached the flagpole or flag.
        """
        if self.reached:
            return False
        
        karel_rect = pygame.Rect(karel.x, karel.y, karel.width, karel.height)
        
        # Check collision with pole
        if karel_rect.colliderect(self.pole_rect):
            self.reached = True
            print("🎉 FLAGPOLE VICTORY! Level Complete!")
            return True
        
        return False
    
    def update(self):
        """Update flagpole glow animation."""
        self.glow_timer += 1
    
    def should_generate_glow(self):
        """Check if glow particles should be generated this frame."""
        return self.glow_timer % 8 == 0  # Generate glow particles every 8 frames
    
    def get_glow_positions(self):
        """Get positions around the flagpole for glow particles."""
        glow_positions = []
        center_x = self.pole_x + self.pole_width // 2
        center_y = self.pole_y + self.base_height // 2
        
        # Generate positions in a circle around the flagpole
        import random
        for _ in range(2):  # 2 glow particles per generation
            angle = random.uniform(0, 6.28)  # 2*pi
            radius = random.uniform(25, 45)
            glow_x = center_x + radius * pygame.math.Vector2(1, 0).rotate_rad(angle).x
            glow_y = center_y + radius * pygame.math.Vector2(1, 0).rotate_rad(angle).y
            glow_positions.append((glow_x, glow_y))
        
        return glow_positions
    
    def draw(self, screen, beeper_percentage):
        """Draw flagpole with dynamic flag position and color."""
        # Draw pole (brown/wooden color)
        pole_color = (139, 69, 19)  # Brown
        pygame.draw.rect(screen, pole_color, self.pole_rect)
        pygame.draw.rect(screen, BLACK, self.pole_rect, 2)  # Black outline
        
        # Calculate flag properties
        flag_color = self.get_flag_color(beeper_percentage)
        flag_y = self.get_flag_height(beeper_percentage)
        
        # Draw flag (attached to right side of pole)
        flag_x = self.pole_x + self.pole_width
        flag_rect = pygame.Rect(flag_x, flag_y, 30, 20)  # FLAG_WIDTH, FLAG_HEIGHT
        pygame.draw.rect(screen, flag_color, flag_rect)
        pygame.draw.rect(screen, BLACK, flag_rect, 2)  # Black border
        
        # Draw flag pattern (triangle)
        flag_points = [
            (flag_x, flag_y),
            (flag_x + 30, flag_y + 10),  # FLAG_WIDTH, FLAG_HEIGHT // 2
            (flag_x, flag_y + 20)  # FLAG_HEIGHT
        ]
        pygame.draw.polygon(screen, flag_color, flag_points)
        pygame.draw.polygon(screen, BLACK, flag_points, 2)

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
        
        # Animation variables
        self.facing_right = True
        self.walking = False
        self.walk_timer = 0
        self.idle_timer = 0
        
        # Create rectangle for collision detection
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
    
    def move_left(self, walls):
        """Move Karel left while respecting boundaries and walls."""
        # Save original position
        original_x = self.x
        
        # Try to move left
        self.x -= self.speed
        self.rect.x = self.x
        
        # Update animation state
        self.facing_right = False
        self.walking = True
        
        # Check boundary collision
        if self.x < 0:
            self.x = 0
            self.rect.x = self.x
            self.walking = False
            return
        
        # Check wall collisions
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                # Collision detected - revert movement
                self.x = original_x
                self.rect.x = self.x
                self.walking = False
                return
    
    def move_right(self, walls):
        """Move Karel right while respecting boundaries and walls."""
        # Save original position
        original_x = self.x
        
        # Try to move right
        self.x += self.speed
        self.rect.x = self.x
        
        # Update animation state
        self.facing_right = True
        self.walking = True
        
        # Check world boundary collision (can move to edge of world)
        if self.x > WORLD_WIDTH - self.width:
            self.x = WORLD_WIDTH - self.width
            self.rect.x = self.x
            self.walking = False
            return
        
        # Check wall collisions
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                # Collision detected - revert movement
                self.x = original_x
                self.rect.x = self.x
                self.walking = False
                return
    
    def jump(self):
        """Make Karel jump if on ground."""
        if self.on_ground:
            self.velocity_y = JUMP_VELOCITY
            self.on_ground = False
            return True  # Signal that jump occurred for sound
        return False
    
    def apply_gravity(self):
        """Apply gravity physics to Karel."""
        if not self.on_ground:
            # Apply gravity
            self.velocity_y += GRAVITY
            
            # Limit to terminal velocity
            if self.velocity_y > TERMINAL_VELOCITY:
                self.velocity_y = TERMINAL_VELOCITY
    
    def check_platform_collision(self, platforms, walls, staircase=None):
        """
        Check if Karel is colliding with any platform, wall, or staircase.
        Handles both top and bottom collisions with proper edge case handling.
        Walls act as platforms for landing but also block movement.
        Ground gaps allow Karel to fall through.
        Returns True if Karel just landed (for dust effects).
        """
        karel_bottom = self.y + self.height
        karel_top = self.y
        was_on_ground = self.on_ground
        self.on_ground = False
        karel_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        landed = False
        
        # Combine platforms, walls, and staircase platforms for collision detection
        all_obstacles = list(platforms) + list(walls)
        if staircase:
            all_obstacles.extend(staircase.get_platforms())
        
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
                    
                    # Check if Karel just landed (for dust effects)
                    if not was_on_ground and self.velocity_y >= 3:  # Only create dust for significant falls
                        landed = True
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
        return landed
    
    def update(self, keys_pressed, platforms, walls, staircase=None):
        """Update Karel's position based on keyboard input, physics, and obstacles.
        Returns tuple: (death, landed, jumped) for game state updates."""
        # Reset walking state
        self.walking = False
        
        # Handle horizontal movement with error checking
        try:
            if keys_pressed[pygame.K_LEFT]:
                self.move_left(walls)
            if keys_pressed[pygame.K_RIGHT]:
                self.move_right(walls)
        except (IndexError, TypeError):
            # Handle edge case where keys_pressed might be invalid
            pass
        
        # Update walk animation timer
        if self.walking:
            self.walk_timer += 1
            self.idle_timer = 0  # Reset idle timer when walking
        else:
            self.walk_timer = 0
            self.idle_timer += 1  # Increment idle timer when not walking
        
        # Handle jumping with error checking
        jumped = False
        try:
            if keys_pressed[pygame.K_SPACE]:
                jumped = self.jump()
        except (IndexError, TypeError):
            pass
        
        # Apply physics
        self.apply_gravity()
        
        # Update vertical position
        self.y += self.velocity_y
        
        # Check platform, wall, and staircase collision
        landed = self.check_platform_collision(platforms, walls, staircase)
        
        # Update collision rectangle (moved before death check)
        self.rect.x = self.x
        self.rect.y = self.y
        
        # Check if Karel fell into a gap (below screen)
        if self.y > DEATH_THRESHOLD:
            return True, False, False  # Signal death, no landing, no jump
        
        return False, landed, jumped
    
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
        self.karel_image = None
        self.score = 0
        self.game_won = False
        self.win_timer = 0
        self.particles = []
        self.screen_shake = 0
        self.camera_shake_x = 0
        self.camera_shake_y = 0
        
        # Performance monitoring
        self.frame_count = 0
        
        # Lives system
        self.lives = STARTING_LIVES
        self.game_over = False
        self.invincible = False
        self.invincibility_timer = 0
        self.respawn_timer = 0
        self.respawning = False
        
        # Instructions screen
        self.show_instructions = True  # Start with instructions showing
        self.game_paused = True        # Start paused
        self.game_started = False      # Track if game has started
        
        # Death effect system
        self.death_flash = False
        self.death_flash_timer = 0
        self.death_flash_duration = 10  # Red flash for 10 frames
        self.karel_white = False
        self.karel_white_timer = 0
        self.karel_white_duration = 30  # Karel white for 30 frames
        
        # Sound system
        self.sound_manager = SoundManager()
        
        # Initialize pygame with error handling
        if not self._initialize_pygame():
            sys.exit(1)
        
        # Load background image (optional)
        self._load_background_image()
        
        # Load Karel image (optional)
        self._load_karel_image()
        
        # Create camera system
        self.camera = Camera()
        
        # Create Karel character
        self.karel = Karel(KAREL_START_X, KAREL_START_Y)
        
        # Start background music
        self.sound_manager.play_background_music()
        
        # Load extended level data
        self._create_level_data()
        
        # Create hazards
        self._create_hazards()
        
        # Create solid staircase 
        self.staircase = Staircase(
            start_x=2800,           # Start after ground platform ends
            start_y=GROUND_LEVEL,   # Start at ground level
            step_width=60,          # Each step 60px wide
            step_height=32,         # Each step 32px high
            num_steps=6             # 6 steps total
        )
        
        # Create flagpole at level end (after stairs)
        self.flagpole = Flagpole()
        
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
    
    def _load_karel_image(self):
        """
        Load Karel character image if available.
        Falls back to blue rectangle if image not found.
        """
        try:
            self.karel_image = pygame.image.load(KAREL_IMAGE_PATH)
            # Scale to Karel size
            if self.karel_image.get_size() != (KAREL_SIZE, KAREL_SIZE):
                self.karel_image = pygame.transform.scale(
                    self.karel_image, (KAREL_SIZE, KAREL_SIZE))
            print(f"Karel image loaded successfully: {KAREL_IMAGE_PATH}")
        except (pygame.error, FileNotFoundError):
            # Karel image not found - use blue rectangle
            self.karel_image = None
            print(f"Karel image not found, using blue rectangle placeholder")
    
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
            Platform(2600, GROUND_LEVEL, 200, GROUND_HEIGHT),     # Gap 6: 2400-2600 (200px gap), ground 2600-2800
            
            # Ground platform under flagpole (after staircase at 2800+60*6=3160)
            Platform(3160, GROUND_LEVEL, 140, GROUND_HEIGHT),         # Extended ground under flagpole (3160-3300)
            
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
            
            # Final section platforms (2400-2600px only - clear area for stairs/flagpole)
            Platform(2500, 220, 80, 20),    # Final challenge platform
        ]
        
        # No walls - clean platforming focus
        self.walls = []
        
        # Balanced beepers for score (optional but rewarding)
        self.beepers = [
            # Early section - easy collection for confidence building
            Beeper(150, GROUND_LEVEL - 20),          # Ground start - easy
            Beeper(250, 400 - 25),                   # Platform 1 - safe
            Beeper(520, 240 - 25),                   # Higher platform - moderate
            Beeper(670, 160 - 25),                   # High platform - skillful
            
            # Mid section - risk/reward balance
            Beeper(850, 350 - 25),                   # Landing platform - safe
            Beeper(1100, 280 - 25),                  # Away from hazard - balanced
            Beeper(1300, 200 - 25),                  # High route - optional
            
            # Advanced section - higher difficulty
            Beeper(1750, 240 - 25),                  # Precision platform
            Beeper(2100, 160 - 25),                  # High skill platform
            Beeper(3200, GROUND_LEVEL - 25),         # Pre-victory reward (after staircase)
        ]
    
    def _create_hazards(self):
        """Create spike hazards at strategic locations."""
        self.hazards = [
            # Balanced hazard placement for progressive difficulty
            Hazard(400, 400 - HAZARD_SIZE),          # Platform 1 - tutorial hazard
            Hazard(1200, 280 - HAZARD_SIZE),         # Mid platform - skill test
            Hazard(1500, 320 - HAZARD_SIZE),         # Rest platform - avoidable danger
            Hazard(2400, 220 - HAZARD_SIZE),         # Final challenge platform
            Hazard(2700, GROUND_LEVEL - HAZARD_SIZE), # Pre-stairs warning
        ]
    
    def _check_beeper_obstacle_collision(self, beeper_x, beeper_y):
        """
        Check if a beeper position conflicts with any wall, platform, or staircase.
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
        
        # Check collision with staircase platforms
        if hasattr(self, 'staircase') and self.staircase:
            for stair_platform in self.staircase.get_platforms():
                # Check if beeper center is inside staircase platform
                if (beeper_x >= stair_platform.x and beeper_x <= stair_platform.x + stair_platform.width and
                    beeper_y >= stair_platform.y and beeper_y <= stair_platform.y + stair_platform.height):
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
                    # Make sure it's still within world bounds and not conflicting
                    if (0 <= new_x <= WORLD_WIDTH and 
                        not self._check_beeper_obstacle_collision(new_x, beeper.y)):
                        beeper.x = new_x
                        beeper.base_y = beeper.y  # Update base position for bobbing
                        print(f"🔧 Moved beeper from ({original_x}, {original_y}) to ({beeper.x}, {beeper.y})")
                        break
                else:
                    # If horizontal movement doesn't work, try vertical adjustment
                    for y_offset in [-30, 30]:
                        new_y = original_y + y_offset
                        if (new_y > 0 and new_y < WINDOW_HEIGHT and
                            not self._check_beeper_obstacle_collision(beeper.x, new_y)):
                            beeper.y = new_y
                            beeper.base_y = beeper.y  # Update base position for bobbing
                            print(f"🔧 Moved beeper from ({original_x}, {original_y}) to ({beeper.x}, {beeper.y})")
                            break
        
        if conflicts_resolved > 0:
            print(f"🔧 Resolved {conflicts_resolved} beeper collision conflicts")
    
    def handle_events(self):
        """
        Process all pygame events.
        Handle window close events and basic input.
        """
        for event in pygame.event.get():
            # Handle window close button
            if event.type == pygame.QUIT:
                self.running = False
            
            # Handle ESC key to quit, R key to restart, M key to mute, and I key for instructions
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_r:
                    if (self.game_won and self.win_timer <= 60) or self.game_over:
                        # Restart game
                        self.restart_game()
                elif event.key == pygame.K_m:
                    # Toggle mute
                    muted = self.sound_manager.toggle_mute()
                    mute_status = "ON" if muted else "OFF"
                    print(f"🔇 Mute: {mute_status}")
                elif event.key == pygame.K_i:
                    # Toggle instructions screen
                    self.show_instructions = not self.show_instructions
                    self.game_paused = self.show_instructions
                    if not self.show_instructions:
                        self.game_started = True  # Mark game as started when instructions are closed
                    print(f"📖 Instructions: {'ON' if self.show_instructions else 'OFF'}")
    
    def update(self):
        """
        Update game logic with comprehensive error checking.
        Handle Karel movement, physics, collisions, and all game systems.
        """
        # Don't update Karel if game is won, game over, or instructions are showing
        if not self.game_won and not self.game_over and not self.game_paused:
            # Handle respawn timer
            if self.respawning:
                self.respawn_timer -= 1
                if self.respawn_timer <= 0:
                    self._respawn_karel()
                return
            
            # Get currently pressed keys for smooth movement with error handling
            try:
                keys_pressed = pygame.key.get_pressed()
            except pygame.error:
                # Fallback if key state cannot be retrieved
                keys_pressed = [False] * 512
            
            # Update Karel's position based on input, platforms, and walls
            try:
                karel_died, karel_landed, karel_jumped = self.karel.update(keys_pressed, self.platforms, self.walls, self.staircase)
                
                # Play jump sound
                if karel_jumped:
                    self.sound_manager.play_sound('jump')
                
                # Check if Karel died
                if karel_died:
                    self._karel_died()
                    return
                
                # Create dust particles if Karel just landed
                if karel_landed:
                    try:
                        # Create dust puff at Karel's feet
                        dust_x = self.karel.x + self.karel.width // 2
                        dust_y = self.karel.y + self.karel.height
                        for _ in range(4):  # Create 4 dust particles
                            self.particles.append(Particle(dust_x, dust_y, Particle.TYPE_DUST))
                    except Exception as e:
                        print(f"WARNING: Dust particle creation error - {e}")
                        
            except Exception as e:
                print(f"WARNING: Karel update error - {e}")
                return
            
            # Check hazard collisions (only if not invincible)
            if not self.invincible and hasattr(self, 'hazards'):
                try:
                    karel_rect = pygame.Rect(self.karel.x, self.karel.y, self.karel.width, self.karel.height)
                    for hazard in self.hazards:
                        if hazard.check_collision(karel_rect):
                            self._karel_died()
                            return
                except Exception as e:
                    print(f"WARNING: Hazard collision error - {e}")
            
            # Update invincibility timer
            if self.invincible:
                self.invincibility_timer -= 1
                if self.invincibility_timer <= 0:
                    self.invincible = False
        
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
        
        # Update death effects
        if self.death_flash_timer > 0:
            self.death_flash_timer -= 1
            if self.death_flash_timer <= 0:
                self.death_flash = False
        
        if self.karel_white_timer > 0:
            self.karel_white_timer -= 1
            if self.karel_white_timer <= 0:
                self.karel_white = False
        
        # Update beeper animations and check collection with particle effects
        try:
            for beeper in self.beepers:
                # Update beeper animation (bobbing and collection jump)
                beeper.update()
                
                # Check if collection animation just started
                if beeper.check_collection(self.karel):
                    # Play beeper collection sound
                    self.sound_manager.play_sound('beep')
                    
                    # Create coin particles when collection starts
                    try:
                        for _ in range(PARTICLE_COUNT):
                            self.particles.append(Particle(beeper.x, beeper.y, Particle.TYPE_COIN))
                    except Exception as e:
                        print(f"WARNING: Particle creation error - {e}")
                
                # Award points when beeper is fully collected (animation complete)
                if beeper.is_fully_collected() and beeper.points > 0:
                    self.score += beeper.points
                    beeper.points = 0  # Prevent double scoring
                    
        except Exception as e:
            print(f"WARNING: Beeper collection error - {e}")
        
        # Update particles with performance optimization
        self.particles = [p for p in self.particles if p.update()]
        
        # Limit particles to maximum for performance
        if len(self.particles) > MAX_PARTICLES:
            # Remove oldest particles (keep newest particles up to limit)
            self.particles = self.particles[-MAX_PARTICLES:]
        
        # Update flagpole (glow particles disabled as they were too much)
        if hasattr(self, 'flagpole'):
            try:
                self.flagpole.update()
                # Glow particles removed - they were too distracting
            except Exception as e:
                print(f"WARNING: Flagpole update error - {e}")
        
        # Check victory condition - jump to the flagpole!
        if not self.game_won and hasattr(self, 'flagpole'):
            try:
                if self.flagpole.check_victory(self.karel):
                    # Play victory sound
                    self.sound_manager.play_sound('victory')
                    
                    self.game_won = True
                    self.win_timer = WIN_SCREEN_DURATION
                    print(f"🎉 VICTORY! Final Score: {self.score}")
            except Exception as e:
                print(f"WARNING: Victory check error - {e}")
        
        # Update win screen timer
        if self.game_won and self.win_timer > 0:
            self.win_timer -= 1
    
    def _karel_died(self):
        """Handle Karel's death - reduce lives and start respawn with visual effects."""
        self.lives -= 1
        self.screen_shake = SHAKE_DURATION
        
        # Play death sound
        self.sound_manager.play_sound('death')
        
        # Trigger death effects
        self.death_flash = True
        self.death_flash_timer = self.death_flash_duration
        self.karel_white = True
        self.karel_white_timer = self.karel_white_duration
        
        if self.lives <= 0:
            # Game over
            self.game_over = True
            print("💀 GAME OVER! Press R to restart.")
        else:
            # Start respawn process
            self.respawning = True
            self.respawn_timer = RESPAWN_DELAY
            print(f"💔 Karel died! Lives remaining: {self.lives}")
    
    def _respawn_karel(self):
        """Respawn Karel at safe position near current camera view with invincibility."""
        # Find a safe respawn position on current screen or nearby
        respawn_x = max(50, self.camera.x + 50)  # Left edge of screen + buffer
        respawn_y = KAREL_START_Y
        
        # Make sure respawn position is on solid ground
        for platform in self.platforms:
            if (respawn_x >= platform.x and respawn_x <= platform.x + platform.width and
                platform.y <= GROUND_LEVEL):
                respawn_y = platform.y - KAREL_SIZE
                break
        
        # Set Karel's new position
        self.karel.x = respawn_x
        self.karel.y = respawn_y
        self.karel.velocity_y = 0
        self.karel.on_ground = False
        
        # Grant invincibility
        self.invincible = True
        self.invincibility_timer = INVINCIBILITY_DURATION
        
        # End respawning state
        self.respawning = False
        
        print(f"✨ Karel respawned with invincibility at ({respawn_x}, {respawn_y})!")
    
    def draw_grid(self):
        """Draw Karel's signature grid background with plus signs."""
        # Calculate grid range based on camera position
        start_x = int(self.camera.x // GRID_SIZE) * GRID_SIZE
        end_x = start_x + WINDOW_WIDTH + GRID_SIZE
        
        # Draw plus signs at grid intersections (camera-relative)
        # Start 35px from bottom, then every 70px
        for world_x in range(start_x, end_x + 1, GRID_SIZE):
            for world_y in range(WINDOW_HEIGHT - 35, -1, -GRID_SIZE):
                screen_x, screen_y = self.camera.get_screen_pos(world_x, world_y)
                
                # Only draw if on screen
                if 0 <= screen_x <= WINDOW_WIDTH:
                    # Draw plus sign at each intersection
                    plus_size = 3
                    # Horizontal line of plus (2 pixels thick)
                    pygame.draw.line(self.screen, GRID_COLOR, 
                                   (screen_x - plus_size, screen_y), (screen_x + plus_size, screen_y), 2)
                    # Vertical line of plus (2 pixels thick)
                    pygame.draw.line(self.screen, GRID_COLOR, 
                                   (screen_x, screen_y - plus_size), (screen_x, screen_y + plus_size), 2)
    
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
        
        # Draw staircase
        if self.staircase:
            self.staircase.draw(self.screen, self.camera)
        
        # Draw hazards (red spikes) with screen shake
        for hazard in self.hazards:
            if self.camera.is_visible(hazard.x, hazard.y, hazard.width, hazard.height):
                screen_x, screen_y = self.camera.get_screen_pos(hazard.x, hazard.y, self.camera_shake_x, self.camera_shake_y)
                
                # Draw red triangular spikes
                spike_width = hazard.width // 3
                for i in range(3):
                    spike_x = screen_x + i * spike_width
                    spike_points = [
                        (spike_x, screen_y + hazard.height),              # Bottom left
                        (spike_x + spike_width, screen_y + hazard.height), # Bottom right
                        (spike_x + spike_width // 2, screen_y)            # Top center
                    ]
                    pygame.draw.polygon(self.screen, HAZARD_COLOR, spike_points)
                    pygame.draw.polygon(self.screen, BLACK, spike_points, 1)  # Black outline
        
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
        
        # Draw flagpole (if visible)
        if self.camera.is_visible(self.flagpole.pole_x, self.flagpole.pole_y, 12 + 30, 280):  # FLAGPOLE_WIDTH + FLAG_WIDTH, FLAGPOLE_BASE_HEIGHT
            screen_x, screen_y = self.camera.get_screen_pos(self.flagpole.pole_x, self.flagpole.pole_y, self.camera_shake_x, self.camera_shake_y)
            
            # Calculate beeper percentage
            beepers_collected = sum(1 for b in self.beepers if b.collected)
            total_beepers = len(self.beepers)
            beeper_percentage = beepers_collected / total_beepers if total_beepers > 0 else 0
            
            # Draw pole
            pole_color = (139, 69, 19)  # Brown
            pole_rect = pygame.Rect(screen_x, screen_y, 12, 280)  # FLAGPOLE_WIDTH, FLAGPOLE_BASE_HEIGHT
            pygame.draw.rect(self.screen, pole_color, pole_rect)
            pygame.draw.rect(self.screen, BLACK, pole_rect, 2)
            
            # Draw flag with dynamic properties and gentle wave motion
            flag_color = self.flagpole.get_flag_color(beeper_percentage)
            flag_height_offset = self.flagpole.get_flag_height(beeper_percentage) - self.flagpole.pole_y
            flag_screen_y = screen_y + flag_height_offset
            flag_screen_x = screen_x + 12  # FLAGPOLE_WIDTH
            
            # Add gentle wave motion to flag
            wave_offset = 2 * pygame.math.Vector2(1, 0).rotate_rad(self.flagpole.glow_timer * 0.15).y
            
            flag_rect = pygame.Rect(flag_screen_x + wave_offset, flag_screen_y, 30, 20)  # FLAG_WIDTH, FLAG_HEIGHT
            pygame.draw.rect(self.screen, flag_color, flag_rect)
            pygame.draw.rect(self.screen, BLACK, flag_rect, 2)
            
            # Draw flag triangle with wave motion
            flag_points = [
                (flag_screen_x + wave_offset, flag_screen_y),
                (flag_screen_x + 30 + wave_offset, flag_screen_y + 10),  # FLAG_WIDTH, FLAG_HEIGHT // 2
                (flag_screen_x + wave_offset, flag_screen_y + 20)  # FLAG_HEIGHT
            ]
            pygame.draw.polygon(self.screen, flag_color, flag_points)
            pygame.draw.polygon(self.screen, BLACK, flag_points, 2)
        
        # Draw particles
        for particle in self.particles:
            particle.draw(self.screen, self.camera)
        
        # Draw Karel character with screen shake and animation
        screen_x, screen_y = self.camera.get_screen_pos(self.karel.x, self.karel.y, self.camera_shake_x, self.camera_shake_y)
        
        # Add walking bob animation (alternating between 2 frames)
        bob_offset = 0
        if self.karel.walking:
            # Create alternating 2-frame walking animation every 6 frames
            walk_frame = (self.karel.walk_timer // 6) % 2
            if walk_frame == 0:
                bob_offset = -3  # Frame 1: Karel lifted up slightly
            else:
                bob_offset = 1   # Frame 2: Karel lowered slightly (step down)
        # No idle animation - removed as it looked odd
        
        final_y = screen_y + bob_offset
        
        # Use Karel image if available, otherwise blue rectangle
        if self.karel_image:
            # Flip image based on direction
            karel_surface = self.karel_image
            if not self.karel.facing_right:
                karel_surface = pygame.transform.flip(self.karel_image, True, False)
            
            # Apply white effect if Karel is in death state
            if self.karel_white:
                # Create white version of Karel sprite
                karel_surface = karel_surface.copy()
                karel_surface.fill((255, 255, 255), special_flags=pygame.BLEND_MULT)
            
            self.screen.blit(karel_surface, (screen_x, final_y))
        else:
            # Fallback to blue rectangle with 'K'
            screen_rect = pygame.Rect(screen_x, final_y, self.karel.width, self.karel.height)
            
            # Use white color if Karel is in death state
            karel_color = WHITE if self.karel_white else KAREL_BLUE
            pygame.draw.rect(self.screen, karel_color, screen_rect)
            
            # Draw Karel's 'K' text
            try:
                font = pygame.font.Font(None, 36)  # Bigger font for bigger Karel
                text_color = BLACK if self.karel_white else WHITE
                k_text = font.render('K', True, text_color)
                text_rect = k_text.get_rect(center=(screen_x + self.karel.width//2, final_y + self.karel.height//2))
                self.screen.blit(k_text, text_rect)
            except pygame.error:
                pass
        
        # Draw UI elements
        try:
            # Enhanced score and progress display in top-left corner
            score_font = pygame.font.Font(None, 34)  # Even larger font for accessibility
            beepers_collected = sum(1 for b in self.beepers if b.collected)
            total_beepers = len(self.beepers)
            score_text = score_font.render(f"Score: {self.score}  |  Beepers: {beepers_collected}/{total_beepers}", True, UI_TEXT_DARK)
            
            # High contrast background for better readability
            score_bg = pygame.Surface((score_text.get_width() + 24, score_text.get_height() + 12))
            score_bg.fill(UI_BACKGROUND)
            pygame.draw.rect(score_bg, UI_TEXT_DARK, (0, 0, score_bg.get_width(), score_bg.get_height()), 2)
            self.screen.blit(score_bg, (8, 8))
            self.screen.blit(score_text, (20, 14))
            
            # Enhanced lives display in top-right corner with accessible design
            lives_font = pygame.font.Font(None, 34)  # Larger font for accessibility
            # Use text-based hearts for better accessibility
            hearts_filled = "♥" * self.lives
            hearts_empty = "♡" * (STARTING_LIVES - self.lives)
            lives_text = lives_font.render(f"Lives: {hearts_filled}{hearts_empty}", True, ERROR_RED if self.lives <= 1 else UI_TEXT_DARK)
            
            # High contrast background
            lives_bg = pygame.Surface((lives_text.get_width() + 24, lives_text.get_height() + 12))
            lives_bg.fill(UI_BACKGROUND)
            pygame.draw.rect(lives_bg, UI_TEXT_DARK, (0, 0, lives_bg.get_width(), lives_bg.get_height()), 2)
            lives_rect = lives_bg.get_rect(topright=(WINDOW_WIDTH - 8, 8))
            self.screen.blit(lives_bg, lives_rect)
            
            lives_text_rect = lives_text.get_rect(topright=(WINDOW_WIDTH - 20, 14))
            self.screen.blit(lives_text, lives_text_rect)
            
            # Victory message only when won - enhanced with better positioning
            if self.game_won:
                # Main victory message
                title_font = pygame.font.Font(None, 48)  # Larger font
                title_text = title_font.render("🎉 VICTORY! Code Quest Complete! 🎉", True, (0, 150, 0))  # Green color
                
                # Add white background for better contrast
                title_bg = pygame.Surface((title_text.get_width() + 30, title_text.get_height() + 15))
                title_bg.set_alpha(200)
                title_bg.fill((255, 255, 255))
                title_bg_rect = title_bg.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 50))
                self.screen.blit(title_bg, title_bg_rect)
                
                title_rect = title_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 50))
                self.screen.blit(title_text, title_rect)
                
                # Add completion message
                subtitle_font = pygame.font.Font(None, 28)
                subtitle_text = subtitle_font.render(f"Final Score: {self.score}  |  Beepers Collected: {beepers_collected}/{total_beepers}", True, BLACK)
                subtitle_rect = subtitle_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 10))
                self.screen.blit(subtitle_text, subtitle_rect)
            
            # Enhanced game state messages
            if self.game_over:
                # Game over screen - enhanced
                overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
                overlay.set_alpha(180)
                overlay.fill((200, 0, 0))  # Red overlay
                self.screen.blit(overlay, (0, 0))
                
                game_over_font = pygame.font.Font(None, 64)  # Much larger
                game_over_text = game_over_font.render("💀 GAME OVER! 💀", True, WHITE)
                game_over_rect = game_over_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 40))
                self.screen.blit(game_over_text, game_over_rect)
                
                instruction_font = pygame.font.Font(None, 32)
                instruction_text = instruction_font.render("Press R to Restart  |  Press I for Instructions", True, WHITE)
                instruction_rect = instruction_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 20))
                self.screen.blit(instruction_text, instruction_rect)
                
            elif self.game_won and self.win_timer > 0:
                # Win screen display - already enhanced above
                if self.win_timer < 60:  # Last second
                    restart_font = pygame.font.Font(None, 24)
                    restart_text = restart_font.render("Press R to Restart  |  Press I for Instructions", True, BLACK)
                    restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 30))
                    self.screen.blit(restart_text, restart_rect)
                    
            elif self.respawning:
                # Respawning message - enhanced
                overlay = pygame.Surface((WINDOW_WIDTH, 50))
                overlay.set_alpha(150)
                overlay.fill((255, 255, 0))  # Yellow overlay
                self.screen.blit(overlay, (0, WINDOW_HEIGHT//2 - 25))
                
                instruction_font = pygame.font.Font(None, 32)
                instruction_text = instruction_font.render(f"⏳ Respawning... Lives Remaining: {self.lives}", True, BLACK)
                instruction_rect = instruction_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
                self.screen.blit(instruction_text, instruction_rect)
                
            elif self.invincible:
                # Invincibility message - enhanced
                flash_alpha = int(128 + 127 * pygame.math.Vector2(1, 0).rotate_rad(self.invincibility_timer * 0.2).y)
                overlay = pygame.Surface((WINDOW_WIDTH, 40))
                overlay.set_alpha(flash_alpha)
                overlay.fill((255, 215, 0))  # Gold overlay
                self.screen.blit(overlay, (0, WINDOW_HEIGHT - 80))
                
                instruction_font = pygame.font.Font(None, 28)
                instruction_text = instruction_font.render("✨ INVINCIBLE! ✨ Temporary protection from spikes!", True, BLACK)
                instruction_rect = instruction_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT - 60))
                self.screen.blit(instruction_text, instruction_rect)
                
            else:
                # Normal gameplay instructions - high contrast
                instruction_bg = pygame.Surface((WINDOW_WIDTH, 35))
                instruction_bg.fill(UI_BACKGROUND)
                pygame.draw.line(instruction_bg, UI_TEXT_DARK, (0, 0), (WINDOW_WIDTH, 0), 2)
                self.screen.blit(instruction_bg, (0, WINDOW_HEIGHT - 35))
                
                instruction_font = pygame.font.Font(None, 24)  # Larger for accessibility
                instruction_text = instruction_font.render("← → : Move  |  SPACE: Jump  |  I: Instructions  |  M: Mute  |  Collect Beepers, Reach GOAL!", True, UI_TEXT_DARK)
                instruction_rect = instruction_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT - 18))
                self.screen.blit(instruction_text, instruction_rect)
            
        except pygame.error as e:
            print(f"WARNING: Text rendering error - {e}")
        
        # Draw death flash overlay (red screen flash)
        if self.death_flash:
            flash_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            flash_surface.set_alpha(128)  # Semi-transparent
            flash_surface.fill((255, 0, 0))  # Red color
            self.screen.blit(flash_surface, (0, 0))
        
        # Draw instructions screen overlay if active
        if self.show_instructions:
            self.draw_instructions_screen()
        
        # Update display
        pygame.display.flip()
    
    def draw_instructions_screen(self):
        """
        Draw comprehensive instructions screen overlay.
        Covers controls, objective, and CIP branding.
        """
        # Semi-transparent dark overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(220)
        overlay.fill((0, 0, 50))  # Dark blue
        self.screen.blit(overlay, (0, 0))
        
        # Main instruction panel
        panel_width = 500
        panel_height = 400
        panel_x = (WINDOW_WIDTH - panel_width) // 2
        panel_y = (WINDOW_HEIGHT - panel_height) // 2
        
        # Panel background
        panel_bg = pygame.Surface((panel_width, panel_height))
        panel_bg.fill((240, 240, 240))  # Light gray
        pygame.draw.rect(panel_bg, (0, 0, 0), (0, 0, panel_width, panel_height), 3)
        self.screen.blit(panel_bg, (panel_x, panel_y))
        
        # Title
        title_font = pygame.font.Font(None, INSTRUCTION_TITLE_SIZE)
        title_text = title_font.render("🤖 KAREL'S CODE QUEST", True, (0, 100, 200))
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH//2, panel_y + 30))
        self.screen.blit(title_text, title_rect)
        
        # Stanford CIP branding
        brand_font = pygame.font.Font(None, INSTRUCTION_SMALL_SIZE)
        brand_text = brand_font.render("Stanford CIP Final Project", True, (150, 0, 0))
        brand_rect = brand_text.get_rect(center=(WINDOW_WIDTH//2, panel_y + 55))
        self.screen.blit(brand_text, brand_rect)
        
        # Instructions content
        instruction_font = pygame.font.Font(None, INSTRUCTION_FONT_SIZE)
        small_font = pygame.font.Font(None, 22)
        
        # Controls section
        y_offset = panel_y + 90
        controls_title = instruction_font.render("🎮 CONTROLS:", True, (0, 0, 0))
        self.screen.blit(controls_title, (panel_x + 20, y_offset))
        
        controls = [
            "← → Arrow Keys: Move Karel left and right",
            "SPACEBAR: Jump (only when on ground)", 
            "R: Restart game (when game over or victory)",
            "I: Toggle this instructions screen",
            "M: Mute/unmute sounds",
            "ESC: Quit game"
        ]
        
        for i, control in enumerate(controls):
            control_text = small_font.render(control, True, (50, 50, 50))
            self.screen.blit(control_text, (panel_x + 30, y_offset + 25 + i * 20))
        
        # Objective section
        y_offset += 160
        objective_title = instruction_font.render("🎯 OBJECTIVE:", True, (0, 0, 0))
        self.screen.blit(objective_title, (panel_x + 20, y_offset))
        
        objective_text = small_font.render("Collect all beepers, then reach the GOAL flagpole!", True, (0, 100, 0))
        self.screen.blit(objective_text, (panel_x + 30, y_offset + 25))
        
        # Karel world references with high contrast
        y_offset += 65
        karel_title = instruction_font.render("🏗️ KAREL'S WORLD:", True, UI_TEXT_DARK)
        self.screen.blit(karel_title, (panel_x + 20, y_offset))
        
        karel_refs = [
            "• Navigate through Karel's grid-based platformer world",
            "• Avoid red spike hazards that cost you lives",
            "• Use your programming logic to solve jumping puzzles"
        ]
        
        for i, ref in enumerate(karel_refs):
            ref_text = small_font.render(ref, True, UI_TEXT_DARK)
            self.screen.blit(ref_text, (panel_x + 30, y_offset + 28 + i * 22))
        
        # Close instruction with high contrast
        close_font = pygame.font.Font(None, 26)  # Slightly larger for accessibility
        if not self.game_started:
            close_text = close_font.render("Press I to start your Code Quest adventure!", True, SUCCESS_GREEN)
        else:
            close_text = close_font.render("Press I again to close instructions and resume game", True, WARNING_ORANGE)
        close_rect = close_text.get_rect(center=(WINDOW_WIDTH//2, panel_y + panel_height - 20))
        self.screen.blit(close_text, close_rect)
    
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
        
        # Reset lives system
        self.lives = STARTING_LIVES
        self.game_over = False
        self.invincible = False
        self.invincibility_timer = 0
        self.respawn_timer = 0
        self.respawning = False
        
        # Reset death effects
        self.death_flash = False
        self.death_flash_timer = 0
        self.karel_white = False
        self.karel_white_timer = 0
        
        # Reset Karel
        self.karel = Karel(KAREL_START_X, KAREL_START_Y)
        
        # Reset camera
        self.camera = Camera()
        
        # Reset beepers completely
        for beeper in self.beepers:
            beeper.collected = False
            beeper.collecting = False
            beeper.collection_timer = 0
            beeper.bob_timer = 0
            beeper.jump_velocity = 0
            beeper.y = beeper.base_y  # Reset to original position
            beeper.points = BEEPER_POINTS  # Reset points for scoring
        
        # Reset staircase
        self.staircase = Staircase(
            start_x=2800,           
            start_y=GROUND_LEVEL,   
            step_width=60,          
            step_height=32,         
            num_steps=6             
        )
        
        # Reset flagpole
        self.flagpole = Flagpole()
        
        # Reset instruction screen
        self.show_instructions = False
        self.game_paused = False
        self.game_started = True  # Keep game started after restart
    
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
    Creates and runs the game instance with comprehensive error handling.
    """
    try:
        print("\n" + "=" * 60)
        print("🤖 KAREL'S CODE QUEST - FINAL PROJECT")
        print("Stanford Computer Science CIP Program")
        print("Programming Meets Platforming Adventure")
        print("=" * 60)
        print("✨ FEATURES: Instructions Screen, Enhanced UI, Professional Polish")
        print("🎯 OBJECTIVE: Collect all beepers, then reach the GOAL flagpole!")
        print("🎮 CONTROLS: Arrow Keys + Spacebar, I for Instructions, R to restart")
        print("🎓 Made with Karel's programming principles in mind")
        print("=" * 60 + "\n")
        
        # Create and run the game
        game = KarelGame()
        game.run()
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        print("Please check pygame installation and dependencies.")
        return 1
    
    print("\n✅ Game session ended successfully. Thanks for playing!")
    return 0

# Run the game when script is executed directly
if __name__ == "__main__":
    main()