# 🎮 QommandahQeen MAQZIMUM

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.5.4--alpha-brightgreen.svg)](VERSION)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![Pygame-CE](https://img.shields.io/badge/pygame--ce-2.5+-orange.svg)](https://pyga.me)

![Splash](assets/qq-main-menu.png)

> **Commander Keen-Inspired Platformer with QonQrete Aesthetics**  
> Built with 💜 using QonQrete AgentiQ OrQhestration

---

## 🚀 Quick Start

```bash
# Install dependencies
pip install pygame-ce

# Run the game
python main.py

# Toggle fullscreen with F11
```

---

## 🎮 Controls

### Movement
| Key | Action |
|-----|--------|
| **Arrow Keys** / **WASD** | Move left/right |
| **Space** / **Z** / **W** / **Up** | Jump |
| **X** / **Ctrl** | Shoot |

### Interaction
| Key | Action |
|-----|--------|
| **SPACE** | Interact with doors (unlock with key, enter when open) |
| **ENTER** / **E** | Mount/Unmount JumpUpstiq pogo stick |
| **Escape** / **P** | Pause menu |
| **F11** | Toggle fullscreen |

---

## 🏋️ JumpUpstiq Pogo Stick

The JumpUpstiq is a **mountable pogo stick** that doubles your jump height!

| Action | How |
|--------|-----|
| **Stand on it** | Walk onto the pogo - you pass through it |
| **Mount** | Press **ENTER** while standing on it |
| **Bounce** | Automatic! You're now jumping 2x higher! |
| **Unmount** | Press **ENTER** again - drops pogo where you stand |
| **Re-mount** | Walk to dropped pogo, press **ENTER** |

> 💡 **Pro Tip:** The JumpUpstiq uses special pogo sprites (qq-qeen-jumpupstiq.png) when mounted!

---

## 🚪 Doors & Keys

1. **Find the Key** - Walk into the floating key to collect it
2. **Go to the Door** - Walk up to the locked door
3. **Press SPACE** - Unlocks the door and plays opening animation
4. **Enter** - Press SPACE again when door is fully open to enter next room

---

## ✨ Features

### Player States
| State | Description | Sprites |
|-------|-------------|---------|
| **Normal** | Standard run, jump, shoot with smoke Q overlay | qq-qommandah-qeen.png |
| **JumpUpstiq** | Mountable pogo stick with 2x jump height | qq-qeen-jumpupstiq.png |
| **JettPaq** | Boombox jetpack for flight | qq-qeen-jetpaq.png |

### Enemies (6 Types)
| Enemy | Behavior | Damage | HP |
|-------|----------|--------|-----|
| **WalQer Bot** | Patrol + chase player | 10 | 50 |
| **Jumper DrQne** | Periodic jumping | 15 | 60 |
| **Qortana Halo** | Follow + ZAP attack | 15 | 60 |
| **Qlippy** | Annoying dialogue blocks | 10 | 30 |
| **BriQ Beaver** | Throws arcing briQs | 20 | 80 |
| **Hover Squid** | Floating figure-8 swoop | 15 | 40 |

### WoNQmodes (6 Modes)
| Mode | Effect |
|------|--------|
| **Low-G** | 50% gravity |
| **Glitch** | Screen shake, jitter |
| **Mirror** | Horizontal flip |
| **Bullet Time** | 0.3x time scale |
| **Speedy Boots** | 2x movement speed |
| **Junglist** | 174 BPM bass pulses! |

### Collectibles & Items
| Item | Effect |
|------|--------|
| **Chips** | Score bonus |
| **Floppies** | Extra points |
| **Medallions** | High value |
| **Keys** | Unlock doors |
| **JumpUpstiq** | Mountable pogo (2x jump!) |
| **JettPaq** | Timed jetpack powerup |

---

## 📁 Project Structure

```
qommandah-qeen/
├── main.py               # Entry point
├── VERSION               # Version file (0.5.4)
├── LICENSE               # AGPL-3.0
├── README.md             # This file
│
├── actors/               # Player, enemies
│   ├── player.py         # Main player class
│   ├── player_states/    # Normal, JumpUpstiq, JettPaq
│   └── enemies/          # All 6 enemy types
│
├── core/                 # Engine systems
├── world/                # Physics, collision, tiles
├── objects/              # Collectibles, doors, keys, powerups
├── modes/                # WoNQmodes
├── scenes/               # Menu, game scene
├── ui/                   # HUD, menus
├── shared/               # Constants, types
├── levels/               # Level JSON files
└── assets/               # Sprites & backgrounds
```

---

## 🔧 Technical Details

### Physics System
- Float-based sub-pixel movement
- Gravity: 2400 units/s²
- Normal jump force: -950
- JumpUpstiq jump force: -1900 (2x!)
- 60 FPS fixed timestep

### Key Bindings (core/input.py)
- `interact` → SPACE (doors)
- `powerup_toggle` → ENTER, E (mount/unmount)
- `jump` → SPACE, Z, W, UP
- `shoot` → X, CTRL

---

## 📝 Changelog

### v0.5.4-alpha (Current)
- **NEW CONTROL SCHEME**: SPACE=Interact, ENTER=Mount/Unmount
- JumpUpstiq requires ENTER to mount (walk through without auto-pickup)
- JumpUpstiq uses qq-qeen-jumpupstiq.png pogo sprites when mounted
- Doors use key system: pick up key, press SPACE to unlock
- Level 1: Key next to door, wall barrier on right side
- Door opens with animation and transitions to next room

### v0.5.3-alpha
- Fixed JettPaq crash (missing `import random`)
- Removed glitchy JettPaq from level 1

### v0.5.2-alpha
- JumpUpstiq mountable system introduced
- Double jump height when mounted

### v0.5.1-alpha
- Fixed JumpUpstiq state crashes

### v0.4.x
- Jump height tuning and bug fixes
- Enemy patrol AI improvements

### v0.3.x
- Walk animation, health system
- Key/door mechanics, powerup UI

### v0.2.x
- All 6 enemy types
- Background parallax scrolling

---

## 🎨 Credits

- **Game Design & Code**: Built with QonQrete AgentiQ OrQhestration
- **Inspiration**: Commander Keen (id Software)
- **Engine**: pygame-ce

---

## 📜 License

QommandahQeen MAQZIMUM is licensed under the **GNU Affero General Public License v3.0** (AGPL-3.0).

See the [LICENSE](LICENSE) file for full text.

---

**KABOOMAGE!!! 💥**

*yafeelme bruv* 🔥🎮
