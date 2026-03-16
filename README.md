# ZZBoard Public

> A cozy, fully customizable terminal dashboard. Open source, free forever, and built to make your desktop feel alive.

```
  ________ ______  ____  ____  ____  ____  ____
 |___  /  /  /  / / __ )/ __ \/ __ \/ __ \/ __ \
    / /  /  /  / / __ )/ / / / / / / /_/ / / / /
   / /__/  /__/ / /_/ / /_/ / /_/ / _, _/ /_/ /
  /____/__/__/ /_____/\____/\____/_/ |_/_____/
         PUBLIC EDITION  -- made by @wtfplutolol with <3
```

---

## Screenshots

![System Tab](https://raw.githubusercontent.com/wtfplutolol/zzboard-public/main/system.png)

![Boot Screen](https://raw.githubusercontent.com/wtfplutolol/zzboard-public/main/splash.png)

---

## Why ZZBoard?

- **Open source** — every line of code is right here. Read it, fork it, modify it, share it.
- **Fully customizable** — 8 themes, adjustable settings, your city, your tasks, your Spotify keys. It's yours.
- **Auto-updating** — ZZBoard checks GitHub Releases every time you launch and updates itself silently. You never have to manually download a new version.
- **No account required** — just download and run. Spotify is optional and uses your own API keys stored locally.
- **No telemetry** — nothing is collected or sent anywhere. Your config stays on your machine.

---

## Features

- **6 tabbed screens** — press `1` through `6` to switch instantly
- **Live system stats** — CPU, RAM, disk, network with sparkline graphs
- **Weather with ASCII doodles** — current conditions plus a 6 hour forecast
- **Moon phase** — ASCII art, illumination % and days to full moon
- **Sunrise and sunset** — pulled automatically from your city
- **Spotify now playing** — bring your own API keys, stored locally
- **Spotify queue** — see what's coming up next
- **Speed test** — auto runs on launch, press T anytime to run manually
- **HUD** — FPS, ping and WiFi signal always visible in the tab bar
- **Snake and Tetris** — fully playable games with high score tracking
- **8 color themes** — pink, green, blue, amber, red, nord, dracula, synthwave
- **Low light mode** — dims all colors for late night use
- **Time-aware greeting** — good morning, afternoon, evening or night
- **Days until weekend** — always visible on the system tab
- **Screensaver** — animated cat appears after 5 minutes of inactivity
- **WASD navigation in settings** — no mouse needed
- **Auto-updater** — checks GitHub Releases on every launch and updates silently

---

## Tabs

| Key | Tab | Contents |
|-----|-----|----------|
| `1` | System | Clock, CPU, Memory, Spotify |
| `2` | Sky | Weather, Moon phase, Hourly forecast |
| `3` | Storage | Disk, Tasks, Processes |
| `4` | Speed | Internet speed test |
| `5` | Games | Snake + Tetris |
| `6` | Settings | Theme, temp unit, time format, city, Spotify keys |

---

## Controls

| Key | Action |
|-----|--------|
| `1` to `6` | Switch tabs |
| `S` | Start Snake |
| `T` | Start Tetris (on games tab) or run speed test (on speed tab) |
| `WASD` / Arrows | Move in Snake, control Tetris, navigate Settings |
| `W` / Up | Rotate in Tetris |
| `S` / Down | Hard drop in Tetris |
| `Q` | Quit current game |
| `Enter` | Confirm setting |
| `Ctrl+C` | Exit ZZBoard |

---

## Download

Go to [Releases](../../releases/latest) and download `zzboard_public.exe`. Double-click to run. No Python required.

> **Windows SmartScreen** may show a warning on first launch. Click **More info** then **Run anyway**. This is normal for unsigned open source apps and only appears once.

---

## Auto-Updates

ZZBoard checks this GitHub repo on every launch. If a new release is found it downloads the new exe, shows the changelog, and restarts automatically. You never need to manually download an update.

Your config file and high scores are never touched by updates.

---

## Themes

| Theme | Style |
|-------|-------|
| `pink` | Hot pink — default |
| `green` | Neon mint |
| `blue` | Sky blue |
| `amber` | Warm gold |
| `red` | Bright red |
| `nord` | Icy blues and cool grays |
| `dracula` | Dark purple with vibrant accents |
| `synthwave` | Neon pink, purple and cyan |

Switch themes live in the Settings tab. Changes apply instantly.

---

## Spotify Setup

1. Go to [developer.spotify.com/dashboard](https://developer.spotify.com/dashboard)
2. Create a free app and set the Redirect URI to `http://127.0.0.1:8888/callback`
3. Copy your **Client ID** and **Client Secret**
4. In ZZBoard press `6` → Advanced → enter your keys
5. Restart — Spotify now playing appears at the bottom of Tab 1

Your keys are stored locally in `zzboard_config.json` and never sent anywhere.

---

## Configuration

ZZBoard saves your settings to `zzboard_config.json` next to the exe. This file is never touched by updates.

```json
{
  "city": "London",
  "city_state": "England",
  "city_country": "GB",
  "theme": "pink",
  "temp_unit": "F",
  "time_format": "24",
  "speed_interval": 30,
  "low_light": false,
  "tasks": ["water the plants", "touch some grass", "take a nap"],
  "spotify_client_id": "",
  "spotify_client_secret": ""
}
```

High scores are saved to `zzboard_scores.json`.

---

## Run from source

```bash
pip install psutil rich requests speedtest-cli watchdog spotipy
python zzboard_public.py
```

## Build the exe yourself

```bash
pip install pyinstaller
pyinstaller --onefile --icon=zzboard_public.ico zzboard_public.py
```

---

## Contributing

ZZBoard is open source and contributions are welcome. Feel free to open issues, suggest features or submit pull requests.

---

## License

MIT — free to use, modify and distribute.

---

## Credits

Built by [@wtfplutolol](https://github.com/wtfplutolol) with <3
