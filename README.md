# ZZBoard Public

> A beautiful, feature-rich terminal dashboard for your desktop. Open source and free to use.

```
  ________ ______  ____  ____  ____  ____  ____
 |___  /  /  /  / / __ )/ __ \/ __ \/ __ \/ __ \
    / /  /  /  / / __ )/ / / / / / / /_/ / / / /
   / /__/  /__/ / /_/ / /_/ / /_/ / _, _/ /_/ /
  /____/__/__/ /_____/\____/\____/_/ |_/_____/
             P U B L I C  E D I T I O N
```

---

## Features

- **5 tabbed screens** — switch with number keys `1` through `5`
- **Live system stats** — CPU, RAM, disk, network with sparkline graphs
- **Weather** — asks for your city on first launch, updates every 5 minutes
- **Moon phase** — real-time moon phase with ASCII art and illumination %
- **Speed test** — download, upload and ping, runs automatically
- **Mini games** — Snake and Flappy Bird, playable right in the terminal
- **Auto-updater** — checks for updates every time you launch
- **Animated boot screen** — sleeping cat splash with progress bar

---

## Tabs

| Key | Tab | Contents |
|-----|-----|----------|
| `1` | System | Clock, CPU, Memory |
| `2` | Sky | Weather + Moon Phase |
| `3` | Storage | Disk, Tasks, Processes |
| `4` | Speed | Internet speed test |
| `5` | Games | Snake + Flappy Bird |

---

## Controls

| Key | Action |
|-----|--------|
| `1` - `5` | Switch tabs |
| `S` | Start / restart Snake |
| `F` | Start / restart Flappy Bird |
| `WASD` / Arrow keys | Move in Snake |
| `Space` | Flap in Flappy Bird |
| `Q` | Quit current game |
| `Ctrl+C` | Exit ZZBoard |

---

## Installation

### Easy way (Windows exe)

1. Go to [Releases](../../releases) and download `zzboard_public.exe`
2. Double-click to run
3. On first launch it will ask for your city

### Developer way (Python)

**Requirements:** Python 3.10+

```bash
# Install dependencies
pip install psutil rich requests speedtest-cli watchdog

# Run
python zzboard_public.py
```

---

## Configuration

On first launch ZZBoard creates a `zzboard_config.json` file next to the exe/script:

```json
{
  "city": "London",
  "tasks": [
    "Review pull requests",
    "Update dependencies",
    "Write docs"
  ]
}
```

Edit this file to change your city or tasks. Changes take effect on next launch.

---

## Auto-updates

ZZBoard checks this GitHub repo for updates every time you launch. If a new version is available it downloads and applies it automatically — you will see it on the boot screen.

---

## Building the exe yourself

```bash
pip install pyinstaller
pyinstaller --onefile zzboard_public.py
```

The exe will be in the `dist` folder.

---

## Requirements

- Windows 10/11 (Linux/Mac may work with minor tweaks)
- Python 3.10+ (not needed if using the exe)
- Internet connection for weather and auto-updates

---

## Credits

Built by [@wtfplutolol](https://github.com/wtfplutolol)

---

## License

MIT — free to use, modify and distribute.
