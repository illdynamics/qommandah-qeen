# 🎮 Qommandah Qeen
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](LICENSE)

![Splash](assets/qq-main-menu.png)

> **Commander Keen-Inspired Platformer with QonQrete Aesthetics**
> Built with QonQrete AgentiQ OrQhestration

## 🚀 Quick Start

```bash
# Install dependencies
pip install pygame-ce

# Run the game
python main.py

# Toggle fullscreen with F11
```

## ✨ v0.2.1-alpha Changelog

- **BUG FIX**: Fixed WalqerBot/BriqBeaver crashes (self.speed -> self._speed)
- **BUG FIX**: Proper fullscreen scaling with game surface approach
- **FEATURE**: Background rendering with parallax scrolling
- **FEATURE**: Added HoverSquid enemy type (6th enemy complete!)
- **IMPROVEMENT**: All enemies now use consistent property accessors

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
| WalQer Bot | Patrol + shoot | 10 | 50 |
| Jumper DrQne | Periodic jumping | 15 | 60 |
| Qortana Halo | Follow + ZAP | 15 | 60 |
| Qlippy | Dialogue blocks | 10 | 30 |
| BriQ Beaver | Throws arcing briQs | 20 | 80 |
| Hover Squid | Floating swoop attack | 15 | 40 |

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
qommandah-qeen-v0.2.1-alpha/
├── actors/           # Player, enemies, projectiles
│   ├── enemies/      # All 6 enemy types (incl. HoverSquid!)
│   └── player_states/ # Normal, JumpUpStiQ, JettPaQ
├── core/             # Engine, resources, input, time
├── world/            # Physics, collision, tiles
├── modes/            # 6 WoNQmodes
├── objects/          # Collectibles, powerups, hazards
├── scenes/           # Menu, game scene with backgrounds
├── ui/               # HUD, menus
├── shared/           # Constants, types, sprite data
├── levels/           # Level JSON files
└── assets/           # Sprites + qq-background1-4.png
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

## License

Qommandah Qeen is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
See the [LICENSE](LICENSE) file for full text.
