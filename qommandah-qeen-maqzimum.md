# 🎮 Project QommandahQeen MAQZIMUM - The Complete WoNQ Platformer Engine

> **THE DEFINITIVE BUILD SPECIFICATION**
> Vorticons-Inspired Engine Revival via QonQrete AgentiQ OrQhestration
> Mode: program | Providers: deepseek-chat / gemini-2.5-flash
> **Configuration: b2c12 (sens=2, cycles=12)**

---

## 📊 TASQLEVELER METADATA

```yaml
# ═══════════════════════════════════════════════════════════════════════════════
# TASQLEVELER v1.0 - Pre-analyzed Task Specification
# This tasq has been pre-processed by TasqLeveler for optimal QonQrete execution
# ═══════════════════════════════════════════════════════════════════════════════

tasqleveler:
  version: "1.0"
  analyzed_at: "2024-12-30T00:00:00Z"
  tasq_id: "qommandah-qeen-maqzimum"
  
  # ─────────────────────────────────────────────────────────────────────────────
  # OVERALL COMPLEXITY ASSESSMENT
  # ─────────────────────────────────────────────────────────────────────────────
  complexity:
    level: "ENTERPRISE"           # SIMPLE | MODERATE | COMPLEX | ENTERPRISE
    score: 8.5                    # 1-10 scale
    confidence: 0.92              # Analysis confidence
    rationale: |
      - 70+ files across 8 packages
      - Complex state machine (3 player modes)
      - Integer-only physics system
      - 6 unique enemy AI behaviors
      - 6 WoNQmodes with hook system
      - Full game loop with UI/scenes
    
  # ─────────────────────────────────────────────────────────────────────────────
  # ESTIMATED METRICS
  # ─────────────────────────────────────────────────────────────────────────────
  estimates:
    total_files: 72
    total_lines_of_code: 8500
    total_briqs_min: 240
    total_briqs_max: 360
    recommended_cycles: 12
    recommended_sensitivity: 2
    estimated_tokens: 85000
    
  # ─────────────────────────────────────────────────────────────────────────────
  # TECHNOLOGY STACK
  # ─────────────────────────────────────────────────────────────────────────────
  stack:
    language: "python"
    version: "3.10+"
    framework: "pygame-ce"
    patterns:
      - "State Machine"
      - "Entity Component"
      - "Observer (hooks)"
      - "Factory (enemies)"
      - "Strategy (WoNQmodes)"
    dependencies:
      - "pygame-ce>=2.4.0"
    
  # ─────────────────────────────────────────────────────────────────────────────
  # CRITICAL PATH ITEMS (must be precise - INSTRUQTOR PRIORITY!)
  # ─────────────────────────────────────────────────────────────────────────────
  critical_paths:
    - id: "CP001"
      name: "PHYSICS_INTEGER"
      description: "All physics must use INTEGER math only - NO FLOATS for positions/velocities"
      priority: "CRITICAL"
      validation: "assert isinstance(pos_x, int) and isinstance(vel_y, int)"
      affects: ["world/physics.py", "actors/player.py", "actors/enemies/*"]
      
    - id: "CP002"
      name: "SPRITE_COORDINATES"
      description: "Frame extraction must match exact coordinates from sprite_data.py"
      priority: "CRITICAL"
      validation: "Frame dimensions match documented values"
      affects: ["core/resources.py", "shared/sprite_data.py"]
      
    - id: "CP003"
      name: "STATE_MACHINE"
      description: "Player state transitions must correctly switch sprite sheets"
      priority: "HIGH"
      validation: "Powerup collect/lose changes active sprite sheet"
      affects: ["actors/player.py", "actors/player_states/*"]
      
    - id: "CP004"
      name: "SMOKE_OVERLAY"
      description: "Smoke must render ON TOP of player sprite as separate layer"
      priority: "HIGH"
      validation: "Overlay draws AFTER player sprite in render order"
      affects: ["actors/smoke_overlay.py", "actors/player.py"]
      
    - id: "CP005"
      name: "POGO_BOUNCE"
      description: "JumpUpStiQ MUST auto-bounce on ground contact - continuous!"
      priority: "HIGH"
      validation: "on_ground=True triggers automatic jump, no stop condition"
      affects: ["actors/player_states/jumpupstiq_state.py"]
      
    - id: "CP006"
      name: "JETPACK_FUEL"
      description: "JettPaQ fuel depletes during thrust, regenerates when grounded"
      priority: "HIGH"
      validation: "Fuel gauge decreases while thrusting, increases when on ground"
      affects: ["actors/player_states/jettpaq_state.py", "ui/hud.py"]

  # ─────────────────────────────────────────────────────────────────────────────
  # PHASE BREAKDOWN WITH BRIQS (INSTRUQTOR PLANNING GUIDE)
  # ─────────────────────────────────────────────────────────────────────────────
  phases:
    - id: 1
      name: "Foundation"
      cycles: [1, 2]
      briqs_estimate: [25, 35]
      priority: "P0"
      complexity: "MODERATE"
      dependencies: []
      deliverables:
        - path: "shared/__init__.py"
          briqs: 1
        - path: "shared/constants.py"
          briqs: 4
          critical: true
          notes: "ALL values must be integers!"
        - path: "shared/types.py"
          briqs: 5
          notes: "Vec2i, Rect, PlayerState, PowerupType, EnemyState enums"
        - path: "shared/exceptions.py"
          briqs: 2
        - path: "shared/sprite_data.py"
          briqs: 15
          critical: true
          notes: "ALL 18 sprite file mappings with exact coordinates!"
        - path: "shared/powerup_data.py"
          briqs: 4
        - path: "shared/wonqmode_data.py"
          briqs: 4
      
    - id: 2
      name: "Core Engine"
      cycles: [3, 4]
      briqs_estimate: [30, 40]
      priority: "P0"
      complexity: "MODERATE"
      dependencies: ["phase_1"]
      deliverables:
        - path: "core/__init__.py"
          briqs: 1
        - path: "core/engine.py"
          briqs: 8
          notes: "Fixed-timestep loop, scene manager"
        - path: "core/scene.py"
          briqs: 4
        - path: "core/resources.py"
          briqs: 10
          critical: true
          notes: "SpriteSheet parser, Animation class - must match sprite_data.py"
        - path: "core/input.py"
          briqs: 5
        - path: "core/time.py"
          briqs: 3
        - path: "core/camera.py"
          briqs: 6
        - path: "core/particles.py"
          briqs: 5
      
    - id: 3
      name: "World & Physics"
      cycles: [5, 6]
      briqs_estimate: [35, 45]
      priority: "P0"
      complexity: "COMPLEX"
      dependencies: ["phase_1", "phase_2"]
      critical_notes:
        - "⚠️ INTEGER MATH ONLY - NO FLOATS FOR POSITIONS!"
        - "⚠️ Slide collision resolution required (not stop/stick)"
        - "⚠️ Sub-pixel precision: 1 pixel = 256 units"
      deliverables:
        - path: "world/__init__.py"
          briqs: 1
        - path: "world/physics.py"
          briqs: 12
          critical: true
          notes: "INTEGER ONLY! PhysicsBody, apply_gravity, apply_friction"
        - path: "world/collision.py"
          briqs: 10
          critical: true
          notes: "AABB collision, tile collision, SLIDE resolution"
        - path: "world/tiles.py"
          briqs: 8
        - path: "world/level_loader.py"
          briqs: 6
        - path: "world/entities.py"
          briqs: 4
      
    - id: 4
      name: "Player & Smoke"
      cycles: [7, 8]
      briqs_estimate: [40, 50]
      priority: "P0"
      complexity: "COMPLEX"
      dependencies: ["phase_1", "phase_2", "phase_3"]
      critical_notes:
        - "⚠️ Smoke overlay is SEPARATE animation layer on TOP of player"
        - "⚠️ State machine pattern for movement modes"
        - "⚠️ Smoke cycles: smoke_idle -> smoke_q_ring -> repeat (4 seconds)"
      deliverables:
        - path: "actors/__init__.py"
          briqs: 1
        - path: "actors/smoke_overlay.py"
          briqs: 8
          critical: true
          notes: "Independent animation layer, Q-shaped smoke rings!"
        - path: "actors/player.py"
          briqs: 15
          critical: true
          notes: "State machine, powerup management, damage handling"
        - path: "actors/player_states/__init__.py"
          briqs: 1
        - path: "actors/player_states/base_state.py"
          briqs: 5
        - path: "actors/player_states/normal_state.py"
          briqs: 10
          notes: "IDLE, RUN, JUMP, FALL, SHOOT transitions"
      
    - id: 5
      name: "Powerup States"
      cycles: [9, 10]
      briqs_estimate: [35, 45]
      priority: "P1"
      complexity: "COMPLEX"
      dependencies: ["phase_4"]
      critical_notes:
        - "⚠️ Pogo: CONTINUOUS BOUNCE on ground contact - cannot stop!"
        - "⚠️ Pogo: Hold jump = BASS BLAST = extra 300 units jump strength"
        - "⚠️ Jetpack: Fuel depletes while thrusting, regens when grounded"
        - "⚠️ Both powerups LOST when player takes damage"
      deliverables:
        - path: "actors/player_states/jumpupstiq_state.py"
          briqs: 12
          critical: true
          notes: "CONTINUOUS BOUNCE! Hold for BASS BLAST!"
        - path: "actors/player_states/jettpaq_state.py"
          briqs: 12
          critical: true
          notes: "Thrust/hover/fall states, fuel management"
        - path: "objects/__init__.py"
          briqs: 1
        - path: "objects/powerup_pickup.py"
          briqs: 5
        - path: "objects/jumpupstiq_pickup.py"
          briqs: 4
        - path: "objects/jettpaq_pickup.py"
          briqs: 4
      
    - id: 6
      name: "Enemies"
      cycles: [11, 12]
      briqs_estimate: [40, 50]
      priority: "P1"
      complexity: "COMPLEX"
      dependencies: ["phase_3", "phase_4"]
      critical_notes:
        - "⚠️ Each enemy has UNIQUE AI behavior - not copy/paste!"
        - "⚠️ Qlippy does NO DAMAGE - only spawns blocking dialogue"
        - "⚠️ Qortana zap does 2 DAMAGE (higher than normal!)"
        - "⚠️ BriQ Beaver throws ARCING projectiles with gravity"
      deliverables:
        - path: "actors/enemies/__init__.py"
          briqs: 1
        - path: "actors/enemies/base_enemy.py"
          briqs: 8
          notes: "Think function pattern, HP, damage, states"
        - path: "actors/enemies/walqer_bot.py"
          briqs: 7
          notes: "Patrol, turn at edges/walls, shoot at player"
        - path: "actors/enemies/jumper_drqne.py"
          briqs: 6
          notes: "Periodic jump, triggered jump on proximity"
        - path: "actors/enemies/qortana_halo.py"
          briqs: 8
          notes: "Follow player, ZAP attack = 2 DAMAGE!"
        - path: "actors/enemies/qlippy.py"
          briqs: 7
          notes: "NO DAMAGE! Spawns blocking dialogue popup"
        - path: "actors/enemies/briq_beaver.py"
          briqs: 8
          notes: "Stationary, throws ARCING briQ projectiles"
        - path: "actors/projectile.py"
          briqs: 5
      
    - id: 7
      name: "WoNQmodes & UI"
      cycles: [13, 14]
      briqs_estimate: [30, 40]
      priority: "P2"
      complexity: "MODERATE"
      dependencies: ["phase_2"]
      critical_notes:
        - "⚠️ Junglist Mode: 174 BPM = 345ms beat interval EXACTLY"
        - "⚠️ HUD must show fuel gauge when jetpack is active"
        - "⚠️ Mode icons from qq-ui-icons.png row 2"
      deliverables:
        - path: "modes/__init__.py"
          briqs: 1
        - path: "modes/base_mode.py"
          briqs: 4
        - path: "modes/registry.py"
          briqs: 4
        - path: "modes/low_g_mode.py"
          briqs: 3
        - path: "modes/glitch_mode.py"
          briqs: 4
        - path: "modes/mirror_mode.py"
          briqs: 3
        - path: "modes/bullet_time_mode.py"
          briqs: 4
        - path: "modes/speedy_boots_mode.py"
          briqs: 3
        - path: "modes/junglist_mode.py"
          briqs: 5
          notes: "174 BPM = 60000/174 = 345ms beat interval!"
        - path: "ui/__init__.py"
          briqs: 1
        - path: "ui/hud.py"
          briqs: 8
          notes: "Health, score, powerup indicator, FUEL GAUGE"
        - path: "ui/main_menu.py"
          briqs: 5
        - path: "ui/pause_menu.py"
          briqs: 4
      
    - id: 8
      name: "Integration"
      cycles: [15, 16]
      briqs_estimate: [25, 35]
      priority: "P2"
      complexity: "MODERATE"
      dependencies: ["ALL"]
      deliverables:
        - path: "scenes/__init__.py"
          briqs: 1
        - path: "scenes/menu_scene.py"
          briqs: 5
        - path: "scenes/game_scene.py"
          briqs: 10
          notes: "Full integration of all systems"
        - path: "scenes/level_complete_scene.py"
          briqs: 4
        - path: "levels/level01.json"
          briqs: 3
        - path: "levels/level02.json"
          briqs: 3
        - path: "levels/level03.json"
          briqs: 3
        - path: "main.py"
          briqs: 3
        - path: "requirements.txt"
          briqs: 1
        - path: "README.md"
          briqs: 2
      
  # ─────────────────────────────────────────────────────────────────────────────
  # RISK ASSESSMENT (INSPEQTOR FOCUS AREAS)
  # ─────────────────────────────────────────────────────────────────────────────
  risks:
    - id: "RISK001"
      name: "FLOAT_LEAKAGE"
      severity: "HIGH"
      description: "Accidental float usage in physics breaks authentic game feel"
      mitigation: "InspeQtor MUST verify all pos/vel values are int type"
      detection: "isinstance(value, int) assertions in tests"
      
    - id: "RISK002"
      name: "STATE_CORRUPTION"
      severity: "MEDIUM"
      description: "Player state machine transitions incorrectly on powerup"
      mitigation: "Golden Path Tests verify each state transition"
      detection: "Test powerup collect -> state change -> damage -> state revert"
      
    - id: "RISK003"
      name: "SPRITE_MISALIGNMENT"
      severity: "MEDIUM"
      description: "Wrong frame coordinates cause visual glitches"
      mitigation: "All coordinates defined centrally in sprite_data.py"
      detection: "Visual inspection of sprite rendering"
      
    - id: "RISK004"
      name: "CIRCULAR_IMPORTS"
      severity: "LOW"
      description: "Dependency graph violation causes import errors"
      mitigation: "Strict layer hierarchy: shared -> core -> world -> actors"
      detection: "python -c 'import game.main' succeeds"
      
    - id: "RISK005"
      name: "POGO_STOP"
      severity: "MEDIUM"
      description: "JumpUpStiQ stops bouncing when it shouldn't"
      mitigation: "on_ground check ALWAYS triggers bounce - no conditions"
      detection: "Test: land on ground -> velocity immediately negative"

  # ─────────────────────────────────────────────────────────────────────────────
  # VALIDATION CHECKPOINTS (INSPEQTOR GATES)
  # ─────────────────────────────────────────────────────────────────────────────
  checkpoints:
    - after_cycle: 2
      name: "Foundation Complete"
      validate:
        - "shared/sprite_data.py contains ALL 18 asset file mappings"
        - "shared/constants.py values are INTEGER types"
        - "SUBPIXEL_SCALE = 256"
        - "TILE_SIZE = 32"
        
    - after_cycle: 6
      name: "Physics Verified"
      validate:
        - "world/physics.py uses integer math ONLY"
        - "world/collision.py produces SLIDE behavior"
        - "No float type in PhysicsBody pos/vel"
        
    - after_cycle: 10
      name: "Powerups Functional"
      validate:
        - "Pogo auto-bounces on ground contact"
        - "Pogo hold-jump gives extra height"
        - "Jetpack thrust/hover/fall states work"
        - "Jetpack fuel depletes and regenerates"
        - "Smoke overlay renders on top of player"
        
    - after_cycle: 12
      name: "Enemies Complete"
      validate:
        - "All 6 enemy types spawn and behave correctly"
        - "Qlippy blocks movement but does no damage"
        - "Qortana zap deals 2 damage"
        - "BriQ Beaver throws arcing projectiles"
        
    - after_cycle: 14
      name: "Game Playable"
      validate:
        - "python -m game.main launches without crash"
        - "Main menu displays"
        - "Can start and play level 1"
        - "WoNQmodes toggle correctly"
        
  # ─────────────────────────────────────────────────────────────────────────────
  # PROVIDER RECOMMENDATIONS
  # ─────────────────────────────────────────────────────────────────────────────
  providers:
    recommended:
      - provider: "deepseek"
        model: "deepseek-chat"
        config: "b2c12"
        sensitivity: 2
        cycles: 12
        reason: "Best balance of cost and reliability for ENTERPRISE complexity"
        estimated_cost: "$0.50-1.00"
        estimated_time: "45-60 minutes"
        
      - provider: "google"
        model: "gemini-2.5-flash"
        config: "b2c12"
        sensitivity: 2
        cycles: 12
        reason: "Fastest completion with 1M context window"
        estimated_cost: "$0.80-1.50"
        estimated_time: "25-40 minutes"
        
    alternative:
      - provider: "deepseek"
        model: "deepseek-coder"
        config: "b2c12"
        reason: "Code-focused, may handle state patterns better"
        
    not_recommended:
      - provider: "openai"
        model: "gpt-4o"
        reason: "128K context may struggle with 85KB+ spec"
```

---

## 0. Executive Summary

This document represents the **COMPLETE, COMPREHENSIVE BUILD SPECIFICATION** for QommandahQeen - a modern Commander Keen-inspired platformer engine. It fuses:

- **Commander Keen Modding Blueprint** technical analysis
- **All sprite asset specifications** with exact frame coordinates
- **Powerup system** (JumpUpStiQ pogo, JettPaQ jetpack)
- **Smoke overlay system** (continuous Q-shaped smoke rings)
- **6 Enemy types** with distinct AI behaviors
- **6 WoNQmodes** with HUD icons
- **Integer sub-pixel physics** (256 units = 1 pixel)
- **Complete project structure** from scratch to playable game

**This tasq is designed for QonQrete to build the ENTIRE GAME in one orchestrated run.**

---

## 1. 🔥 Project Overview & Historical Context

### 1.1 The Commander Keen Legacy

Commander Keen: Invasion of the Vorticons (1990) pioneered smooth-scrolling platformers on PC hardware through John Carmack's **Adaptive Tile Refresh (ATR)** technique. The engine's distinctive "Nintendo feel" came from:

- **Integer-based sub-pixel physics** (1 pixel = 256 units)
- **Fixed-point math** for smooth acceleration/deceleration
- **Actor model with "Think" functions** for entity behavior
- **Tile-based collision** with slide resolution
- **Pogo stick mechanic** for variable-height jumps

### 1.2 QommandahQeen Vision

We recreate this legendary feel with modern Python/Pygame-CE while adding:

- **Custom QonQrete/Junglist aesthetic** (neon green/purple, glitch effects)
- **Expanded powerup system** (subwoofer pogo, boombox jetpack)
- **Signature smoke overlay** (Q-shaped smoke rings)
- **6 unique enemy types** with distinct AI
- **6 WoNQmodes** for gameplay modification
- **Full UI system** with HUD, menus, level transitions

### 1.3 Technical Stack

| Component | Technology | Rationale |
|-----------|------------|-----------|
| Language | Python 3.10+ | Type hints, AI-friendly |
| Framework | pygame-ce | Community Edition, active development |
| Resolution | 320x200 internal | Authentic EGA feel |
| Scaling | 3-4x NEAREST | Crisp pixel art |
| Physics | Custom integer | Authentic "Nintendo feel" |
| Data | JSON/PNG | Human-readable, moddable |

---

## 2. 🎨 COMPLETE SPRITE ASSET SPECIFICATIONS

### 2.1 Asset Files Registry

```python
# =============================================================================
# COMPLETE ASSET FILE REGISTRY
# All sprites must be placed in: qodeyard/assets/
# =============================================================================

ASSET_FILES = {
    # =========================================================================
    # PLAYER SPRITES
    # =========================================================================
    "player": "qq-qommandah-qeen.png",
    "player_smoqin": "qq-smoqin.png",
    "player_jumpupstiq": "qq-qommandah-qeen-jumpupstiq.png",
    "player_jettpaq": "qq-qommandah-qeen-jetpaq.png",
    
    # =========================================================================
    # POWERUP PICKUP ITEMS
    # =========================================================================
    "pickup_jumpupstiq": "qq-jumpupstiq.png",
    "pickup_jettpaq": "qq-jettpaq.png",
    
    # =========================================================================
    # ENEMY SPRITES
    # =========================================================================
    "walqer_bot": "qq-walqer-bot.png",
    "jumper_drqne": "qq-jumper-drqne.png",
    "qortana_halo": "qq-qortana-halo.png",
    "qlippy": "qq-qlippy.png",
    "briq_beaver": "qq-briq-beaver.png",
    
    # =========================================================================
    # EFFECTS & TILES
    # =========================================================================
    "projectiles": "qq-bullets-explosions.png",
    "tilesets": "qq-tilesets.png",
    "ui_icons": "qq-ui-icons.png",
    
    # =========================================================================
    # BACKGROUNDS
    # =========================================================================
    "background1": "qq-background1.png",
    "background2": "qq-background2.png",
    "background3": "qq-background3.png",
    "background4": "qq-background4.png",
}
```

---

### 2.2 Player Base Sprite: qq-qommandah-qeen.png

**Character:** Neon green/purple armored figure with glowing yellow visor, steam vents from helmet

**Visual Style:** Cyberpunk meets retro platformer, QonQrete brand colors

```python
# =============================================================================
# SPRITE MAPPING: qq-qommandah-qeen.png
# Base player animations - used when NO powerup is active
# =============================================================================

QOMMANDAH_QEEN_FRAMES = {
    # -------------------------------------------------------------------------
    # ROW 0: IDLE (4 frames) - Breathing animation with steam puffs
    # -------------------------------------------------------------------------
    "idle": {
        "row": 0,
        "frames": 4,
        "start_col": 0,
        "fps": 6,
        "frame_width": 192,
        "frame_height": 192,
        "loop": True,
        "note": "Standing idle with helmet steam puffs, slight sway"
    },
    
    # -------------------------------------------------------------------------
    # ROW 0-1: RUN (8 frames) - Running cycle with muzzle flash on last frame
    # -------------------------------------------------------------------------
    "run": {
        "row": 0,
        "frames": 8,
        "start_col": 4,
        "fps": 12,
        "frame_width": 192,
        "frame_height": 192,
        "loop": True,
        "note": "Full run cycle, frames 5-8 on row 1, last frame has muzzle flash variant"
    },
    
    # -------------------------------------------------------------------------
    # ROW 2: JUMP (3 frames) - Jump arc animation
    # -------------------------------------------------------------------------
    "jump": {
        "row": 2,
        "frames": 3,
        "start_col": 0,
        "fps": 8,
        "frame_width": 192,
        "frame_height": 192,
        "loop": False,
        "note": "Jump anticipation, apex, descent"
    },
    
    # -------------------------------------------------------------------------
    # ROW 2: FALL (1 frame) - Falling pose (can reuse jump frame 3)
    # -------------------------------------------------------------------------
    "fall": {
        "row": 2,
        "frames": 1,
        "start_col": 2,
        "fps": 1,
        "frame_width": 192,
        "frame_height": 192,
        "loop": False,
        "note": "Descent pose, arms up"
    },
    
    # -------------------------------------------------------------------------
    # ROW 3: SHOOT (2 frames) - Shooting with muzzle flash
    # -------------------------------------------------------------------------
    "shoot": {
        "row": 3,
        "frames": 2,
        "start_col": 0,
        "fps": 10,
        "frame_width": 192,
        "frame_height": 192,
        "loop": False,
        "note": "Arm extended, muzzle flash effect on frame 2"
    },
    
    # -------------------------------------------------------------------------
    # ROW 3: HURT (2 frames) - Taking damage with particles
    # -------------------------------------------------------------------------
    "hurt": {
        "row": 3,
        "frames": 2,
        "start_col": 2,
        "fps": 8,
        "frame_width": 192,
        "frame_height": 192,
        "loop": False,
        "note": "Recoil animation with orange damage particles"
    },
    
    # -------------------------------------------------------------------------
    # ROW 4: DEAD (4 frames) - Death sequence
    # -------------------------------------------------------------------------
    "dead": {
        "row": 4,
        "frames": 4,
        "start_col": 0,
        "fps": 6,
        "frame_width": 192,
        "frame_height": 192,
        "loop": False,
        "note": "Collapse sequence - stagger, fall, crumple, still"
    }
}

# Hitbox is smaller than sprite for fair gameplay
QOMMANDAH_QEEN_HITBOX = {
    "width": 64,
    "height": 80,
    "offset_x": 64,   # Center in 192px frame
    "offset_y": 56    # Bottom-aligned
}
```

---

### 2.3 Smoke Overlay: qq-smoqin.png

**CRITICAL SYSTEM:** This is an INDEPENDENT ANIMATION LAYER that plays ON TOP of the player sprite continuously during idle/run states. The smoke forms a distinctive "Q" shape - signature QonQrete branding!

```python
# =============================================================================
# SPRITE MAPPING: qq-smoqin.png
# Smoke overlay animation - plays continuously on top of player
# The smoke forms Q-shaped rings - THE SIGNATURE VISUAL!
# =============================================================================

SMOQIN_FRAMES = {
    # -------------------------------------------------------------------------
    # ROW 0: SMOKE IDLE START (4 frames) - Character smoking, smoke growing
    # -------------------------------------------------------------------------
    "smoke_idle": {
        "row": 0,
        "frames": 4,
        "start_col": 0,
        "fps": 4,
        "frame_width": 200,
        "frame_height": 240,
        "loop": False,
        "note": "Idle stance with pipe, smoke starting to form and rise"
    },
    
    # -------------------------------------------------------------------------
    # ROW 1: Q-RING FORMATION (4 frames) - Smoke expands into Q shape!
    # -------------------------------------------------------------------------
    "smoke_q_ring": {
        "row": 1,
        "frames": 4,
        "start_col": 0,
        "fps": 3,
        "frame_width": 200,
        "frame_height": 240,
        "loop": False,
        "note": "Smoke expands into Q-shaped ring with green/purple colors - THE SIGNATURE!"
    }
}

# Smoke overlay configuration
SMOQIN_CONFIG = {
    "always_active": True,
    "overlay_offset_x": -20,
    "overlay_offset_y": -60,
    "cycle_duration_ms": 4000,
    "blend_mode": "additive",
    "plays_during_states": [
        "idle", "run",
        "pogo_idle",
        "jetpack_idle", "jetpack_hover"
    ],
    "disabled_during_states": [
        "hurt", "dead", "shoot",
        "pogo_jump", "jetpack_thrust"
    ]
}
```

---

### 2.4 JumpUpStiQ Pickup: qq-jumpupstiq.png

**Description:** Subwoofer-powered pogo stick with green energy rings at the base. Collectible powerup item that floats and bobs in the level.

```python
# =============================================================================
# SPRITE MAPPING: qq-jumpupstiq.png
# Pogo stick pickup item - subwoofer with T-handle and energy rings
# =============================================================================

JUMPUPSTIQ_PICKUP_FRAMES = {
    # -------------------------------------------------------------------------
    # IDLE (1 frame or animated glow)
    # -------------------------------------------------------------------------
    "idle": {
        "row": 0,
        "frames": 1,
        "start_col": 0,
        "fps": 1,
        "frame_width": 160,
        "frame_height": 280,
        "loop": True,
        "note": "Subwoofer pogo with purple T-handle, green energy meter, green rings at base"
    },
    
    # Optional: If animated
    "glow": {
        "row": 0,
        "frames": 4,
        "start_col": 0,
        "fps": 6,
        "frame_width": 160,
        "frame_height": 280,
        "loop": True,
        "note": "Pulsing green energy rings animation"
    }
}

JUMPUPSTIQ_PICKUP_CONFIG = {
    "type": "powerup",
    "grants": "jumpupstiq",
    "duration": -1,
    "hitbox_width": 48,
    "hitbox_height": 80,
    "bob_amplitude": 8,
    "bob_speed": 2.0,
    "glow_color": (0, 255, 100),
    "pickup_sound": "powerup_collect.wav"
}
```

---

### 2.5 Player ON JumpUpStiQ: qq-qommandah-qeen-jumpupstiq.png

**Description:** Qommandah Qeen balancing on the subwoofer pogo stick! Features the signature BASS BLAST colorful explosion effect on super jumps.

```python
# =============================================================================
# SPRITE MAPPING: qq-qommandah-qeen-jumpupstiq.png
# Player riding the JumpUpStiQ pogo stick - continuous bouncing!
# =============================================================================

QOMMANDAH_QEEN_JUMPUPSTIQ_FRAMES = {
    # -------------------------------------------------------------------------
    # ROW 0: IDLE BALANCE (4 frames) - Bouncing on stick with energy base
    # -------------------------------------------------------------------------
    "pogo_idle": {
        "row": 0,
        "frames": 4,
        "start_col": 0,
        "fps": 8,
        "frame_width": 200,
        "frame_height": 300,
        "loop": True,
        "note": "Balancing on JumpUpStiQ, slight wobble, green energy rings at base"
    },
    
    # -------------------------------------------------------------------------
    # ROW 1: BASS BLAST JUMP (2 frames) - Explosive colorful jump!
    # -------------------------------------------------------------------------
    "pogo_jump": {
        "row": 1,
        "frames": 2,
        "start_col": 0,
        "fps": 15,
        "frame_width": 240,
        "frame_height": 320,
        "loop": False,
        "note": "MASSIVE bass explosion with green/purple/orange colorful splatter - THE SUPER JUMP!"
    },
    
    # -------------------------------------------------------------------------
    # ROW 1: LANDING COMPRESSION (2 frames) - After the jump
    # -------------------------------------------------------------------------
    "pogo_land": {
        "row": 1,
        "frames": 2,
        "start_col": 2,
        "fps": 10,
        "frame_width": 200,
        "frame_height": 280,
        "loop": False,
        "note": "Landing compression, springs compress, energy rings reform"
    }
}

# JumpUpStiQ physics configuration - THE POGO FEEL!
JUMPUPSTIQ_PHYSICS = {
    "jump_strength": -1400,
    "normal_bounce": -900,
    "continuous_bounce": True,
    "hold_for_higher": True,
    "max_hold_bonus": 300,
    "gravity_modifier": 0.9,
    "horizontal_control": 0.7,
    "friction_modifier": 0.5,
    "bass_blast_particles": True,
    "particle_colors": [(0, 255, 100), (200, 0, 255), (255, 150, 0)],
    "bounce_sound": "bass_bounce.wav",
    "blast_sound": "bass_blast.wav"
}

JUMPUPSTIQ_HITBOX = {
    "width": 64,
    "height": 120,
    "offset_x": 68,
    "offset_y": 90
}
```

---

### 2.6 JettPaQ Pickup: qq-jettpaq.png

**Description:** Boombox jetpack with twin speaker thrusters and energy rings. The ultimate mobility powerup!

```python
# =============================================================================
# SPRITE MAPPING: qq-jettpaq.png
# Jetpack pickup item - twin boombox speakers with thrust rings
# =============================================================================

JETTPAQ_PICKUP_FRAMES = {
    # -------------------------------------------------------------------------
    # IDLE (1 frame or animated thrust)
    # -------------------------------------------------------------------------
    "idle": {
        "row": 0,
        "frames": 1,
        "start_col": 0,
        "fps": 1,
        "frame_width": 200,
        "frame_height": 300,
        "loop": True,
        "note": "Boombox jetpack with twin speaker thrusters, green/purple energy rings"
    },
    
    # If animated - shows thrust effect
    "active": {
        "row": 0,
        "frames": 4,
        "start_col": 0,
        "fps": 12,
        "frame_width": 200,
        "frame_height": 300,
        "loop": True,
        "note": "Thrusters firing with animated green/purple/yellow energy rings"
    }
}

JETTPAQ_PICKUP_CONFIG = {
    "type": "powerup",
    "grants": "jettpaq",
    "duration": -1,
    "fuel_amount": 300,
    "hitbox_width": 64,
    "hitbox_height": 80,
    "bob_amplitude": 10,
    "bob_speed": 3.0,
    "glow_color": (200, 0, 255),
    "pickup_sound": "powerup_collect.wav"
}
```

---

### 2.7 Player WITH JettPaQ: qq-qommandah-qeen-jetpaq.png

**Description:** Qommandah Qeen with boombox jetpack mounted on back! Full flight capability with fuel management.

```python
# =============================================================================
# SPRITE MAPPING: qq-qommandah-qeen-jetpaq.png
# Player with JettPaQ jetpack equipped - FLIGHT MODE!
# =============================================================================

QOMMANDAH_QEEN_JETTPAQ_FRAMES = {
    # -------------------------------------------------------------------------
    # ROW 0: IDLE GROUNDED (5 frames) - Walking/idle with jetpack on back
    # -------------------------------------------------------------------------
    "jetpack_idle": {
        "row": 0,
        "frames": 5,
        "start_col": 0,
        "fps": 8,
        "frame_width": 180,
        "frame_height": 200,
        "loop": True,
        "note": "Grounded with boombox jetpack visible on back, slight movement"
    },
    
    # -------------------------------------------------------------------------
    # ROW 1: THRUST/ASCEND (3 frames) - Flying upward with thrust effect!
    # -------------------------------------------------------------------------
    "jetpack_thrust": {
        "row": 1,
        "frames": 3,
        "start_col": 0,
        "fps": 15,
        "frame_width": 180,
        "frame_height": 280,
        "loop": True,
        "note": "Jetpack FIRING! Green/purple energy rings below, particle trail"
    },
    
    # -------------------------------------------------------------------------
    # ROW 2: HOVER/STABILIZE (2 frames) - Hovering in place
    # -------------------------------------------------------------------------
    "jetpack_hover": {
        "row": 2,
        "frames": 2,
        "start_col": 0,
        "fps": 6,
        "frame_width": 180,
        "frame_height": 240,
        "loop": True,
        "note": "Hovering in place, gentle thrust, smaller rings"
    },
    
    # -------------------------------------------------------------------------
    # ROW 2: FALLING (1 frame) - Falling without thrust
    # -------------------------------------------------------------------------
    "jetpack_fall": {
        "row": 2,
        "frames": 1,
        "start_col": 2,
        "fps": 1,
        "frame_width": 180,
        "frame_height": 200,
        "loop": False,
        "note": "Falling with jetpack (no fuel or not thrusting), wind lines"
    }
}

# JettPaQ physics configuration - FLIGHT MECHANICS!
JETTPAQ_PHYSICS = {
    "thrust_strength": -60,
    "max_vertical_speed_up": -600,
    "max_vertical_speed_down": 400,
    "hover_gravity": 15,
    "fall_gravity": 35,
    "horizontal_speed": 400,
    "horizontal_accel": 30,
    "air_friction": 0.95,
    "fuel_consumption_rate": 1,
    "fuel_regen_grounded": 0.5,
    "fuel_regen_delay_ms": 500,
    "can_shoot": True,
    "thrust_sound": "jetpack_thrust.wav",
    "hover_sound": "jetpack_hover.wav"
}

JETTPAQ_HITBOX = {
    "width": 72,
    "height": 100,
    "offset_x": 54,
    "offset_y": 50
}
```

---

### 2.8 Enemy: WalQer Bot - qq-walqer-bot.png

**Character:** Rusty industrial robot with glowing orange eye, steam exhaust, bipedal walker. Classic patrol enemy.

```python
# =============================================================================
# SPRITE MAPPING: qq-walqer-bot.png
# Enemy: Patrol robot that walks back and forth, shoots at player
# =============================================================================

WALQER_BOT_FRAMES = {
    # -------------------------------------------------------------------------
    # ROW 0: IDLE (6 frames) - Breathing/steam animation
    # -------------------------------------------------------------------------
    "idle": {
        "row": 0,
        "frames": 6,
        "start_col": 0,
        "fps": 6,
        "frame_width": 160,
        "frame_height": 160,
        "loop": True,
        "note": "Standing idle with steam puffs from exhaust, eye glow pulse"
    },
    
    # -------------------------------------------------------------------------
    # ROW 1: WALK (6 frames) - Stomping walk cycle with shooting variant
    # -------------------------------------------------------------------------
    "walk": {
        "row": 1,
        "frames": 6,
        "start_col": 0,
        "fps": 8,
        "frame_width": 160,
        "frame_height": 160,
        "loop": True,
        "note": "Heavy stomping walk, frame 6 has muzzle flash for walk+shoot"
    },
    
    # -------------------------------------------------------------------------
    # ROW 2: DEATH PHASE 1 (4 frames) - Sparks, crumble, explosion
    # -------------------------------------------------------------------------
    "death": {
        "row": 2,
        "frames": 4,
        "start_col": 0,
        "fps": 8,
        "frame_width": 200,
        "frame_height": 160,
        "loop": False,
        "note": "Sparks fly, parts break off, BIG orange explosion on frame 4"
    },
    
    # -------------------------------------------------------------------------
    # ROW 3: DEATH PHASE 2 (4 frames) - Wreckage settling
    # -------------------------------------------------------------------------
    "death_settle": {
        "row": 3,
        "frames": 4,
        "start_col": 0,
        "fps": 6,
        "frame_width": 200,
        "frame_height": 120,
        "loop": False,
        "note": "Wreckage falls, smoke rises, debris settles"
    }
}

WALQER_BOT_HITBOX = {
    "width": 80,
    "height": 100,
    "offset_x": 40,
    "offset_y": 30
}

WALQER_BOT_CONFIG = {
    "hp": 3,
    "damage": 1,
    "patrol_speed": 96,
    "chase_speed": 128,
    "detection_range": 200,
    "can_shoot": True,
    "shoot_cooldown_ms": 2000,
    "projectile_speed": 256,
    "turn_at_edges": True,
    "turn_at_walls": True,
    "score_value": 100
}
```

---

### 2.9 Enemy: Jumper DrQne - qq-jumper-drqne.png

**Character:** Spring-coiled drone with glowing orange core. Jumps periodically or when player approaches.

```python
# =============================================================================
# SPRITE MAPPING: qq-jumper-drqne.png
# Enemy: Bouncing drone that jumps at regular intervals or on proximity
# =============================================================================

JUMPER_DRQNE_FRAMES = {
    # -------------------------------------------------------------------------
    # ROW 0: COIL (3 frames) - Extended spring idle
    # -------------------------------------------------------------------------
    "coil": {
        "row": 0,
        "frames": 3,
        "start_col": 0,
        "fps": 4,
        "frame_width": 160,
        "frame_height": 200,
        "loop": True,
        "note": "Spring extended, glowing core pulses, particles around body"
    },
    
    # -------------------------------------------------------------------------
    # ROW 1: JUMP CHARGE (2 frames) - Spring compressed, ready to launch
    # -------------------------------------------------------------------------
    "jump_charge": {
        "row": 1,
        "frames": 2,
        "start_col": 0,
        "fps": 8,
        "frame_width": 140,
        "frame_height": 120,
        "loop": False,
        "note": "Compressed coil, energy building, about to spring"
    },
    
    # -------------------------------------------------------------------------
    # ROW 2: BREAK/DEATH (3 frames) - Explosion
    # -------------------------------------------------------------------------
    "break": {
        "row": 2,
        "frames": 3,
        "start_col": 0,
        "fps": 10,
        "frame_width": 180,
        "frame_height": 180,
        "loop": False,
        "note": "Explosive destruction with core burst and debris"
    }
}

JUMPER_DRQNE_HITBOX = {
    "width": 60,
    "height": 80,
    "offset_x": 50,
    "offset_y": 60
}

JUMPER_DRQNE_CONFIG = {
    "hp": 2,
    "damage": 1,
    "jump_strength": -800,
    "horizontal_jump_speed": 150,
    "jump_interval_ms": 2500,
    "triggered_jump_range": 150,
    "gravity": 40,
    "score_value": 75
}
```

---

### 2.10 Enemy: Qortana Halo - qq-qortana-halo.png

**Character:** Glitchy holographic figure with green halo ring. Follows player and ZAP attacks with electricity when close!

```python
# =============================================================================
# SPRITE MAPPING: qq-qortana-halo.png
# Enemy: Floating hologram that follows player and zaps with electricity
# HIGH DAMAGE - 2 points per zap!
# =============================================================================

QORTANA_HALO_FRAMES = {
    # -------------------------------------------------------------------------
    # ROW 0: IDLE/HOVER (4 frames) - Glitchy floating animation
    # -------------------------------------------------------------------------
    "hover": {
        "row": 0,
        "frames": 4,
        "start_col": 0,
        "fps": 8,
        "frame_width": 160,
        "frame_height": 200,
        "loop": True,
        "note": "Pixelated glitch effect body, green halo spinning above head"
    },
    
    # -------------------------------------------------------------------------
    # ROW 1: HOVER VARIANT (2 frames) - Alternative hover
    # -------------------------------------------------------------------------
    "hover_alt": {
        "row": 1,
        "frames": 2,
        "start_col": 0,
        "fps": 6,
        "frame_width": 160,
        "frame_height": 200,
        "loop": True,
        "note": "Different glitch pattern, halo at different angle"
    },
    
    # -------------------------------------------------------------------------
    # ROW 2: ATTACK CHARGE (4 frames) - Electricity zap!
    # -------------------------------------------------------------------------
    "attack": {
        "row": 2,
        "frames": 4,
        "start_col": 0,
        "fps": 12,
        "frame_width": 200,
        "frame_height": 200,
        "loop": False,
        "note": "Lightning/electricity effect spreading out from body - ZAP!"
    }
}

QORTANA_HALO_HITBOX = {
    "width": 60,
    "height": 120,
    "offset_x": 50,
    "offset_y": 40
}

QORTANA_HALO_CONFIG = {
    "hp": 4,
    "damage": 0,
    "zap_damage": 2,
    "hover_speed": 48,
    "follow_speed": 64,
    "zap_range": 128,
    "zap_cooldown_ms": 3000,
    "zap_duration_ms": 500,
    "follows_player": True,
    "score_value": 150
}
```

---

### 2.11 Enemy: Qlippy - qq-qlippy.png

**Character:** Corrupted Clippy parody - annoying helper that blocks your path with dialogue popups! NO DAMAGE but incredibly annoying!

```python
# =============================================================================
# SPRITE MAPPING: qq-qlippy.png
# Enemy: Annoying paperclip that spawns blocking dialogue boxes
# DOES NOT DAMAGE - just blocks movement!
# =============================================================================

QLIPPY_FRAMES = {
    # -------------------------------------------------------------------------
    # ROW 0: MOVE (3 frames) - Floating paperclip movement
    # -------------------------------------------------------------------------
    "move": {
        "row": 0,
        "frames": 3,
        "start_col": 0,
        "fps": 6,
        "frame_width": 100,
        "frame_height": 140,
        "loop": True,
        "note": "Glitchy floating animation, green/purple eye glow alternates"
    },
    
    # -------------------------------------------------------------------------
    # ROW 1: ANNOY SKILL - Dialogue Box (special attack!)
    # -------------------------------------------------------------------------
    "annoy_dialogue": {
        "row": 1,
        "frames": 1,
        "start_col": 0,
        "fps": 1,
        "frame_width": 320,
        "frame_height": 180,
        "loop": False,
        "note": "Glitchy popup with fake error text, warning icons, 'OK' button"
    },
    
    # -------------------------------------------------------------------------
    # ROW 2: Small Qlippy (appears alongside dialogue)
    # -------------------------------------------------------------------------
    "annoy_small": {
        "row": 2,
        "frames": 1,
        "start_col": 0,
        "fps": 1,
        "frame_width": 60,
        "frame_height": 80,
        "loop": False,
        "note": "Tiny Qlippy that appears next to dialogue box"
    }
}

QLIPPY_HITBOX = {
    "width": 40,
    "height": 60,
    "offset_x": 30,
    "offset_y": 40
}

QLIPPY_CONFIG = {
    "hp": 1,
    "damage": 0,
    "move_speed": 64,
    "patrol_range": 200,
    "annoy_interval_ms": 5000,
    "annoy_duration_ms": 2000,
    "dialogue_blocks_movement": True,
    "dialogue_offset_y": -100,
    "score_value": 25
}
```

---

### 2.12 Enemy: BriQ Beaver - qq-briq-beaver.png

**Character:** Blue cyber-beaver that throws colorful briQ blocks with arcing trajectory!

```python
# =============================================================================
# SPRITE MAPPING: qq-briq-beaver.png
# Enemy: Stationary beaver that throws arcing briQ projectiles
# =============================================================================

BRIQ_BEAVER_FRAMES = {
    # -------------------------------------------------------------------------
    # ROW 0: IDLE (3 frames) - Holding briQ block
    # -------------------------------------------------------------------------
    "idle": {
        "row": 0,
        "frames": 3,
        "start_col": 0,
        "fps": 4,
        "frame_width": 180,
        "frame_height": 160,
        "loop": True,
        "note": "Blue beaver holding colorful glitchy briQ block"
    },
    
    # -------------------------------------------------------------------------
    # ROW 1: WIND-UP/RELOAD (3 frames) - Preparing to throw
    # -------------------------------------------------------------------------
    "windup": {
        "row": 1,
        "frames": 3,
        "start_col": 0,
        "fps": 8,
        "frame_width": 180,
        "frame_height": 160,
        "loop": False,
        "note": "Pulling back briQ, charging throw animation"
    },
    
    # -------------------------------------------------------------------------
    # ROW 2: THROW ATTACK (3 frames) - Releasing briQ
    # -------------------------------------------------------------------------
    "throw": {
        "row": 2,
        "frames": 3,
        "start_col": 0,
        "fps": 12,
        "frame_width": 200,
        "frame_height": 160,
        "loop": False,
        "note": "Full throwing motion, arm extended"
    },
    
    # -------------------------------------------------------------------------
    # ROW 3: BRIQ PROJECTILE (3 frames) - The thrown briQ itself
    # -------------------------------------------------------------------------
    "briq_projectile": {
        "row": 3,
        "frames": 3,
        "start_col": 0,
        "fps": 15,
        "frame_width": 48,
        "frame_height": 48,
        "loop": True,
        "note": "Spinning colorful briQ block projectile"
    },
    
    # -------------------------------------------------------------------------
    # ROW 3: DEATH (3 frames) - After projectile frames
    # -------------------------------------------------------------------------
    "death": {
        "row": 3,
        "frames": 3,
        "start_col": 3,
        "fps": 8,
        "frame_width": 180,
        "frame_height": 120,
        "loop": False,
        "note": "Collapse and debris"
    }
}

BRIQ_BEAVER_HITBOX = {
    "width": 80,
    "height": 100,
    "offset_x": 50,
    "offset_y": 30
}

BRIQ_BEAVER_CONFIG = {
    "hp": 3,
    "damage": 1,
    "briq_damage": 1,
    "throw_interval_ms": 2500,
    "briq_speed": 384,
    "briq_arc_gravity": 25,
    "briq_arc": True,
    "stationary": True,
    "detection_range": 300,
    "score_value": 100
}
```

---

### 2.13 Projectiles & Effects: qq-bullets-explosions.png

```python
# =============================================================================
# SPRITE MAPPING: qq-bullets-explosions.png
# Projectiles, impacts, and explosion effects
# =============================================================================

PROJECTILES_FRAMES = {
    # -------------------------------------------------------------------------
    # ROW 0: GREEN BULLET (player projectile)
    # -------------------------------------------------------------------------
    "bullet_green": {
        "row": 0,
        "frames": 4,
        "start_col": 0,
        "fps": 15,
        "frame_width": 64,
        "frame_height": 32,
        "loop": True,
        "note": "Player's green energy bullet with trail"
    },
    
    # -------------------------------------------------------------------------
    # ROW 1: PURPLE BULLET (enemy projectile)
    # -------------------------------------------------------------------------
    "bullet_purple": {
        "row": 1,
        "frames": 4,
        "start_col": 0,
        "fps": 15,
        "frame_width": 64,
        "frame_height": 32,
        "loop": True,
        "note": "Enemy's purple energy bullet with trail"
    },
    
    # -------------------------------------------------------------------------
    # ROW 2: GREEN SPLAT IMPACT
    # -------------------------------------------------------------------------
    "impact_green": {
        "row": 2,
        "frames": 4,
        "start_col": 0,
        "fps": 20,
        "frame_width": 80,
        "frame_height": 80,
        "loop": False,
        "note": "Green splatter when player bullet hits"
    },
    
    # -------------------------------------------------------------------------
    # ROW 3: PURPLE/ORANGE IMPACT
    # -------------------------------------------------------------------------
    "impact_purple": {
        "row": 3,
        "frames": 4,
        "start_col": 0,
        "fps": 20,
        "frame_width": 80,
        "frame_height": 80,
        "loop": False,
        "note": "Purple/orange energy burst when enemy bullet hits"
    },
    
    # -------------------------------------------------------------------------
    # ROW 4: BIG EXPLOSION (enemy death)
    # -------------------------------------------------------------------------
    "explosion_big": {
        "row": 4,
        "frames": 3,
        "start_col": 0,
        "fps": 12,
        "frame_width": 200,
        "frame_height": 200,
        "loop": False,
        "note": "Large fiery explosion for enemy deaths"
    }
}

PROJECTILE_CONFIG = {
    "player_bullet_speed": 512,
    "player_bullet_damage": 1,
    "enemy_bullet_speed": 256,
    "enemy_bullet_damage": 1,
    "projectile_lifetime_ms": 3000
}
```

---

### 2.14 Tilesets: qq-tilesets.png

```python
# =============================================================================
# SPRITE MAPPING: qq-tilesets.png
# Tiles, platforms, hazards, and decorations
# =============================================================================

TILESET_REGIONS = {
    # -------------------------------------------------------------------------
    # GROUND TILES (top-left area)
    # -------------------------------------------------------------------------
    "ground": {
        "start_x": 0,
        "start_y": 0,
        "tile_width": 64,
        "tile_height": 64,
        "columns": 4,
        "rows": 4,
        "tiles": [
            {"id": 0, "name": "empty", "solid": False},
            {"id": 1, "name": "stone_dark", "solid": True},
            {"id": 2, "name": "stone_rusty", "solid": True},
            {"id": 3, "name": "dirt_rocky", "solid": True},
            {"id": 4, "name": "dirt_brown", "solid": True},
            {"id": 5, "name": "stone_slime_top", "solid": True},
            {"id": 6, "name": "stone_slime_drip", "solid": True},
            {"id": 7, "name": "brick_green", "solid": True},
            {"id": 8, "name": "brick_rusty", "solid": True},
            {"id": 9, "name": "metal_plate", "solid": True},
            {"id": 10, "name": "metal_grate", "solid": True},
            {"id": 11, "name": "concrete_cracked", "solid": True},
            {"id": 12, "name": "concrete_mossy", "solid": True},
            {"id": 13, "name": "stone_slime_full", "solid": True},
            {"id": 14, "name": "industrial_panel", "solid": True},
            {"id": 15, "name": "industrial_vent", "solid": True}
        ]
    },
    
    # -------------------------------------------------------------------------
    # PLATFORMS (metal scaffolding - middle area)
    # -------------------------------------------------------------------------
    "platforms": {
        "start_x": 256,
        "start_y": 0,
        "tile_width": 64,
        "tile_height": 32,
        "columns": 4,
        "rows": 6,
        "tiles": [
            {"id": 20, "name": "scaffold_green_left", "solid": True, "semi_solid": True},
            {"id": 21, "name": "scaffold_green_mid", "solid": True, "semi_solid": True},
            {"id": 22, "name": "scaffold_green_right", "solid": True, "semi_solid": True},
            {"id": 23, "name": "scaffold_yellow_left", "solid": True, "semi_solid": True},
            {"id": 24, "name": "scaffold_yellow_mid", "solid": True, "semi_solid": True},
            {"id": 25, "name": "scaffold_yellow_right", "solid": True, "semi_solid": True},
            {"id": 26, "name": "scaffold_purple_left", "solid": True, "semi_solid": True},
            {"id": 27, "name": "scaffold_purple_mid", "solid": True, "semi_solid": True},
            {"id": 28, "name": "scaffold_purple_right", "solid": True, "semi_solid": True},
            {"id": 29, "name": "beam_horizontal", "solid": True},
            {"id": 30, "name": "beam_vertical", "solid": False},
            {"id": 31, "name": "ladder", "solid": False, "climbable": True}
        ]
    },
    
    # -------------------------------------------------------------------------
    # HAZARDS (right side - labeled "HAZARDS")
    # -------------------------------------------------------------------------
    "hazards": {
        "start_x": 512,
        "start_y": 0,
        "tile_width": 64,
        "tile_height": 64,
        "tiles": [
            {"id": 40, "name": "acid_pool", "deadly": True, "animated": True, "frames": 3, "fps": 4},
            {"id": 41, "name": "acid_bubble", "deadly": True, "animated": True, "frames": 3, "fps": 6},
            {"id": 42, "name": "spikes_metal", "deadly": True, "damage": 1},
            {"id": 43, "name": "energy_beam_purple", "deadly": True, "animated": True, "frames": 4, "fps": 8},
            {"id": 44, "name": "energy_beam_yellow", "deadly": True, "animated": True, "frames": 4, "fps": 8},
            {"id": 45, "name": "laser_horizontal", "deadly": True, "animated": True, "frames": 2, "fps": 12},
            {"id": 46, "name": "laser_vertical", "deadly": True, "animated": True, "frames": 2, "fps": 12}
        ]
    },
    
    # -------------------------------------------------------------------------
    # DECOR (bottom area - labeled "DECOR")
    # -------------------------------------------------------------------------
    "decor": {
        "start_x": 0,
        "start_y": 400,
        "tiles": [
            {"id": 60, "name": "pipe_slime", "solid": False},
            {"id": 61, "name": "barrel_qonqrete", "solid": True, "destructible": True},
            {"id": 62, "name": "barrel_nuclear", "solid": True, "destructible": True, "explodes": True},
            {"id": 63, "name": "crate_screen", "solid": True},
            {"id": 64, "name": "crate_radioactive", "solid": True},
            {"id": 65, "name": "barrel_rusty", "solid": True},
            {"id": 66, "name": "terminal", "solid": True, "interactable": True},
            {"id": 67, "name": "monitor", "solid": False, "animated": True, "frames": 4, "fps": 2}
        ]
    }
}
```

---

### 2.15 UI Icons: qq-ui-icons.png

```python
# =============================================================================
# SPRITE MAPPING: qq-ui-icons.png
# Health, score, collectibles, and WoNQmode indicators
# =============================================================================

UI_ICONS = {
    # -------------------------------------------------------------------------
    # ROW 0: HEALTH INDICATORS
    # -------------------------------------------------------------------------
    "health": {
        "row": 0,
        "icons": [
            {"name": "heart", "col": 0, "width": 64, "height": 64, "note": "Green glowing heart - HP"},
            {"name": "shield", "col": 1, "width": 64, "height": 64, "note": "Purple cracked shield - Armor"},
            {"name": "biohazard", "col": 2, "width": 64, "height": 64, "note": "Orange biohazard - Hazard indicator"}
        ]
    },
    
    # -------------------------------------------------------------------------
    # ROW 1: SCORE/CURRENCY/COLLECTIBLES
    # -------------------------------------------------------------------------
    "score": {
        "row": 1,
        "icons": [
            {"name": "chip_green", "col": 0, "width": 48, "height": 48, "value": 100, "note": "Green chip - +100 score"},
            {"name": "floppy_purple", "col": 1, "width": 48, "height": 48, "value": 500, "note": "Purple floppy - +500 score"},
            {"name": "medallion", "col": 2, "width": 48, "height": 48, "value": 1000, "note": "Medallion - +1000 score"},
            {"name": "key_orange", "col": 3, "width": 48, "height": 48, "note": "Orange key - Opens doors"},
            {"name": "qlippy_ref", "col": 4, "width": 48, "height": 48, "note": "Qlippy counter reference"}
        ]
    },
    
    # -------------------------------------------------------------------------
    # ROW 2: WONQMODE INDICATORS (6 icons for 6 modes!)
    # -------------------------------------------------------------------------
    "modes": {
        "row": 2,
        "icons": [
            {"name": "mode_lowg", "col": 0, "width": 48, "height": 48, "mode": "low_g"},
            {"name": "mode_glitch", "col": 1, "width": 48, "height": 48, "mode": "glitch"},
            {"name": "mode_speedy", "col": 2, "width": 48, "height": 48, "mode": "speedy_boots"},
            {"name": "mode_mirror", "col": 3, "width": 48, "height": 48, "mode": "mirror"},
            {"name": "mode_bullettime", "col": 4, "width": 48, "height": 48, "mode": "bullet_time"},
            {"name": "mode_junglist", "col": 5, "width": 48, "height": 48, "mode": "junglist"}
        ]
    }
}
```

---

### 2.16 Backgrounds

```python
# =============================================================================
# BACKGROUND IMAGES
# Full-screen parallax backgrounds for each level
# =============================================================================

BACKGROUNDS = {
    "level1": {
        "file": "qq-background1.png",
        "parallax_factor": 0.5,
        "scroll_speed": 0,
        "note": "Industrial factory setting"
    },
    "level2": {
        "file": "qq-background2.png",
        "parallax_factor": 0.5,
        "scroll_speed": 0,
        "note": "Underground caves/sewers"
    },
    "level3": {
        "file": "qq-background3.png",
        "parallax_factor": 0.5,
        "scroll_speed": 0,
        "note": "Cyberpunk cityscape"
    },
    "menu": {
        "file": "qq-background4.png",
        "parallax_factor": 0.0,
        "scroll_speed": 0,
        "note": "Main menu background - static"
    }
}
```

---

## 3. 🎮 GAME CONSTANTS & PHYSICS

### 3.1 Core Constants

```python
# =============================================================================
# CORE GAME CONSTANTS
# These values define the authentic "Keen feel" - DO NOT USE FLOATS FOR POSITIONS!
# =============================================================================

# Display
INTERNAL_WIDTH = 320
INTERNAL_HEIGHT = 200
DISPLAY_SCALE = 4
WINDOW_WIDTH = INTERNAL_WIDTH * DISPLAY_SCALE
WINDOW_HEIGHT = INTERNAL_HEIGHT * DISPLAY_SCALE

# Physics precision (THE CRITICAL INTEGER SYSTEM!)
SUBPIXEL_SCALE = 256  # 1 pixel = 256 sub-pixel units
TILE_SIZE = 32  # Pixels
TILE_SIZE_SUBPIXEL = TILE_SIZE * SUBPIXEL_SCALE  # 8192 units

# Timing
TARGET_FPS = 60
FRAME_TIME_MS = 1000 // TARGET_FPS  # ~16.67ms
PHYSICS_TIMESTEP_MS = 16  # Fixed physics step

# Player physics (all in sub-pixel units per frame!)
PLAYER_ACCEL = 48
PLAYER_FRICTION = 32
PLAYER_MAX_SPEED = 384
PLAYER_JUMP_STRENGTH = -900
PLAYER_GRAVITY = 40
PLAYER_TERMINAL_VELOCITY = 600
PLAYER_SHOOT_COOLDOWN_MS = 250
INVULNERABILITY_MS = 1500

# Camera
CAMERA_DEADZONE_X = 48
CAMERA_DEADZONE_Y = 32
CAMERA_SMOOTH_FACTOR = 0.1
```

### 3.2 Player State Definitions

```python
# =============================================================================
# PLAYER STATE DEFINITIONS
# =============================================================================

from enum import Enum, auto

class PlayerState(Enum):
    # Normal states
    IDLE = "idle"
    RUN = "run"
    JUMP = "jump"
    FALL = "fall"
    SHOOT = "shoot"
    HURT = "hurt"
    DEAD = "dead"
    
    # JumpUpStiQ (pogo) states
    POGO_IDLE = "pogo_idle"
    POGO_JUMP = "pogo_jump"
    POGO_LAND = "pogo_land"
    
    # JettPaQ (jetpack) states
    JETPACK_IDLE = "jetpack_idle"
    JETPACK_THRUST = "jetpack_thrust"
    JETPACK_HOVER = "jetpack_hover"
    JETPACK_FALL = "jetpack_fall"


class PowerupType(Enum):
    NONE = "none"
    JUMPUPSTIQ = "jumpupstiq"
    JETTPAQ = "jettpaq"


class EnemyState(Enum):
    IDLE = "idle"
    PATROL = "patrol"
    CHASE = "chase"
    ATTACK = "attack"
    HURT = "hurt"
    DEAD = "dead"
```

---

## 4. 🌀 WONQMODES SYSTEM

### 4.1 WoNQmode Definitions

```python
# =============================================================================
# WONQMODES - Gameplay modifiers that can be toggled
# Each mode has a hook system for modifying game behavior
# =============================================================================

WONQMODES = {
    # -------------------------------------------------------------------------
    # LOW-G MODE - Reduced gravity for floaty jumps
    # -------------------------------------------------------------------------
    "low_g": {
        "name": "LowGMode",
        "display_name": "Low-G",
        "icon": "mode_lowg",
        "description": "Gravity reduced by 50% - float like you're on the moon!",
        "hooks": {
            "modify_physics": True,
            "pre_update": False,
            "post_update": False,
            "on_render": False
        },
        "config": {
            "gravity_multiplier": 0.5,
            "jump_multiplier": 1.0,
            "terminal_velocity_multiplier": 0.7
        }
    },
    
    # -------------------------------------------------------------------------
    # GLITCH MODE - Visual corruption effects
    # -------------------------------------------------------------------------
    "glitch": {
        "name": "GlitchMode",
        "display_name": "Glitch",
        "icon": "mode_glitch",
        "description": "Screen shake, sprite jitter, chromatic aberration!",
        "hooks": {
            "modify_physics": False,
            "pre_update": False,
            "post_update": False,
            "on_render": True
        },
        "config": {
            "shake_intensity": 3,
            "shake_frequency": 0.1,
            "jitter_range": 2,
            "chromatic_offset": 2,
            "scanline_opacity": 0.3
        }
    },
    
    # -------------------------------------------------------------------------
    # SPEEDY BOOTS MODE - Increased speed
    # -------------------------------------------------------------------------
    "speedy_boots": {
        "name": "SpeedyBootsMode",
        "display_name": "Speedy",
        "icon": "mode_speedy",
        "description": "2x acceleration and max speed - GOTTA GO FAST!",
        "hooks": {
            "modify_physics": True,
            "pre_update": False,
            "post_update": False,
            "on_render": False
        },
        "config": {
            "accel_multiplier": 2.0,
            "max_speed_multiplier": 2.0,
            "friction_multiplier": 1.5
        }
    },
    
    # -------------------------------------------------------------------------
    # MIRROR MODE - Horizontal flip
    # -------------------------------------------------------------------------
    "mirror": {
        "name": "MirrorMode",
        "display_name": "Mirror",
        "icon": "mode_mirror",
        "description": "Everything is horizontally flipped - LEFT IS RIGHT!",
        "hooks": {
            "modify_physics": False,
            "pre_update": True,
            "post_update": False,
            "on_render": True
        },
        "config": {
            "flip_input": True,
            "flip_render": True
        }
    },
    
    # -------------------------------------------------------------------------
    # BULLET TIME MODE - Slow motion
    # -------------------------------------------------------------------------
    "bullet_time": {
        "name": "BulletTimeMode",
        "display_name": "Bullet Time",
        "icon": "mode_bullettime",
        "description": "Time slows to 30% - Matrix style!",
        "hooks": {
            "modify_physics": True,
            "pre_update": True,
            "post_update": False,
            "on_render": True
        },
        "config": {
            "time_scale": 0.3,
            "player_time_scale": 0.6,
            "color_desaturation": 0.3,
            "motion_blur": True
        }
    },
    
    # -------------------------------------------------------------------------
    # JUNGLIST MODE - 174 BPM synced visual pulses!
    # -------------------------------------------------------------------------
    "junglist": {
        "name": "JunglistMode",
        "display_name": "Junglist",
        "icon": "mode_junglist",
        "description": "Visual pulses synced to 174 BPM - DRUM AND BASS!",
        "hooks": {
            "modify_physics": False,
            "pre_update": True,
            "post_update": True,
            "on_render": True
        },
        "config": {
            "bpm": 174,
            "beat_interval_ms": 345,
            "pulse_color": (255, 215, 0),
            "pulse_intensity": 0.4,
            "bass_drop_shake": True,
            "snare_flash": True
        }
    }
}
```

---

## 5. 📦 COMPLETE DEPENDENCY GRAPH

```
game/
├── shared/                      # LAYER 0: NO external game imports
│   ├── __init__.py
│   ├── constants.py            # All game constants from Section 3
│   ├── sprite_data.py          # ALL sprite mappings from Section 2
│   ├── powerup_data.py         # Powerup configurations
│   ├── wonqmode_data.py        # WoNQmode definitions from Section 4
│   ├── exceptions.py           # GameException hierarchy
│   ├── types.py                # Vec2i, Rect, enums from Section 3.2
│   └── config.py               # Config loading utilities
│
├── core/                        # LAYER 1: Depends on shared ONLY
│   ├── __init__.py
│   ├── engine.py               # Main loop, scene manager, fixed-timestep
│   ├── scene.py                # Base Scene class
│   ├── camera.py               # Viewport, parallax backgrounds
│   ├── resources.py            # SpriteSheet parser, Animation class
│   ├── input.py                # Keyboard state, action mapping
│   ├── time.py                 # Delta time, global time_scale
│   └── particles.py            # Particle system for effects
│
├── world/                       # LAYER 2: Depends on shared, core
│   ├── __init__.py
│   ├── tiles.py                # TileSet, TileMap from tileset regions
│   ├── physics.py              # Integer physics integration
│   ├── collision.py            # AABB collision, tile collision, slide resolution
│   ├── level_loader.py         # JSON level parsing
│   └── entities.py             # Base entity interfaces
│
├── actors/                      # LAYER 3: Depends on shared, core, world
│   ├── __init__.py
│   ├── player.py               # Player with state machine
│   ├── player_states/          # State pattern for movement modes
│   │   ├── __init__.py
│   │   ├── base_state.py       # PlayerStateBase ABC
│   │   ├── normal_state.py     # Default movement (idle/run/jump/fall)
│   │   ├── jumpupstiq_state.py # Pogo stick physics
│   │   └── jettpaq_state.py    # Jetpack flight physics
│   ├── smoke_overlay.py        # Smoke Q animation overlay
│   ├── projectile.py           # Bullets (player & enemy)
│   └── enemies/
│       ├── __init__.py
│       ├── base_enemy.py       # BaseEnemy ABC with Think function
│       ├── walqer_bot.py       # Patrol + shoot AI
│       ├── jumper_drqne.py     # Jump AI
│       ├── qortana_halo.py     # Follow + zap AI
│       ├── qlippy.py           # Annoy + block AI
│       └── briq_beaver.py      # Throw briQ AI
│
├── objects/                     # LAYER 3: Depends on shared, core, world
│   ├── __init__.py
│   ├── collectible.py          # Score items (chip, floppy, medallion)
│   ├── powerup_pickup.py       # Base powerup pickup
│   ├── jumpupstiq_pickup.py    # Pogo stick pickup
│   ├── jettpaq_pickup.py       # Jetpack pickup
│   ├── door.py                 # Locked doors (need key)
│   ├── exit_zone.py            # Level completion trigger
│   └── hazard.py               # Hazard tiles (spikes, acid, lasers)
│
├── modes/                       # LAYER 4: Depends on shared, core
│   ├── __init__.py
│   ├── base_mode.py            # WoNQMode ABC with hooks
│   ├── registry.py             # ModeRegistry - manages active modes
│   ├── low_g_mode.py           # Gravity modifier
│   ├── glitch_mode.py          # Visual corruption
│   ├── mirror_mode.py          # Horizontal flip
│   ├── bullet_time_mode.py     # Slow motion
│   ├── speedy_boots_mode.py    # Speed boost
│   └── junglist_mode.py        # 174 BPM pulses
│
├── ui/                          # LAYER 5: Depends on shared, core
│   ├── __init__.py
│   ├── main_menu.py            # Main menu scene
│   ├── pause_menu.py           # Pause overlay
│   ├── hud.py                  # In-game HUD (health, score, powerup, fuel)
│   ├── level_complete.py       # Level complete screen
│   └── widgets.py              # UI primitives (text, buttons)
│
├── scenes/                      # LAYER 6: Depends on ALL
│   ├── __init__.py
│   ├── menu_scene.py           # Main menu
│   ├── game_scene.py           # Main gameplay
│   └── level_complete_scene.py # Level transition
│
├── assets/                      # SPRITE FILES (placed by user)
│   ├── qq-qommandah-qeen.png
│   ├── qq-smoqin.png
│   ├── qq-jumpupstiq.png
│   ├── qq-qommandah-qeen-jumpupstiq.png
│   ├── qq-jettpaq.png
│   ├── qq-qommandah-qeen-jetpaq.png
│   ├── qq-walqer-bot.png
│   ├── qq-jumper-drqne.png
│   ├── qq-qortana-halo.png
│   ├── qq-qlippy.png
│   ├── qq-briq-beaver.png
│   ├── qq-bullets-explosions.png
│   ├── qq-tilesets.png
│   ├── qq-ui-icons.png
│   ├── qq-background1.png
│   ├── qq-background2.png
│   ├── qq-background3.png
│   └── qq-background4.png
│
├── levels/                      # Level data
│   ├── level01.json
│   ├── level02.json
│   └── level03.json
│
├── config/                      # Configuration files
│   ├── controls.json
│   └── settings.json
│
├── tests/                       # Test files
│   ├── __init__.py
│   ├── test_sprite_loading.py
│   ├── test_physics.py
│   ├── test_collision.py
│   ├── test_player_states.py
│   └── mocks.py
│
├── main.py                      # Entry point
├── requirements.txt             # pygame-ce
└── README.md                    # Documentation
```

---

## 6. 🎯 GLOBAL SUCCESS CRITERIA

Before ANY cycle is marked SUCCESS, ALL of these must pass:

### 6.1 Compilation & Structure
1. ✅ All Python files pass `python -m py_compile <file>`
2. ✅ All imports resolve within the project structure
3. ✅ No circular import dependencies
4. ✅ All `__init__.py` files export appropriate symbols

### 6.2 Sprite Loading
5. ✅ All 18 sprite files load from `ASSET_FILES` registry
6. ✅ Frame extraction matches documented coordinates exactly
7. ✅ Animations cycle correctly at specified FPS
8. ✅ Sprites flip horizontally when `facing_right = False`

### 6.3 Core Engine
9. ✅ Fixed-timestep loop runs at stable 60Hz
10. ✅ Scene manager switches scenes without memory leaks
11. ✅ Camera follows player with smooth scrolling
12. ✅ Parallax backgrounds scroll at correct factor

### 6.4 Physics (CRITICAL!)
13. ✅ Physics uses INTEGER math ONLY (no floats for positions/velocities)
14. ✅ Sub-pixel precision: 1 pixel = 256 units enforced
15. ✅ Player accelerates and decelerates with correct inertia
16. ✅ Gravity applies correctly (40 units/frame)
17. ✅ Tile collision produces SLIDE behavior (not stop/stick)

### 6.5 Player States
18. ✅ Normal state: idle → run → jump → fall transitions work
19. ✅ Shooting triggers shoot animation and spawns projectile
20. ✅ Hurt state triggers on damage with invulnerability frames
21. ✅ Dead state triggers when HP reaches 0

### 6.6 Smoke Overlay
22. ✅ Smoke overlay loads from `qq-smoqin.png`
23. ✅ Smoke plays continuously during idle/run states
24. ✅ Smoke forms Q-shaped rings in second phase
25. ✅ Smoke disabled during hurt/dead/shooting states

### 6.7 Powerup System
26. ✅ JumpUpStiQ pickup grants pogo mode
27. ✅ Pogo mode: continuous bouncing, hold for higher jump (BASS BLAST!)
28. ✅ JettPaQ pickup grants jetpack mode
29. ✅ Jetpack mode: thrust/hover/fall with fuel management
30. ✅ Taking damage removes active powerup (returns to normal)
31. ✅ Powerup state correctly switches player sprite sheet

### 6.8 Enemies
32. ✅ WalQer Bot: patrols, turns at edges/walls, shoots at player
33. ✅ Jumper DrQne: jumps periodically or when player approaches
34. ✅ Qortana Halo: follows player, zaps when in range (2 damage!)
35. ✅ Qlippy: moves around, spawns dialogue that blocks movement (0 damage!)
36. ✅ BriQ Beaver: throws arcing briQ projectiles at player
37. ✅ All enemies play death animation and drop score

### 6.9 WoNQmodes
38. ✅ Mode registry toggles modes on/off
39. ✅ Low-G Mode: gravity reduced by 50%
40. ✅ Glitch Mode: screen shake and sprite jitter
41. ✅ Mirror Mode: horizontal flip of input and render
42. ✅ Bullet Time Mode: time scale 0.3x
43. ✅ Speedy Boots Mode: 2x acceleration and max speed
44. ✅ Junglist Mode: visual pulses at 174 BPM (beat interval ~345ms)
45. ✅ Active mode icons display in HUD

### 6.10 UI & Scenes
46. ✅ Main menu displays on launch with background4
47. ✅ Pause menu accessible during gameplay
48. ✅ HUD shows: health hearts, score, active powerup, fuel gauge (if jetpack)
49. ✅ Level complete screen shows between levels
50. ✅ Game over screen on player death

### 6.11 Level System
51. ✅ Levels load from JSON format
52. ✅ Tile collision layer parsed correctly
53. ✅ Entity spawns (player, enemies, pickups) work
54. ✅ Exit zone triggers level transition
55. ✅ Can play through all 3 levels end-to-end

### 6.12 Final Integration
56. ✅ `python -m game.main` opens window with main menu
57. ✅ Full game loop: menu → level 1 → level 2 → level 3 → victory
58. ✅ No crashes during normal gameplay

---

## 7. 📋 DETAILED PHASE BREAKDOWN

### PHASE 1: Foundation (Cycles 1-2)

**Deliverables:**
- `shared/__init__.py`
- `shared/constants.py` - All constants from Section 3
- `shared/types.py` - Vec2i, Rect, enums
- `shared/exceptions.py` - GameException hierarchy
- `shared/sprite_data.py` - ALL sprite mappings from Section 2
- `shared/powerup_data.py` - Powerup configurations
- `shared/wonqmode_data.py` - WoNQmode definitions

```python
# 🎯 Golden Path Test: shared/sprite_data.py
from shared.sprite_data import (
    ASSET_FILES, QOMMANDAH_QEEN_FRAMES, SMOQIN_FRAMES,
    JUMPUPSTIQ_PICKUP_FRAMES, QOMMANDAH_QEEN_JUMPUPSTIQ_FRAMES,
    JETTPAQ_PICKUP_FRAMES, QOMMANDAH_QEEN_JETTPAQ_FRAMES,
    WALQER_BOT_FRAMES, JUMPER_DRQNE_FRAMES, QORTANA_HALO_FRAMES,
    QLIPPY_FRAMES, BRIQ_BEAVER_FRAMES, PROJECTILES_FRAMES,
    TILESET_REGIONS, UI_ICONS, BACKGROUNDS
)

# Verify all 18 asset files defined
assert len(ASSET_FILES) == 18
assert ASSET_FILES["player"] == "qq-qommandah-qeen.png"
assert ASSET_FILES["player_smoqin"] == "qq-smoqin.png"
assert ASSET_FILES["player_jumpupstiq"] == "qq-qommandah-qeen-jumpupstiq.png"
assert ASSET_FILES["player_jettpaq"] == "qq-qommandah-qeen-jetpaq.png"

# Verify player animations
assert "idle" in QOMMANDAH_QEEN_FRAMES
assert "run" in QOMMANDAH_QEEN_FRAMES
assert "shoot" in QOMMANDAH_QEEN_FRAMES
assert QOMMANDAH_QEEN_FRAMES["idle"]["frames"] == 4

# Verify smoke overlay
assert "smoke_idle" in SMOQIN_FRAMES
assert "smoke_q_ring" in SMOQIN_FRAMES

# Verify powerup animations
assert "pogo_idle" in QOMMANDAH_QEEN_JUMPUPSTIQ_FRAMES
assert "pogo_jump" in QOMMANDAH_QEEN_JUMPUPSTIQ_FRAMES
assert "jetpack_thrust" in QOMMANDAH_QEEN_JETTPAQ_FRAMES

# Verify all enemy types
assert "idle" in WALQER_BOT_FRAMES
assert "coil" in JUMPER_DRQNE_FRAMES
assert "hover" in QORTANA_HALO_FRAMES
assert "annoy_dialogue" in QLIPPY_FRAMES
assert "briq_projectile" in BRIQ_BEAVER_FRAMES
```

```python
# 🎯 Golden Path Test: shared/constants.py
from shared.constants import (
    SUBPIXEL_SCALE, TILE_SIZE, PLAYER_GRAVITY,
    PLAYER_ACCEL, PLAYER_MAX_SPEED, PLAYER_JUMP_STRENGTH
)

# Verify integer physics constants
assert SUBPIXEL_SCALE == 256
assert isinstance(SUBPIXEL_SCALE, int)
assert TILE_SIZE == 32
assert TILE_SIZE * SUBPIXEL_SCALE == 8192

# Verify physics values are integers
assert isinstance(PLAYER_GRAVITY, int)
assert isinstance(PLAYER_ACCEL, int)
assert isinstance(PLAYER_MAX_SPEED, int)
assert isinstance(PLAYER_JUMP_STRENGTH, int)
```

---

### PHASE 2: Core Engine (Cycles 3-4)

**Deliverables:**
- `core/__init__.py`
- `core/engine.py` - Main loop, scene manager
- `core/scene.py` - Base Scene class
- `core/resources.py` - SpriteSheet parser, Animation class
- `core/input.py` - Keyboard handling
- `core/time.py` - Time management
- `core/camera.py` - Camera with parallax
- `core/particles.py` - Particle system

```python
# 🎯 Golden Path Test: core/resources.py
from core.resources import ResourceManager, SpriteSheet, Animation
from shared.sprite_data import ASSET_FILES, QOMMANDAH_QEEN_FRAMES
import pygame
pygame.init()
pygame.display.set_mode((100, 100))

resources = ResourceManager(assets_path="assets")

# Test sprite sheet loading
player_sheet = resources.load_sprite_sheet("player")
assert player_sheet is not None

# Test animation extraction
idle_anim = player_sheet.get_animation("idle", QOMMANDAH_QEEN_FRAMES["idle"])
assert len(idle_anim.frames) == 4
assert idle_anim.fps == 6

# Test frame retrieval
frame = idle_anim.get_frame(0)
assert isinstance(frame, pygame.Surface)

# Test animation update
idle_anim.update(200)  # 200ms
assert idle_anim._current_frame >= 0
```

```python
# 🎯 Golden Path Test: core/engine.py
from core.engine import Engine
from core.scene import Scene
import pygame
pygame.init()

class TestScene(Scene):
    def __init__(self):
        self.update_count = 0
        self.draw_count = 0
    
    def update(self, dt_ms):
        self.update_count += 1
    
    def draw(self, surface):
        self.draw_count += 1

engine = Engine()
test_scene = TestScene()
engine.scene_manager.push(test_scene)

# Simulate one frame
engine._process_frame()
assert test_scene.update_count == 1
assert test_scene.draw_count == 1
```

---

### PHASE 3: World & Physics (Cycles 5-6)

**Deliverables:**
- `world/__init__.py`
- `world/tiles.py` - TileSet, TileMap
- `world/physics.py` - Integer physics
- `world/collision.py` - AABB, tile collision, slide resolution
- `world/level_loader.py` - JSON level loading
- `world/entities.py` - Base entity interface

```python
# 🎯 Golden Path Test: world/physics.py
from world.physics import PhysicsBody, apply_gravity, apply_friction
from shared.constants import SUBPIXEL_SCALE, PLAYER_GRAVITY

# Create physics body
body = PhysicsBody(pos_x=0, pos_y=0, vel_x=0, vel_y=0)

# Verify integer types
assert isinstance(body.pos_x, int)
assert isinstance(body.pos_y, int)
assert isinstance(body.vel_x, int)
assert isinstance(body.vel_y, int)

# Apply gravity
apply_gravity(body, PLAYER_GRAVITY)
assert body.vel_y == PLAYER_GRAVITY
assert isinstance(body.vel_y, int)

# Apply friction
body.vel_x = 100
apply_friction(body, 32)
assert body.vel_x == 68  # 100 - 32
assert isinstance(body.vel_x, int)
```

```python
# 🎯 Golden Path Test: world/collision.py
from world.collision import check_tile_collision, resolve_slide
from shared.types import Rect

# Test AABB collision
rect_a = Rect(0, 0, 64, 64)
rect_b = Rect(32, 32, 64, 64)
rect_c = Rect(100, 100, 64, 64)

assert rect_a.collides_with(rect_b) == True
assert rect_a.collides_with(rect_c) == False

# Test slide resolution (should zero velocity in collision axis, allow other axis)
# Moving right, hit wall -> vel_x = 0, vel_y unchanged
vel_x, vel_y = 100, 50
new_vel_x, new_vel_y = resolve_slide(vel_x, vel_y, collision_axis='x')
assert new_vel_x == 0
assert new_vel_y == 50
```

---

### PHASE 4: Player & Smoke Overlay (Cycles 7-8)

**Deliverables:**
- `actors/__init__.py`
- `actors/player.py` - Player with state machine
- `actors/smoke_overlay.py` - Smoke Q animation
- `actors/player_states/__init__.py`
- `actors/player_states/base_state.py`
- `actors/player_states/normal_state.py`

```python
# 🎯 Golden Path Test: actors/smoke_overlay.py
from actors.smoke_overlay import SmokeOverlay
from core.resources import ResourceManager
from shared.sprite_data import SMOQIN_CONFIG
import pygame
pygame.init()
pygame.display.set_mode((100, 100))

resources = ResourceManager(assets_path="assets")
smoke = SmokeOverlay(resources)

# Verify loaded from qq-smoqin.png
assert smoke._sprite_sheet is not None
assert "smoke_idle" in smoke._animations
assert "smoke_q_ring" in smoke._animations

# Test configuration
assert smoke.always_active == SMOQIN_CONFIG["always_active"]

# Test state checking
assert smoke.should_play("idle") == True
assert smoke.should_play("run") == True
assert smoke.should_play("hurt") == False
assert smoke.should_play("dead") == False

# Test animation cycling
smoke.update(2000)  # Half cycle
assert smoke._in_q_ring_phase == True
smoke.update(2000)  # Full cycle
assert smoke._in_q_ring_phase == False
```

```python
# 🎯 Golden Path Test: actors/player.py
from actors.player import Player
from core.resources import ResourceManager
from core.input import InputHandler
from shared.types import Vec2i, PlayerState, PowerupType
import pygame
pygame.init()
pygame.display.set_mode((100, 100))

resources = ResourceManager(assets_path="assets")
player = Player(spawn_pos=Vec2i(0, 0), resources=resources)

# Verify initial state
assert player.state == PlayerState.IDLE
assert player.active_powerup == PowerupType.NONE
assert player.hp == 3

# Verify smoke overlay exists
assert player._smoke_overlay is not None

# Test state transitions
player.vel_x = 100
player._update_state()
assert player.state == PlayerState.RUN

player.vel_y = -100
player.on_ground = False
player._update_state()
assert player.state == PlayerState.JUMP

# Test damage
player.take_damage(1)
assert player.hp == 2
assert player.is_invulnerable == True
assert player.state == PlayerState.HURT
```

---

### PHASE 5: Powerup States (Cycles 9-10)

**Deliverables:**
- `actors/player_states/jumpupstiq_state.py`
- `actors/player_states/jettpaq_state.py`
- `objects/__init__.py`
- `objects/powerup_pickup.py`
- `objects/jumpupstiq_pickup.py`
- `objects/jettpaq_pickup.py`

```python
# 🎯 Golden Path Test: actors/player_states/jumpupstiq_state.py
from actors.player_states.jumpupstiq_state import JumpUpStiQState
from actors.player import Player
from core.resources import ResourceManager
from shared.types import Vec2i
from shared.sprite_data import JUMPUPSTIQ_PHYSICS
import pygame
pygame.init()
pygame.display.set_mode((100, 100))

resources = ResourceManager(assets_path="assets")
player = Player(spawn_pos=Vec2i(0, 0), resources=resources)
state = JumpUpStiQState(player, resources)

# Verify sprite sheet loaded
assert "pogo_idle" in state._animations
assert "pogo_jump" in state._animations
assert "pogo_land" in state._animations

# Test continuous bounce (THE POGO FEEL!)
state.enter()
player.on_ground = True
state.update(16)
assert player.vel_y < 0  # Should have auto-bounced!
assert player.vel_y == JUMPUPSTIQ_PHYSICS["normal_bounce"]

# Test BASS BLAST (hold for higher!)
player.on_ground = True
state._holding_jump = True
state.update(16)
expected_jump = JUMPUPSTIQ_PHYSICS["jump_strength"] - JUMPUPSTIQ_PHYSICS["max_hold_bonus"]
assert player.vel_y == expected_jump
```

```python
# 🎯 Golden Path Test: actors/player_states/jettpaq_state.py
from actors.player_states.jettpaq_state import JettPaQState
from actors.player import Player
from core.resources import ResourceManager
from shared.types import Vec2i
from shared.sprite_data import JETTPAQ_PHYSICS
import pygame
pygame.init()
pygame.display.set_mode((100, 100))

resources = ResourceManager(assets_path="assets")
player = Player(spawn_pos=Vec2i(0, 0), resources=resources)
state = JettPaQState(player, resources)

# Verify sprite sheet loaded
assert "jetpack_idle" in state._animations
assert "jetpack_thrust" in state._animations
assert "jetpack_hover" in state._animations
assert "jetpack_fall" in state._animations

# Test fuel system
assert state.fuel == state.max_fuel

# Test thrust
state.enter()
state._thrusting = True
old_fuel = state.fuel
state.update(16)
assert state.fuel < old_fuel  # Fuel consumed
assert player.vel_y < 0  # Thrust applied

# Test hover gravity (reduced)
state._thrusting = False
player.vel_y = 0
state.update(16)
assert player.vel_y == JETTPAQ_PHYSICS["hover_gravity"]
```

---

### PHASE 6: Enemies (Cycles 11-12)

**Deliverables:**
- `actors/enemies/__init__.py`
- `actors/enemies/base_enemy.py`
- `actors/enemies/walqer_bot.py`
- `actors/enemies/jumper_drqne.py`
- `actors/enemies/qortana_halo.py`
- `actors/enemies/qlippy.py`
- `actors/enemies/briq_beaver.py`
- `actors/projectile.py`

```python
# 🎯 Golden Path Test: actors/enemies/base_enemy.py
from actors.enemies.base_enemy import BaseEnemy
from shared.types import Vec2i, EnemyState

class TestEnemy(BaseEnemy):
    def think(self, dt_ms, level, player_pos=None):
        pass

enemy = TestEnemy(
    pos=Vec2i(8192, 8192),
    hp=3,
    damage=1,
    width=64 * 256,
    height=64 * 256
)

assert enemy.hp == 3
assert enemy.is_alive == True
assert enemy.state == EnemyState.IDLE

enemy.take_damage(2)
assert enemy.hp == 1
assert enemy.state == EnemyState.HURT

enemy.take_damage(1)
assert enemy.hp == 0
assert enemy.is_alive == False
assert enemy.state == EnemyState.DEAD
```

```python
# 🎯 Golden Path Test: actors/enemies/qlippy.py (unique behavior!)
from actors.enemies.qlippy import Qlippy
from core.resources import ResourceManager
from shared.types import Vec2i
from shared.sprite_data import QLIPPY_CONFIG
import pygame
pygame.init()
pygame.display.set_mode((100, 100))

resources = ResourceManager(assets_path="assets")
qlippy = Qlippy(pos=Vec2i(8192, 8192), resources=resources)

# Verify NO DAMAGE
assert qlippy.damage == 0
assert QLIPPY_CONFIG["damage"] == 0

# Verify annoy behavior
assert qlippy.is_annoying == False

# Trigger annoy
qlippy._annoy_timer = 0
qlippy.think(16, None, None)
assert qlippy.is_annoying == True
assert qlippy.get_blocking_rect() is not None

# Verify blocking duration
qlippy._dialogue_timer = 0
qlippy.think(16, None, None)
assert qlippy.is_annoying == False
assert qlippy.get_blocking_rect() is None
```

```python
# 🎯 Golden Path Test: actors/enemies/qortana_halo.py (zap attack!)
from actors.enemies.qortana_halo import QortanaHalo
from core.resources import ResourceManager
from shared.types import Vec2i
from shared.sprite_data import QORTANA_HALO_CONFIG
import pygame
pygame.init()
pygame.display.set_mode((100, 100))

resources = ResourceManager(assets_path="assets")
qortana = QortanaHalo(pos=Vec2i(8192, 8192), resources=resources)

# Verify high damage zap
assert qortana.zap_damage == 2
assert QORTANA_HALO_CONFIG["zap_damage"] == 2

# Verify follows player
assert qortana.follows_player == True

# Test zap trigger
qortana._player_distance = 100  # Within zap_range (128)
qortana._zap_timer = 0
qortana.think(16, None, Vec2i(8192 + 100 * 256, 8192))
assert qortana._state == "attacking"
assert qortana.is_zapping() == True
```

---

### PHASE 7: WoNQmodes & UI (Cycles 13-14)

**Deliverables:**
- `modes/__init__.py`
- `modes/base_mode.py`
- `modes/registry.py`
- `modes/low_g_mode.py`
- `modes/glitch_mode.py`
- `modes/mirror_mode.py`
- `modes/bullet_time_mode.py`
- `modes/speedy_boots_mode.py`
- `modes/junglist_mode.py`
- `ui/__init__.py`
- `ui/hud.py`
- `ui/main_menu.py`
- `ui/pause_menu.py`

```python
# 🎯 Golden Path Test: modes/junglist_mode.py (signature mode!)
from modes.junglist_mode import JunglistMode
from shared.wonqmode_data import WONQMODES

mode = JunglistMode()

# Verify BPM configuration
assert mode.bpm == 174
assert mode.beat_interval_ms == 345  # 60000 / 174 ≈ 345

# Verify hooks
config = WONQMODES["junglist"]
assert config["hooks"]["on_render"] == True
assert config["hooks"]["pre_update"] == True
assert config["hooks"]["post_update"] == True

# Test beat detection
mode._elapsed_ms = 0
assert mode.is_on_beat() == True

mode._elapsed_ms = 172  # Half beat
assert mode.is_on_beat() == False

mode._elapsed_ms = 345  # Full beat
assert mode.is_on_beat() == True
```

```python
# 🎯 Golden Path Test: ui/hud.py
from ui.hud import HUD
from core.resources import ResourceManager
import pygame
pygame.init()
pygame.display.set_mode((100, 100))

resources = ResourceManager(assets_path="assets")
hud = HUD(resources)

# Verify icons loaded
assert hud._heart_icon is not None
assert hud._shield_icon is not None
assert len(hud._mode_icons) == 6

# Test fuel gauge (for jetpack)
class MockPlayer:
    hp = 2
    max_hp = 3
    score = 1500
    active_powerup = "jettpaq"

class MockJetpackState:
    fuel_percent = 0.75

surface = pygame.Surface((320, 200))
hud.draw(surface, MockPlayer(), [], jetpack_state=MockJetpackState())
# Should display: 2 hearts, score 1500, fuel gauge at 75%
```

---

### PHASE 8: Scenes & Integration (Cycles 15-16)

**Deliverables:**
- `scenes/__init__.py`
- `scenes/menu_scene.py`
- `scenes/game_scene.py`
- `scenes/level_complete_scene.py`
- `levels/level01.json`
- `levels/level02.json`
- `levels/level03.json`
- `main.py`
- `requirements.txt`
- `README.md`

```python
# 🎯 Golden Path Test: main.py
import subprocess
import sys

# Test that game launches without crash
result = subprocess.run(
    [sys.executable, "-c", "from game.main import Game; g = Game(); g.quit()"],
    capture_output=True,
    timeout=5
)
assert result.returncode == 0
```

---

## 8. 📄 LEVEL JSON FORMAT

```json
{
    "name": "Level 01 - Industrial Complex",
    "background": "background1",
    "music": "level01.ogg",
    "width": 100,
    "height": 20,
    "tile_size": 32,
    
    "layers": {
        "background": [
            [0, 0, 0, 0, 0, ...],
            ...
        ],
        "collision": [
            [1, 1, 1, 0, 0, 40, 40, 0, 1, 1, ...],
            ...
        ],
        "foreground": [
            [0, 0, 0, 0, 0, ...],
            ...
        ]
    },
    
    "entities": {
        "player_spawn": {"x": 3, "y": 17},
        "exit_zone": {"x": 95, "y": 17, "width": 2, "height": 3},
        
        "enemies": [
            {"type": "walqer_bot", "x": 20, "y": 17},
            {"type": "walqer_bot", "x": 45, "y": 17},
            {"type": "jumper_drqne", "x": 30, "y": 15},
            {"type": "qortana_halo", "x": 60, "y": 10},
            {"type": "qlippy", "x": 70, "y": 12},
            {"type": "briq_beaver", "x": 85, "y": 17}
        ],
        
        "pickups": [
            {"type": "chip_green", "x": 10, "y": 15},
            {"type": "chip_green", "x": 25, "y": 12},
            {"type": "floppy_purple", "x": 50, "y": 10},
            {"type": "key_orange", "x": 75, "y": 17},
            {"type": "jumpupstiq", "x": 35, "y": 8},
            {"type": "jettpaq", "x": 55, "y": 5}
        ],
        
        "doors": [
            {"x": 80, "y": 17, "requires_key": true}
        ]
    },
    
    "wonqmodes_available": ["low_g", "glitch", "junglist"]
}
```

---

## 9. 🚀 EXECUTION RECOMMENDATIONS

### 9.1 Complexity Analysis

This tasq is **MASSIVE** with:
- **~100KB** of specifications
- **~70+ files** to generate
- **Player state machine** with 3 movement modes
- **Smoke overlay system** (independent animation layer)
- **Full powerup collection + loss mechanics**
- **6 enemy types** with distinct AI behaviors
- **6 WoNQmodes** with hook system
- **Integer sub-pixel physics** (precision-critical!)
- **Full UI system** with HUD, menus, fuel gauge
- **3 playable levels** with JSON format
- **Complete game loop** from menu to victory

### 9.2 Provider Recommendations

| Provider | Model | Sensitivity | Cycles | Config | Reasoning |
|----------|-------|-------------|--------|--------|-----------|
| **DeepSeek** | `deepseek-chat` | **2** | **12** | `b2c12` | ✅ RECOMMENDED - Best balance |
| **Google** | `gemini-2.5-flash` | **2** | **12** | `b2c12` | ✅ FASTEST - Good for iteration |

### 9.3 DeepSeek Chat Configuration

```yaml
# config.yaml for DeepSeek Chat
agents:
  instruqtor:
    provider: deepseek
    model: deepseek-chat
  construqtor:
    provider: deepseek
    model: deepseek-chat
  inspeqtor:
    provider: deepseek
    model: deepseek-chat

options:
  briq_sensitivity: 2
  auto_cycle_limit: 12
  cheqpoint: false
  mode: program
```

```bash
./qonqrete.sh run -b 2 --auto --mode program
```

**Why b2c12 for DeepSeek:**
- sens=2 = **20-30 briqs per cycle** (High Granularity)
- Player state machine needs PRECISE implementation
- Smoke overlay timing must be exact
- Powerup physics (pogo bounce, jetpack thrust) are complex
- 12 cycles is sufficient for this model's capabilities
- **Estimated briqs:** ~240-360 total
- **Est. completion time:** 45-60 minutes
- **Est. cost:** $0.50-1.00

### 9.4 Gemini 2.5 Flash Configuration

```yaml
# config.yaml for Gemini Flash
agents:
  instruqtor:
    provider: google
    model: gemini-2.5-flash
  construqtor:
    provider: google
    model: gemini-2.5-flash
  inspeqtor:
    provider: google
    model: gemini-2.5-flash

options:
  briq_sensitivity: 2
  auto_cycle_limit: 12
  cheqpoint: false
  mode: program
```

```bash
./qonqrete.sh run -b 2 --auto --mode program
```

**Why b2c12 for Gemini Flash:**
- sens=2 = **20-30 briqs per cycle** (High Granularity)
- Flash is FAST but can miss details - fine briqs help
- 12 cycles should be sufficient with 1M context window
- Flash handles game logic well
- **Estimated briqs:** ~240-360 total
- **Est. completion time:** 25-40 minutes (FAST!)
- **Est. cost:** $0.80-1.50

### 9.5 Expected Cycle Progression

```
Cycle 1:    shared/constants.py, shared/types.py, shared/exceptions.py
Cycle 2:    shared/sprite_data.py (ALL sprite mappings!)
Cycle 3:    core/engine.py, core/scene.py, core/time.py
Cycle 4:    core/resources.py, core/input.py, core/camera.py
Cycle 5:    world/physics.py, world/collision.py
Cycle 6:    world/tiles.py, world/level_loader.py
Cycle 7:    actors/smoke_overlay.py, actors/player.py (base)
Cycle 8:    actors/player_states/* (normal, jumpupstiq, jettpaq)
Cycle 9:    objects/powerup_pickup.py, jumpupstiq_pickup.py, jettpaq_pickup.py
Cycle 10:   actors/enemies/* (all 6 enemy types)
Cycle 11:   modes/* (all 6 WoNQmodes)
Cycle 12:   ui/*, scenes/*, levels/*.json, main.py
```

---

## 10. 📁 COMPLETE ASSET CHECKLIST

Place these files in `qodeyard/assets/` after QonQrete completes the build:

```
✅ qq-qommandah-qeen.png             - Base player (6 animation states)
✅ qq-smoqin.png                     - Smoke Q overlay (continuous smoking!)
✅ qq-jumpupstiq.png                 - Pogo pickup item
✅ qq-qommandah-qeen-jumpupstiq.png  - Player ON pogo (BASS BLAST!)
✅ qq-jettpaq.png                    - Jetpack pickup item
✅ qq-qommandah-qeen-jetpaq.png      - Player WITH jetpack (FLIGHT!)
✅ qq-walqer-bot.png                 - Walker Bot enemy
✅ qq-jumper-drqne.png               - Jumper Drone enemy
✅ qq-qortana-halo.png               - Qortana Halo enemy (ZAP!)
✅ qq-qlippy.png                     - Qlippy enemy (ANNOYING!)
✅ qq-briq-beaver.png                - BriQ Beaver enemy (throws briQs!)
✅ qq-bullets-explosions.png         - Projectiles and effects
✅ qq-tilesets.png                   - Ground, platforms, hazards, decor
✅ qq-ui-icons.png                   - Health, score, mode icons
✅ qq-background1.png                - Level 1 background
✅ qq-background2.png                - Level 2 background
✅ qq-background3.png                - Level 3 background
✅ qq-background4.png                - Menu background

Total: 18 sprite files
```

---

## 11. 🎮 GAMEPLAY SUMMARY

### Player Mechanics
- **Move:** Arrow keys / WASD
- **Jump:** Space / Z
- **Shoot:** X / Ctrl
- **Pause:** Escape

### Normal Mode
- Standard run, jump, shoot mechanics
- Smoke Q overlay during idle/run
- 3 HP, invulnerability on damage

### JumpUpStiQ Mode (Pogo)
- Collect the subwoofer pogo stick
- **CONTINUOUS BOUNCING** - can't stop!
- Hold JUMP for **BASS BLAST** super jump
- Colorful explosion particle effect
- Lose on damage

### JettPaQ Mode (Jetpack)
- Collect the boombox jetpack
- Hold JUMP to **THRUST** upward
- Release for **HOVER** (slow fall)
- Fuel gauge - regenerates when grounded
- Can still shoot while flying!
- Lose on damage

### Enemies
| Enemy | Behavior | Damage | HP |
|-------|----------|--------|-----|
| WalQer Bot | Patrol + shoot | 1 | 3 |
| Jumper DrQne | Periodic jumping | 1 | 2 |
| Qortana Halo | Follow + ZAP | 2 (zap!) | 4 |
| Qlippy | Dialogue blocks | 0 (annoying!) | 1 |
| BriQ Beaver | Throws arcing briQs | 1 | 3 |

### WoNQmodes
| Mode | Effect | Icon |
|------|--------|------|
| Low-G | 50% gravity | mode_lowg |
| Glitch | Screen shake, jitter | mode_glitch |
| Mirror | Horizontal flip | mode_mirror |
| Bullet Time | 0.3x time scale | mode_bullettime |
| Speedy Boots | 2x speed | mode_speedy |
| Junglist | 174 BPM pulses | mode_junglist |

---

## 12. 🏆 FINAL NOTES

This tasq represents the **COMPLETE, DEFINITIVE BUILD SPECIFICATION** for QommandahQeen. It contains:

- **Every sprite mapping** with exact frame coordinates
- **Every physics constant** as integers
- **Every enemy behavior** specification
- **Every WoNQmode** configuration
- **Complete project structure** with dependency graph
- **Golden Path Tests** for all critical components
- **Level JSON format** for creating content

When QonQrete completes this build and you drop the sprite assets into the `assets/` folder, you will have a **FULLY PLAYABLE** Commander Keen-inspired platformer with:

- Custom QonQrete aesthetic
- Subwoofer pogo stick powerup
- Boombox jetpack powerup
- Continuous smoke Q overlay
- 6 unique enemies
- 6 gameplay-modifying WoNQmodes
- 3 playable levels

**LET'S GOOOOO!!! 🏗️🎮🔊💨**

---

*QommandahQeen MAQZIMUM - The Complete WoNQ Platformer Engine*
*Full Sprite Integration • Powerup System • Smoke Q Overlay*
*JumpUpStiQ Pogo • JettPaQ Jetpack • 6 Enemies • 6 WoNQmodes*
*Built with QonQrete AgentiQ OrQhestration*
*KABOOMAGE!!! 💥*
