ZZBoard Public

A beautiful, cozy terminal dashboard. Free, open source, and made for everyone.

  ________ ______  ____  ____  ____  ____  ____
 |___  /  /  /  / / __ )/ __ \/ __ \/ __ \/ __ \
    / /  /  /  / / __ )/ / / / / / / /_/ / / / /
   / /__/  /__/ / /_/ / /_/ / /_/ / _, _/ /_/ /
  /____/__/__/ /_____/\____/\____/_/ |_/_____/
         PUBLIC EDITION  -- made by @wtfplutolol with <3

What it looks like
System tab — CPU, Memory and Spotify now playing
Show Image
Boot screen — animated sleeping cat with update checker
Show Image

Features

6 tabbed screens — press 1 through 6 to switch instantly
Live system stats — CPU, RAM, disk, network with sparkline graphs and per-core bars
Weather with doodles — ASCII art for each weather condition, auto-detects your city
Moon phase — real-time ASCII moon art, illumination % and days to full moon
Sunrise & sunset — fetched automatically based on your city
Spotify now playing — enter your own API keys in Settings, stored locally
Speed test — press T on the Speed tab whenever you feel curious
Snake — classic snake game with high score tracking
5 color themes — green, blue, pink, amber, red, switchable live in settings
WASD navigation in settings — W/S to navigate, A/D to change values
Advanced settings — Spotify keys, city reset, time format
Auto-updater — checks GitHub Releases on every launch and updates silently
Cozy vibes — friendly messages, lowercase text, relaxed animations


Tabs
KeyTabContents1SystemClock, CPU, Memory, Spotify (if configured)2SkyWeather with doodles + Moon Phase + Sunrise/Sunset3StorageDisk usage, Tasks, Top Processes4SpeedInternet speed test — press T to run5GamesSnake with high score6SettingsTheme, temp unit, time format, city reset, Spotify keys

Controls
KeyAction1 - 6Switch tabsSStart / restart SnakeWASD / Arrow keysMove in Snake or navigate SettingsA / DChange setting value left / rightTRun speed test (on Speed tab)QQuit current gameEnterConfirm setting / actionCtrl+CExit ZZBoard

Installation
Easy way — Windows exe (no Python needed)

Go to Releases and download zzboard_public.exe
Double-click to run
On first launch it asks for your city — just type it and hit Enter
That's it!


Windows SmartScreen warning — Windows may show a "Windows protected your PC" popup on first launch because the app isn't code-signed. This is normal for open source apps. Click "More info" then "Run anyway" to proceed. You will only see this once.

Developer way — Python
Requirements: Python 3.10+
bashpip install psutil rich requests speedtest-cli watchdog spotipy
python zzboard_public.py

Setting up Spotify

Go to developer.spotify.com/dashboard
Create a free app — set Redirect URI to http://127.0.0.1:8888/callback
Copy your Client ID and Client Secret
In ZZBoard press 6 for Settings → scroll down to Advanced
Enter your Client ID and Secret — saved locally, never uploaded
Restart ZZBoard — Spotify now playing appears at the bottom of Tab 1


Configuration
On first launch ZZBoard creates zzboard_config.json next to the exe. This file saves all your settings and is never touched by updates:
json{
  "city": "London",
  "city_state": "England",
  "city_country": "GB",
  "theme": "pink",
  "temp_unit": "F",
  "time_format": "24",
  "tasks": ["water the plants", "touch some grass", "take a nap"],
  "spotify_client_id": "",
  "spotify_client_secret": ""
}
High scores are saved to zzboard_scores.json.

Themes
NameColorpinkHot pink (default)greenNeon mintblueSky blueamberWarm goldredBright red
Switch themes live in Settings — no restart needed.

Auto-updates
ZZBoard checks GitHub Releases on every launch. If a newer version is found it downloads the new exe, shows the changelog, and applies the update automatically. Your config and scores are never affected.

Uploading screenshots to fix images
If the screenshots above don't load, upload them to the repo:

Save the screenshots as system.png and splash.png
Go to your repo on GitHub → Add file → Upload files
Upload both images and commit


Building the exe yourself
bashpip install pyinstaller
pyinstaller --onefile --icon=zzboard_public.ico zzboard_public.py
The exe will be in the dist folder.

Requirements

Windows 10/11
Python 3.10+ (not needed if using the exe)
Internet connection for weather, Spotify and auto-updates


Credits
Built by @wtfplutolol with <3

License
MIT — free to use, modify and distribute.
