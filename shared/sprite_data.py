"""
QommandahQeen Sprite Data
Complete sprite sheet mappings for all game assets.
All character/enemy sprites use 128x128 grid cells!
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class SpriteLayer(Enum):
    """Render layers for sprite ordering."""
    BACKGROUND = 0
    TILES = 1
    ENTITIES = 2
    PROJECTILES = 3
    COLLECTIBLES = 4
    POWERUPS = 5
    PLAYER = 6
    SMOKE_OVERLAY = 7
    UI = 10


@dataclass
class FrameSpec:
    """Specification for a single animation frame."""
    x: int
    y: int
    width: int
    height: int
    duration: float = 0.1


@dataclass
class AnimationSpec:
    """Complete animation specification."""
    name: str
    row: int
    frames: int
    start_col: int
    fps: int
    frame_width: int
    frame_height: int
    loop: bool = True
    note: str = ""


@dataclass
class SpriteSheetSpec:
    """Complete sprite sheet specification."""
    name: str
    filename: str
    tile_width: int
    tile_height: int
    animations: Dict[str, AnimationSpec] = field(default_factory=dict)


# =============================================================================
# PLAYER BASE SPRITE: qq-qommandah-qeen.png (1024x512 = 8x4 grid of 128x128)
# =============================================================================
QOMMANDAH_QEEN_FRAMES = {
    "idle": AnimationSpec("idle", 0, 4, 0, 6, 128, 128, True, "Standing idle"),
    "run": AnimationSpec("run", 1, 8, 0, 12, 128, 128, True, "Run cycle"),
    "jump": AnimationSpec("jump", 2, 3, 0, 8, 128, 128, False, "Jump arc"),
    "fall": AnimationSpec("fall", 2, 2, 3, 6, 128, 128, True, "Falling"),
    "shoot": AnimationSpec("shoot", 3, 2, 0, 10, 128, 128, False, "Shooting"),
    "hurt": AnimationSpec("hurt", 3, 2, 2, 8, 128, 128, False, "Taking damage"),
    "dead": AnimationSpec("dead", 3, 4, 4, 6, 128, 128, False, "Death sequence"),
}

QOMMANDAH_QEEN_HITBOX = {"width": 48, "height": 64, "offset_x": 40, "offset_y": 48}

# =============================================================================
# SMOKE OVERLAY: qq-qeen-smoqin.png (512x256 = 4x2 grid of 128x128)
# =============================================================================
SMOQIN_FRAMES = {
    "smoke_idle": AnimationSpec("smoke_idle", 0, 4, 0, 4, 128, 128, True, "Smoke forming"),
    "smoke_q_ring": AnimationSpec("smoke_q_ring", 1, 4, 0, 3, 128, 128, False, "Q-shaped ring!"),
}

SMOQIN_CONFIG = {
    "always_active": True,
    "overlay_offset_x": 0,
    "overlay_offset_y": -20,
    "cycle_duration_ms": 4000,
    "plays_during_states": ["idle", "run", "pogo_idle", "jetpack_idle"],
    "disabled_during_states": ["hurt", "dead", "shoot"],
}

# =============================================================================
# JUMPUPSTIQ: qq-qeen-jumpupstiq.png (1024x512 = 8x4 grid of 128x128)
# =============================================================================
JUMPUPSTIQ_PICKUP_FRAMES = {
    "idle": AnimationSpec("idle", 0, 4, 0, 6, 64, 64, True, "Pickup item"),
}

QOMMANDAH_QEEN_JUMPUPSTIQ_FRAMES = {
    "pogo_idle": AnimationSpec("pogo_idle", 0, 8, 0, 8, 128, 128, True, "Pogo idle"),
    "pogo_bounce": AnimationSpec("pogo_bounce", 2, 8, 0, 12, 128, 128, True, "Bouncing"),
    "pogo_land": AnimationSpec("pogo_land", 3, 4, 0, 10, 128, 128, False, "Landing"),
}

JUMPUPSTIQ_PHYSICS = {
    "jump_strength": -1400, "normal_bounce": -900, "continuous_bounce": True,
    "hold_for_higher": True, "max_hold_bonus": 300, "gravity_modifier": 0.9,
    "particle_colors": [(0, 255, 100), (200, 0, 255), (255, 150, 0)],
}

# =============================================================================
# JETTPAQ: qq-qeen-jetpaq.png (1024x512 = 8x4 grid of 128x128)
# =============================================================================
JETTPAQ_PICKUP_FRAMES = {
    "idle": AnimationSpec("idle", 0, 4, 0, 6, 64, 64, True, "Pickup item"),
}

QOMMANDAH_QEEN_JETTPAQ_FRAMES = {
    "jetpack_idle": AnimationSpec("jetpack_idle", 0, 8, 0, 6, 128, 128, True, "With jetpack"),
    "jetpack_thrust": AnimationSpec("jetpack_thrust", 2, 8, 0, 15, 128, 128, True, "Thrusting"),
    "jetpack_hover": AnimationSpec("jetpack_hover", 3, 4, 0, 8, 128, 128, True, "Hovering"),
}

JETTPAQ_PHYSICS = {
    "thrust_force": -1800, "hover_gravity": 0.3, "fuel_max": 100,
    "fuel_consumption": 25, "fuel_regen": 15, "fuel_regen_grounded_only": True,
}

# =============================================================================
# ENEMY SPRITES (All use 128x128 grid cells)
# =============================================================================

# WalqerBot: qq-walqer-bot.png (512x512 = 4x4 grid of 128x128)
WALQER_BOT_FRAMES = {
    "idle": AnimationSpec("idle", 0, 2, 0, 4, 128, 128, True, "Standing"),
    "walk": AnimationSpec("walk", 0, 4, 0, 8, 128, 128, True, "Patrolling"),
    "shoot": AnimationSpec("shoot", 1, 4, 0, 10, 128, 128, False, "Shooting"),
    "hurt": AnimationSpec("hurt", 2, 2, 0, 8, 128, 128, False, "Hit"),
    "dead": AnimationSpec("dead", 2, 4, 0, 6, 128, 128, False, "Death"),
}

# JumperDrqne: qq-jumper-drqne.png (1024x256 = 8x2 grid of 128x128)
JUMPER_DRQNE_FRAMES = {
    "idle": AnimationSpec("idle", 0, 4, 0, 6, 128, 128, True, "Hovering"),
    "fly": AnimationSpec("fly", 0, 8, 0, 10, 128, 128, True, "Flying"),
    "dead": AnimationSpec("dead", 1, 8, 0, 8, 128, 128, False, "Exploding"),
}

# QortanaHalo: qq-qortana-halo.png (512x384 = 4x3 grid of 128x128)
QORTANA_HALO_FRAMES = {
    "idle": AnimationSpec("idle", 0, 4, 0, 6, 128, 128, True, "Floating"),
    "charge": AnimationSpec("charge", 1, 4, 0, 8, 128, 128, False, "Charging"),
    "dead": AnimationSpec("dead", 2, 4, 0, 6, 128, 128, False, "Death"),
}

# Qlippy: qq-annoying-qlippy.png (1024x256 = 8x2 grid of 128x128)
QLIPPY_FRAMES = {
    "idle": AnimationSpec("idle", 0, 8, 0, 4, 128, 128, True, "Annoying idle"),
    "popup": AnimationSpec("popup", 1, 8, 0, 6, 128, 128, True, "Popup attack"),
}

# BriQBeaver: qq-briq-beaver.png (1024x512 = 8x4 grid of 128x128)
BRIQ_BEAVER_FRAMES = {
    "idle": AnimationSpec("idle", 0, 4, 0, 4, 128, 128, True, "Standing"),
    "walk": AnimationSpec("walk", 0, 8, 0, 8, 128, 128, True, "Walking"),
    "throw": AnimationSpec("throw", 1, 4, 0, 10, 128, 128, False, "Throwing briQ!"),
    "hurt": AnimationSpec("hurt", 2, 2, 0, 8, 128, 128, False, "Hit"),
    "dead": AnimationSpec("dead", 2, 4, 4, 6, 128, 128, False, "Death"),
}

# HoverSquid: qq-hover-squid.png (512x256 = 4x2 grid of 128x128)
HOVER_SQUID_FRAMES = {
    "idle": AnimationSpec("idle", 0, 4, 0, 6, 128, 128, True, "Hovering"),
    "attack": AnimationSpec("attack", 1, 4, 0, 10, 128, 128, False, "Attacking"),
}

# =============================================================================
# PROJECTILES: qq-bullets-explosions.png (512x768 = 8x12 grid of 64x64)
# =============================================================================
PROJECTILE_FRAMES = {
    "bullet_green": AnimationSpec("bullet_green", 0, 4, 0, 15, 64, 64, True, "Player bullet"),
    "bullet_purple": AnimationSpec("bullet_purple", 1, 4, 0, 15, 64, 64, True, "Enemy bullet"),
    "impact_green": AnimationSpec("impact_green", 2, 4, 0, 20, 64, 64, False, "Green splat"),
    "impact_purple": AnimationSpec("impact_purple", 3, 4, 0, 20, 64, 64, False, "Purple burst"),
    "explosion_big": AnimationSpec("explosion_big", 4, 4, 0, 12, 64, 64, False, "Big explosion"),
}

# =============================================================================
# COLLECTIBLES: qq-items-collectibles.png (512x128 = 8x2 grid of 64x64)
# =============================================================================
COLLECTIBLE_FRAMES = {
    "chip": AnimationSpec("chip", 0, 4, 0, 6, 64, 64, True, "Chip collectible"),
    "floppy": AnimationSpec("floppy", 0, 4, 4, 6, 64, 64, True, "Floppy disk"),
    "medallion": AnimationSpec("medallion", 1, 4, 0, 6, 64, 64, True, "Medallion"),
    "key": AnimationSpec("key", 1, 4, 4, 6, 64, 64, True, "Key"),
}

# =============================================================================
# UI ICONS: qq-ui-icons.png (768x512 = 12x8 grid of 64x64)
# =============================================================================
UI_ICONS = {
    "health": [
        {"name": "heart", "row": 0, "col": 0, "width": 64, "height": 64},
        {"name": "shield", "row": 0, "col": 1, "width": 64, "height": 64},
        {"name": "biohazard", "row": 0, "col": 2, "width": 64, "height": 64},
    ],
    "score": [
        {"name": "chip_green", "row": 1, "col": 0, "width": 64, "height": 64, "value": 100},
        {"name": "floppy_purple", "row": 1, "col": 1, "width": 64, "height": 64, "value": 500},
        {"name": "medallion", "row": 1, "col": 2, "width": 64, "height": 64, "value": 1000},
        {"name": "key_orange", "row": 1, "col": 3, "width": 64, "height": 64},
    ],
    "modes": [
        {"name": "mode_lowg", "row": 2, "col": 0, "width": 64, "height": 64, "mode": "low_g"},
        {"name": "mode_glitch", "row": 2, "col": 1, "width": 64, "height": 64, "mode": "glitch"},
        {"name": "mode_speedy", "row": 2, "col": 2, "width": 64, "height": 64, "mode": "speedy_boots"},
        {"name": "mode_mirror", "row": 2, "col": 3, "width": 64, "height": 64, "mode": "mirror"},
        {"name": "mode_bullettime", "row": 2, "col": 4, "width": 64, "height": 64, "mode": "bullet_time"},
        {"name": "mode_junglist", "row": 2, "col": 5, "width": 64, "height": 64, "mode": "junglist"},
    ],
}

# =============================================================================
# SPRITE REGISTRY
# =============================================================================
SPRITE_REGISTRY: Dict[str, Dict[str, AnimationSpec]] = {
    "player": QOMMANDAH_QEEN_FRAMES,
    "player_smoqin": SMOQIN_FRAMES,
    "player_jumpupstiq": QOMMANDAH_QEEN_JUMPUPSTIQ_FRAMES,
    "player_jettpaq": QOMMANDAH_QEEN_JETTPAQ_FRAMES,
    "pickup_jumpupstiq": JUMPUPSTIQ_PICKUP_FRAMES,
    "pickup_jettpaq": JETTPAQ_PICKUP_FRAMES,
    "walqer_bot": WALQER_BOT_FRAMES,
    "jumper_drqne": JUMPER_DRQNE_FRAMES,
    "qortana_halo": QORTANA_HALO_FRAMES,
    "qlippy": QLIPPY_FRAMES,
    "briq_beaver": BRIQ_BEAVER_FRAMES,
    "hover_squid": HOVER_SQUID_FRAMES,
    "projectiles": PROJECTILE_FRAMES,
    "collectibles": COLLECTIBLE_FRAMES,
}


def get_sprite_spec(sprite_name: str) -> Optional[SpriteSheetSpec]:
    """Retrieve sprite specification by name."""
    from shared.constants import ASSET_FILES
    
    animations = SPRITE_REGISTRY.get(sprite_name, {})
    first_anim = next(iter(animations.values())) if animations else None
    
    return SpriteSheetSpec(
        name=sprite_name,
        filename=ASSET_FILES.get(sprite_name, f"{sprite_name}.png"),
        tile_width=first_anim.frame_width if first_anim else 128,
        tile_height=first_anim.frame_height if first_anim else 128,
        animations=animations
    )


def get_animation_spec(sprite_name: str, animation_name: str) -> Optional[AnimationSpec]:
    """Retrieve animation specification for a sprite."""
    return SPRITE_REGISTRY.get(sprite_name, {}).get(animation_name)


def get_frame_spec(sprite_name: str, animation_name: str, frame_index: int) -> FrameSpec:
    """Retrieve specific frame specification."""
    anim = get_animation_spec(sprite_name, animation_name)
    if anim and 0 <= frame_index < anim.frames:
        col = anim.start_col + frame_index
        return FrameSpec(
            x=col * anim.frame_width,
            y=anim.row * anim.frame_height,
            width=anim.frame_width,
            height=anim.frame_height,
            duration=1.0 / anim.fps
        )
    return FrameSpec(0, 0, 128, 128, 0.1)


def validate_sprite_registry() -> List[str]:
    """Validate all sprite specifications."""
    errors = []
    from shared.constants import ASSET_FILES
    for key in SPRITE_REGISTRY:
        if key not in ASSET_FILES:
            errors.append(f"Missing asset mapping: {key}")
    return errors
