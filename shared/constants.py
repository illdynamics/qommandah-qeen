"""
QommandahQeen Core Constants
ALL VALUES MUST BE INTEGERS for authentic Commander Keen physics!
"""

import pygame
import os

# =============================================================================
# DISPLAY CONFIGURATION
# =============================================================================
INTERNAL_WIDTH = 320
INTERNAL_HEIGHT = 200
DISPLAY_SCALE = 4
SCREEN_WIDTH = INTERNAL_WIDTH * DISPLAY_SCALE  # 1280
SCREEN_HEIGHT = INTERNAL_HEIGHT * DISPLAY_SCALE  # 800
TILE_SIZE = 32

# =============================================================================
# INTEGER PHYSICS - THE CRITICAL SYSTEM!
# 1 pixel = 256 sub-pixel units for smooth movement
# =============================================================================
SUBPIXEL_SCALE = 256
TILE_SIZE_SUBPIXEL = TILE_SIZE * SUBPIXEL_SCALE  # 8192

# Gravity and physics (in sub-pixel units per second squared)
GRAVITY = 2400  # ~9.4 pixels/s²
PLAYER_JUMP_FORCE = -1200  # Negative = upward
PLAYER_MOVE_SPEED = 768  # ~3 pixels/frame at 60fps
PLAYER_ACCELERATION = 1000  # ~3.9 pixels/frame at 60fps
PLAYER_TERMINAL_VELOCITY = 1536  # ~6 pixels/frame
FRICTION = 200  # Ground friction

# =============================================================================
# TIMING
# =============================================================================
TARGET_FPS = 60
FIXED_TIMESTEP = 1.0 / 60.0

# Projectile constants
PROJECTILE_SPEED = 500
PROJECTILE_DAMAGE = 10
PROJECTILE_LIFETIME = 3.0
PROJECTILE_SIZE = 8
PROJECTILE_COLOR = (255, 255, 0)

# Layer constants
LAYER_BACKGROUND = 0
LAYER_TILES = 1
LAYER_ENTITIES = 2
LAYER_PROJECTILES = 3
LAYER_COLLECTIBLES = 4
LAYER_POWERUPS = 5
LAYER_UI = 10

# Hazard constants
HAZARD_DAMAGE = 20
HAZARD_SPIKE_DAMAGE = 30
HAZARD_ACID_DAMAGE = 10
HAZARD_LASER_DAMAGE = 40
HAZARD_SPIKE_COLOR = (255, 0, 0)
HAZARD_ACID_COLOR = (0, 255, 0)
HAZARD_LASER_COLOR = (255, 255, 0)
HAZARD_SPIKE_WIDTH = 32
HAZARD_SPIKE_HEIGHT = 32
HAZARD_ACID_WIDTH = 64
HAZARD_ACID_HEIGHT = 32
HAZARD_LASER_WIDTH = 320
HAZARD_LASER_HEIGHT = 8
HAZARD_ANIMATION_SPEED = 2.0
HAZARD_BLINK_INTERVAL = 0.5
HAZARD_LASER_CYCLE_TIME = 3.0

# Powerup constants
POWERUP_DURATION = 10.0
POWERUP_ANIMATION_SPEED = 1.5
POWERUP_BOB_SPEED = 2.0
POWERUP_BOB_HEIGHT = 5.0

# Collectible constants
COLLECTIBLE_CHIP = 100
COLLECTIBLE_FLOPPY = 500
COLLECTIBLE_MEDALLION = 1000
COLLECTIBLE_SCORE_VALUES = {
    "chip": 100,
    "floppy": 500,
    "medallion": 1000
}
COLLECTIBLE_ANIMATION_SPEED = 1.0
COLLECTIBLE_BOB_SPEED = 1.5
COLLECTIBLE_BOB_HEIGHT = 3.0

# Enemy constants
ENEMY_WALQER_HEALTH = 50
ENEMY_WALQER_DAMAGE = 10
ENEMY_WALQER_SPEED = 80
ENEMY_WALQER_DETECTION_RANGE = 200
ENEMY_WALQER_ATTACK_RANGE = 150
ENEMY_WALQER_ATTACK_COOLDOWN = 1.5
ENEMY_WALQER_PROJECTILE_SPEED = 300

ENEMY_JUMPER_HEALTH = 60
ENEMY_JUMPER_DAMAGE = 15
ENEMY_JUMPER_SPEED = 60
ENEMY_JUMPER_JUMP_FORCE = 350
ENEMY_JUMPER_JUMP_INTERVAL = 2.0
ENEMY_JUMPER_DETECTION_RANGE = 180
ENEMY_JUMPER_ATTACK_RANGE = 50

ENEMY_BRIQ_BEAVER_HEALTH = 80
ENEMY_BRIQ_BEAVER_DAMAGE = 20
ENEMY_BRIQ_BEAVER_SPEED = 70
ENEMY_BRIQ_BEAVER_DETECTION_RANGE = 220
ENEMY_BRIQ_BEAVER_ATTACK_RANGE = 200
ENEMY_BRIQ_BEAVER_THROW_COOLDOWN = 2.0
ENEMY_BRIQ_BEAVER_THROW_WINDUP = 0.5
ENEMY_BRIQ_BEAVER_PROJECTILE_SPEED = 200
ENEMY_BRIQ_BEAVER_PROJECTILE_GRAVITY = 300
ENEMY_BRIQ_BEAVER_PROJECTILE_DAMAGE = 15
ENEMY_BRIQ_BEAVER_PROJECTILE_RANGE = 300

# Jettpaq constants
JETTPAQ_DASH_SPEED = 600
JETTPAQ_DASH_DURATION = 0.3
JETTPAQ_COOLDOWN = 1.0
JETTPAQ_FUEL_MAX = 100.0
JETTPAQ_FUEL_CONSUMPTION_RATE = 20.0
JETTPAQ_FUEL_RECHARGE_RATE = 10.0
JETTPAQ_FUEL_RECHARGE_DELAY = 1.0

# Jumpupstiq constants
JUMPUPSTIQ_BOUNCE_FORCE = 350
JUMPUPSTIQ_BASS_BLAST_FORCE = 500
JUMPUPSTIQ_BASS_BLAST_RADIUS = 100
JUMPUPSTIQ_BOUNCE_DAMPING = 0.8
JUMPUPSTIQ_HORIZONTAL_BOOST = 1.5

# HUD constants
HUD_HEIGHT = 60
HUD_MARGIN = 10
HUD_FONT_SIZE = 18
HUD_TEXT_COLOR = (255, 255, 255)
HUD_BG_COLOR = (0, 0, 0, 128)
HUD_ICON_SIZE = 24
HUD_FUEL_BAR_WIDTH = 100
HUD_FUEL_BAR_HEIGHT = 8
HUD_FUEL_FULL_COLOR = (0, 255, 0)
HUD_FUEL_LOW_COLOR = (255, 0, 0)
HUD_SCORE_LABEL = "SCORE:"
HUD_FUEL_LABEL = "FUEL:"
HUD_MODES_LABEL = "MODES:"
HUD_PLAYER_STATE_LABEL = "STATE:"
HUD_HEALTH_BAR_WIDTH = 100
HUD_HEALTH_BAR_HEIGHT = 8
HUD_HEALTH_FULL_COLOR = (0, 255, 0)
HUD_HEALTH_LOW_COLOR = (255, 0, 0)

# Door constants
DOOR_CLOSED = 0
DOOR_OPEN = 1
DOOR_UNLOCKED = 2
DOOR_LOCKED = 3

# Exit zone constants
EXIT_ZONE_COLOR = (0, 255, 0, 100)

# Asset paths
ASSETS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
SPRITE_SIZE = 128  # Main character/enemy sprite cell size
TILE_SPRITE_SIZE = 64  # Tileset cell size
ANIMATION_FPS = 10

# =============================================================================
# ASSET FILE REGISTRY - All sprite files (UPDATED FOR FIXED ASSETS!)
# =============================================================================
ASSET_FILES = {
    # Player sprites (128x128 grid cells)
    "player": "qq-qommandah-qeen.png",              # 1024x512 = 8x4 grid
    "player_smoqin": "qq-qeen-smoqin.png",          # 512x256 = 4x2 grid
    "player_jumpupstiq": "qq-qeen-jumpupstiq.png",  # 1024x512 = 8x4 grid
    "player_jettpaq": "qq-qeen-jetpaq.png",         # 1024x512 = 8x4 grid
    
    # Powerup pickup items (64x64 cells in these sheets)
    "pickup_jumpupstiq": "qq-bonus-powerups.png",   # 256x128 = 4x2 grid
    "pickup_jettpaq": "qq-bonus-powerups.png",      # Same sheet, different frame
    "collectibles": "qq-items-collectibles.png",    # 512x128 = 8x2 grid
    
    # Enemy sprites (128x128 grid cells)
    "walqer_bot": "qq-walqer-bot.png",              # 512x512 = 4x4 grid
    "jumper_drqne": "qq-jumper-drqne.png",          # 1024x256 = 8x2 grid
    "qortana_halo": "qq-qortana-halo.png",          # 512x384 = 4x3 grid
    "qlippy": "qq-annoying-qlippy.png",             # 1024x256 = 8x2 grid
    "briq_beaver": "qq-briq-beaver.png",            # 1024x512 = 8x4 grid
    "hover_squid": "qq-hover-squid.png",            # 512x256 = 4x2 grid
    
    # Effects & tiles
    "projectiles": "qq-bullets-explosions.png",     # 512x768
    "tilesets": "qq-objects-tilesets.png",          # 512x512 = 8x8 grid (64x64 tiles)
    "ui_icons": "qq-ui-icons.png",                  # 768x512
    
    # Backgrounds
    "background1": "qq-background1.png",
    "background2": "qq-background2.png",
    "background3": "qq-background3.png",
    "background4": "qq-background4.png",
    "main_menu_background": "qq-main-menu.png",
}

# Sprite sheet configurations (filename -> (cell_width, cell_height, cols, rows))
SPRITE_CONFIGS = {
    "qq-qommandah-qeen.png": (128, 128, 8, 4),
    "qq-qeen-jetpaq.png": (128, 128, 8, 4),
    "qq-qeen-jumpupstiq.png": (128, 128, 8, 4),
    "qq-qeen-smoqin.png": (128, 128, 4, 2),
    "qq-walqer-bot.png": (128, 128, 4, 4),
    "qq-briq-beaver.png": (128, 128, 8, 4),
    "qq-jumper-drqne.png": (128, 128, 8, 2),
    "qq-annoying-qlippy.png": (128, 128, 8, 2),
    "qq-qortana-halo.png": (128, 128, 4, 3),
    "qq-hover-squid.png": (128, 128, 4, 2),
    "qq-objects-tilesets.png": (64, 64, 8, 8),
    "qq-items-collectibles.png": (64, 64, 8, 2),
    "qq-bonus-powerups.png": (64, 64, 4, 2),
    "qq-bullets-explosions.png": (64, 64, 8, 12),
    "qq-ui-icons.png": (64, 64, 12, 8),
}

# Colors
COLORS = {
    "black": (0, 0, 0),
    "white": (255, 255, 255),
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "yellow": (255, 255, 0),
    "cyan": (0, 255, 255),
    "magenta": (255, 0, 255)
}

# =============================================================================
# PARTICLE CONSTANTS
# =============================================================================
class ParticleConstants:
    # Smoke
    SMOKE_EMISSION_RATE = 20
    SMOKE_MIN_SPEED = 10
    SMOKE_MAX_SPEED = 30
    SMOKE_RISE_SPEED = 20
    SMOKE_COLOR = (128, 128, 128)
    SMOKE_MIN_SIZE = 2
    SMOKE_MAX_SIZE = 5
    SMOKE_MIN_LIFETIME = 0.5
    SMOKE_MAX_LIFETIME = 1.5
    SMOKE_GRAVITY = -10

    # Explosion
    EXPLOSION_PARTICLE_COUNT = 50
    EXPLOSION_MIN_SPEED = 50
    EXPLOSION_MAX_SPEED = 200
    EXPLOSION_COLORS = [(255, 128, 0), (255, 0, 0), (255, 255, 0), (200, 200, 200)]
    EXPLOSION_MIN_SIZE = 2
    EXPLOSION_MAX_SIZE = 6
    EXPLOSION_MIN_LIFETIME = 0.5
    EXPLOSION_MAX_LIFETIME = 1.2
    EXPLOSION_GRAVITY = 100
