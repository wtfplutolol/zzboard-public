# ZZBoard Public

A cozy, feature-rich terminal dashboard. Free, open source, made by [@wtfplutolol](https://github.com/wtfplutolol).

---

![Boot Screen](https://raw.githubusercontent.com/wtfplutolol/zzboard-public/main/splash.png)

![System Tab](https://raw.githubusercontent.com/wtfplutolol/zzboard-public/main/system.png)

---

## Features

- Live CPU, RAM, disk and network stats with graphs
- Weather with ASCII doodles for each condition
- Moon phase art, illumination and days to full moon
- Sunrise and sunset times
- Spotify now playing (bring your own API keys)
- Speed test — press T whenever you want to check
- Snake with high score tracking
- 5 color themes switchable live
- WASD navigation in settings
- Auto-updater via GitHub Releases
- Cozy messages and relaxed animations throughout

---

## Tabs

| Key | Tab |
|-----|-----|
| `1` | System — clock, CPU, memory, Spotify |
| `2` | Sky — weather, moon, sunrise/sunset |
| `3` | Storage — disk, tasks, processes |
| `4` | Speed — press T to test |
| `5` | Games — Snake |
| `6` | Settings |

---

## Controls

| Key | Action |
|-----|--------|
| `1` to `6` | Switch tabs |
| `S` | Start Snake |
| `WASD` / arrows | Move in Snake or navigate Settings |
| `A` / `D` | Change setting value |
| `T` | Run speed test |
| `Q` | Quit game |
| `Enter` | Confirm setting |
| `Ctrl+C` | Exit |

---

## Download

Go to [Releases](../../releases/latest) and download `zzboard_public.exe`. Double-click to run. No Python needed.

> **Windows SmartScreen** may show a warning on first launch. Click **More info** then **Run anyway**. This is normal for unsigned open source apps and only appears once.

---

## Spotify Setup

1. Go to [developer.spotify.com/dashboard](https://developer.spotify.com/dashboard)
2. Create an app and set the Redirect URI to `http://127.0.0.1:8888/callback`
3. Copy your Client ID and Client Secret
4. In ZZBoard press `6` → Advanced → enter your keys
5. Restart — Spotify appears at the bottom of Tab 1

Keys are stored locally in `zzboard_config.json` and never uploaded anywhere.

---

## Configuration

ZZBoard saves your settings to `zzboard_config.json` next to the exe. This file is never touched by updates.

```json
{
  "city": "London",
  "theme": "pink",
  "temp_unit": "F",
  "time_format": "24",
  "tasks": ["water the plants", "touch some grass", "take a nap"],
  "spotify_client_id": "",
  "spotify_client_secret": ""
}
```

High scores are saved separately in `zzboard_scores.json`.

---

## Themes

`pink` `green` `blue` `amber` `red` — switch live in Settings, no restart needed.

---

## Auto-updates

On every launch ZZBoard checks GitHub Releases. If a new version is found it downloads the exe, shows the changelog, and restarts. Your config and scores are never affected.

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


## License

MIT — free to use, modify and share.
