# ZZBoard Public

> A cozy, cat-powered terminal dashboard. Open source, fully customizable, and built to make your desktop feel alive.

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
- **Fully customizable** — 8 themes, your city, your cat's name, your tasks, your Spotify keys. Make it yours.
- **Cat-powered** — a sleeping cat lives on your dashboard and reacts to music, weather, CPU load and the time of day.
- **Auto-updating** — checks GitHub Releases on every launch and updates itself silently. You never need to download a new version manually.
- **No account required** — download and run. Spotify is optional and uses your own API keys stored locally.
- **No telemetry** — nothing is collected or sent anywhere. Your config stays on your machine.

---

## Features

**System**
- Live CPU, RAM, disk and network stats with sparkline graphs and per-core view
- Clock with 12hr/24hr format, day of week and days until weekend
- Time-aware greeting — good morning, afternoon, evening or night

**Weather**
- Current conditions with ASCII doodles for each weather type
- 6 hour hourly forecast
- Sunrise and sunset times
- Sky doodle changes based on time of day — dawn, morning, afternoon, golden hour, dusk, night
- Countdown to next sky period shown live

**Cat**
- Sleeping cat that reacts to Spotify, CPU load, weather and time of day
- Different expressions depending on what is happening
- Random idle animations — twitches and rolls over every 30-60 seconds
- Indicators float around the cat — music note, lightning bolt, moon
- Name your cat in settings

**Music**
- Spotify now playing with progress bar and queue
- Song name and artist shown near the cat
- Bring your own API keys, stored locally
- Browser opens automatically for Spotify login — no URL pasting needed

**Speed and WiFi**
- Internet speed test — auto runs on launch, press T to run manually
- WiFi panel shows public IP, local IP and ISP name
- IP hidden by default — press H to reveal
- Press C to copy results to clipboard

**Games**
- Snake with high score tracking
- Tetris with level progression and high score
- Pause with P, quit with Q

**HUD**
- Always visible in the tab bar — FPS, ping and WiFi signal strength
- Color coded — goes red when values are poor

**Settings**
- 8 themes switchable live with no restart
- Low light mode dims all colors for night use
- Change city instantly without restarting
- Live typing input — letters appear as you type with a flashing cursor
- WASD or arrow key navigation

---

## Tabs

| Key | Tab | Contents |
|-----|-----|----------|
| `1` | System | Clock, CPU, Memory, Cat, Spotify |
| `2` | Sky | Weather, Moon, Sky doodle, Hourly forecast |
| `3` | Storage | Disk, Tasks, Processes |
| `4` | Speed | Speed test, WiFi and IP info |
| `5` | Games | Snake + Tetris |
| `6` | Settings | Theme, temp, time, cat name, city, Spotify keys |

---

## Controls

| Key | Action |
|-----|--------|
| `1` to `6` | Switch tabs |
| `S` | Start Snake |
| `T` | Start Tetris (games tab) or run speed test (speed tab) |
| `WASD` / Arrows | Move in Snake, control Tetris, navigate Settings |
| `H` | Toggle IP / WiFi visibility |
| `C` | Copy current tab stats to clipboard |
| `P` | Pause game |
| `Q` | Quit current game |
| `Enter` | Confirm / save setting |
| `Ctrl+C` | Exit ZZBoard |

---

## Download

Go to [Releases](../../releases/latest) and download `zzboard_public.exe`. Double-click to run. No Python required.

> **Windows SmartScreen** may show a warning on first launch. Click **More info** then **Run anyway**. This is normal for unsigned open source apps and only appears once.

---

## Auto-Updates

ZZBoard checks GitHub Releases on every launch. If a newer version is found it downloads the exe, shows the changelog, and restarts automatically. Your config and high scores are never touched.

---

## Themes

| Name | Style |
|------|-------|
| `pink` | Hot pink — default |
| `green` | Neon mint |
| `blue` | Sky blue |
| `amber` | Warm gold |
| `red` | Bright red |
| `nord` | Icy blues and cool grays |
| `dracula` | Dark purple with vibrant accents |
| `synthwave` | Neon pink, purple and cyan |

Switch live in Settings. No restart needed.

---

## Spotify Setup

1. Go to [developer.spotify.com/dashboard](https://developer.spotify.com/dashboard)
2. Create a free app and set the Redirect URI to `http://127.0.0.1:8888/callback`
3. Copy your **Client ID** and **Client Secret**
4. In ZZBoard press `6` → Advanced → enter your keys
5. Your browser opens automatically to authorize — no URL pasting needed
6. Spotify now playing appears on Tab 1

Keys are stored locally in `zzboard_config.json` and never sent anywhere.

---

## Configuration

Settings are saved to `zzboard_config.json` next to the exe. Never touched by updates.

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
  "cat_name": "cat",
  "tasks": ["water the plants", "touch some grass", "take a nap"],
  "spotify_client_id": "",
  "spotify_client_secret": ""
}
```

High scores saved to `zzboard_scores.json`.

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

Open source and contributions are welcome. Open an issue, suggest a feature or submit a pull request.

---

## License

MIT — free to use, modify and distribute.

---

*made by [@wtfplutolol](https://github.com/wtfplutolol) with <3*
