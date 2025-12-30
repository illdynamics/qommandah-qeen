# 🎮 QommandahQeen MAQZIMUM v0.1.0-alpha

> **Commander Keen-Inspired Platformer with QonQrete Aesthetics**
> Built with QonQrete AgentiQ OrQhestration

## 🚀 Quick Start

```bash
# Install dependencies
pip install pygame-ce

# Run the game
python main.py
```

## 🎯 Features

### Player Mechanics
- **Normal Mode**: Run, jump, shoot with smoke Q overlay
- **JumpUpStiQ Mode**: Subwoofer pogo stick with BASS BLAST!
  - Continuous bouncing - can't stop!
  - Hold JUMP for extra height
  - Colorful explosion particles
- **JettPaQ Mode**: Boombox jetpack for flight!
  - Hold JUMP to thrust upward
  - Release for hover (slow fall)
  - Fuel gauge that regenerates when grounded

### Enemies (6 Types)
| Enemy | Behavior | Damage | HP |
|-------|----------|--------|-----|
| WalQer Bot | Patrol + shoot | 1 | 3 |
| Jumper DrQne | Periodic jumping | 1 | 2 |
| Qortana Halo | Follow + ZAP | **2** | 4 |
| Qlippy | Dialogue blocks | 0 | 1 |
| BriQ Beaver | Throws arcing briQs | 1 | 3 |

### WoNQmodes (6 Modes)
| Mode | Effect |
|------|--------|
| Low-G | 50% gravity |
| Glitch | Screen shake, jitter |
| Mirror | Horizontal flip |
| Bullet Time | 0.3x time scale |
| Speedy Boots | 2x speed |
| Junglist | 174 BPM pulses |

## 🎨 Assets

All sprites in `assets/`:
- `qq-qommandah-qeen.png` - Base player (6 states)
- `qq-smoqin.png` - Smoke Q overlay (THE SIGNATURE!)
- `qq-qommandah-qeen-jumpupstiq.png` - Player on pogo
- `qq-qommandah-qeen-jetpaq.png` - Player with jetpack
- `qq-jumpupstiq.png` / `qq-jettpaq.png` - Powerup pickups
- `qq-walqer-bot.png` through `qq-briq-beaver.png` - Enemies
- `qq-tilesets.png` - World tiles
- `qq-ui-icons.png` - HUD elements
- `qq-background1-4.png` - Parallax backgrounds

## 🔧 Technical Details

### Integer Physics System
- **SUBPIXEL_SCALE**: 256 (1 pixel = 256 units)
- All positions/velocities use integers for authentic "Keen feel"
- Fixed timestep at 60 FPS

### Project Structure
```
qommandah-qeen-v0.1.0-alpha/
├── actors/           # Player, enemies, projectiles
│   ├── enemies/      # All 6 enemy types
│   └── player_states/ # Normal, JumpUpStiQ, JettPaQ
├── core/             # Engine, resources, input, time
├── world/            # Physics, collision, tiles
├── modes/            # 6 WoNQmodes
├── objects/          # Collectibles, powerups, hazards
├── scenes/           # Menu, game, level complete
├── ui/               # HUD, menus
├── shared/           # Constants, types, sprite data
├── levels/           # Level JSON files
└── assets/           # All sprite assets
```

## 🎮 Controls

| Key | Action |
|-----|--------|
| Arrow Keys / WASD | Move |
| Space / Z | Jump |
| X / Ctrl | Shoot |
| Escape | Pause |

## 📜 License

Built with 💜 using QonQrete AgentiQ OrQhestration

**KABOOMAGE!!! 💥**
