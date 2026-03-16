# -*- coding: utf-8 -*-
#!/usr/bin/env python3
# ZZBoard Public v1.4
# https://github.com/wtfplutolol/zzboard-public
# Made by @wtfplutolol with <3
# Requirements: pip install psutil rich requests speedtest-cli watchdog spotipy
# Keys: 1-6 tabs | S=snake | F=flappy | WASD/arrows | Space=flap | Q=quit game

import argparse
import hashlib
import json
import math
import os
import random
import subprocess
import sys
import threading
import time
import urllib3
from collections import deque
from datetime import datetime, timezone

urllib3.disable_warnings()

try:
    import psutil
except ImportError:
    print("Run: pip install psutil rich requests speedtest-cli watchdog spotipy")
    sys.exit(1)

try:
    from rich import box
    from rich.align import Align
    from rich.console import Console
    from rich.layout import Layout
    from rich.live import Live
    from rich.panel import Panel
    from rich.text import Text
except ImportError:
    print("Run: pip install psutil rich requests speedtest-cli watchdog spotipy")
    sys.exit(1)

try:
    import requests
except ImportError:
    requests = None

try:
    import speedtest as speedtest_lib
except ImportError:
    speedtest_lib = None

try:
    import spotipy
    from spotipy.oauth2 import SpotifyOAuth
except ImportError:
    spotipy = None

try:
    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer
except ImportError:
    Observer = None
    FileSystemEventHandler = object

# ── Runtime detection ──────────────────────────────────────────────────────────
IS_EXE    = getattr(sys, "frozen", False)
THIS_FILE = sys.executable if IS_EXE else os.path.abspath(__file__)
THIS_DIR  = os.path.dirname(THIS_FILE)

# ── Config ─────────────────────────────────────────────────────────────────────
CONFIG_FILE       = os.path.join(THIS_DIR, "zzboard_config.json")
SPOTIFY_CACHE     = os.path.join(THIS_DIR, ".cache")
GITHUB_USER       = "wtfplutolol"
GITHUB_REPO       = "zzboard-public"
GITHUB_RAW_URL    = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/zzboard_public.py"
GITHUB_LATEST_URL = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/releases/latest"
CURRENT_VERSION   = "v1.4"

# ── Changelog ─────────────────────────────────────────────────────────────────
CHANGELOG = [
    ("v1.4", [
        "Multi-city selection with state/country disambiguation",
        "Smoother Flappy Bird physics",
        "12hr/24hr time format toggle in settings",
        "Sunrise/sunset times on Sky tab",
        "Spotify now playing at bottom of System tab",
        "Advanced settings: enter Spotify Client ID and Secret",
        "Spotify stored locally, never uploaded",
        "High scores for Snake and Flappy Bird",
    ]),
    ("v1.2", [
        "Pink default theme",
        "City reset countdown",
        "City not found error message",
        "Changelog screen after updates",
        "Exe auto-updater via GitHub Releases",
    ]),
    ("v1.1", [
        "Settings tab with themes, temp unit, speed interval",
        "Reset city and force update from settings",
    ]),
    ("v1.0", ["Initial public release"]),
]

# ── Themes ─────────────────────────────────────────────────────────────────────
THEMES = {
    "green": {"CLR_CLOCK":"#00FFB2","CLR_CPU":"#FF6B6B","CLR_MEM":"#FFD93D","CLR_WEATHER":"#6BCBFF","CLR_MOON":"#E0E0FF","CLR_DISK":"#A8FF78","CLR_TASKS":"#BD93F9","CLR_PROCS":"#FF9F43","CLR_SPEED":"#00CEC9","CLR_SNAKE":"#00FF00","CLR_FLAPPY":"#FFD700","CLR_SPOTIFY":"#1DB954","CLR_DIM":"#555566"},
    "blue":  {"CLR_CLOCK":"#00BFFF","CLR_CPU":"#87CEEB","CLR_MEM":"#4169E1","CLR_WEATHER":"#00CED1","CLR_MOON":"#E0E8FF","CLR_DISK":"#1E90FF","CLR_TASKS":"#6495ED","CLR_PROCS":"#00BFFF","CLR_SPEED":"#40E0D0","CLR_SNAKE":"#00FF7F","CLR_FLAPPY":"#87CEFA","CLR_SPOTIFY":"#1DB954","CLR_DIM":"#334455"},
    "pink":  {"CLR_CLOCK":"#FF79C6","CLR_CPU":"#FF6B9D","CLR_MEM":"#FFB3DE","CLR_WEATHER":"#FF85C8","CLR_MOON":"#FFE0F0","CLR_DISK":"#FF69B4","CLR_TASKS":"#DA70D6","CLR_PROCS":"#FF1493","CLR_SPEED":"#FF82AB","CLR_SNAKE":"#FF69B4","CLR_FLAPPY":"#FFB6C1","CLR_SPOTIFY":"#1DB954","CLR_DIM":"#553344"},
    "amber": {"CLR_CLOCK":"#FFB000","CLR_CPU":"#FF8C00","CLR_MEM":"#FFD700","CLR_WEATHER":"#FFA500","CLR_MOON":"#FFEEBB","CLR_DISK":"#FFCC00","CLR_TASKS":"#FF9F43","CLR_PROCS":"#FF6347","CLR_SPEED":"#FFC125","CLR_SNAKE":"#ADFF2F","CLR_FLAPPY":"#FFD700","CLR_SPOTIFY":"#1DB954","CLR_DIM":"#554433"},
    "red":   {"CLR_CLOCK":"#FF4444","CLR_CPU":"#FF6B6B","CLR_MEM":"#FF8080","CLR_WEATHER":"#FF6666","CLR_MOON":"#FFE0E0","CLR_DISK":"#FF5555","CLR_TASKS":"#CC3333","CLR_PROCS":"#FF0000","CLR_SPEED":"#FF3333","CLR_SNAKE":"#FF6666","CLR_FLAPPY":"#FFB3B3","CLR_SPOTIFY":"#1DB954","CLR_DIM":"#553333"},
}

CLR = {}

def apply_theme(name):
    global CLR
    CLR.update(THEMES.get(name, THEMES["pink"]))

# ── State ──────────────────────────────────────────────────────────────────────
CPU_HIST        = deque([0.0] * 50, maxlen=50)
MEM_HIST        = deque([0.0] * 50, maxlen=50)
START_TIME      = datetime.now()
console         = Console()
reload_flag     = threading.Event()
current_tab     = {"tab": 1}
settings_cursor = {"pos": 0, "section": "main"}
settings_msg    = {"text": "", "color": "#FF79C6", "time": 0}

weather_cache  = {"data": None, "error": None, "last": 0}
speed_cache    = {"download": None, "upload": None, "ping": None, "testing": False, "last": 0, "error": None}
update_status  = {"checked": False, "updated": False, "error": None, "log": [], "new_version": None}
weather_meta   = {"url": None, "city": "Unknown", "country": "", "not_found": False, "lat": 0, "lon": 0}
spotify_cache  = {"data": None, "error": None, "sp": None, "authed": False}
sun_cache      = {"sunrise": None, "sunset": None, "last": 0}
high_scores    = {"snake": 0, "flappy": 0}
_cfg_ref       = {}

# ── Config helpers ─────────────────────────────────────────────────────────────

DEFAULT_CONFIG = {
    "city": "", "theme": "pink", "temp_unit": "F", "time_format": "24",
    "speed_interval": 30,
    "tasks": ["Review pull requests", "Update dependencies", "Write docs"],
    "spotify_client_id": "", "spotify_client_secret": "",
}

def load_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            cfg = json.load(f)
        for k, v in DEFAULT_CONFIG.items():
            if k not in cfg:
                cfg[k] = v
        return cfg
    except Exception:
        return dict(DEFAULT_CONFIG)

def save_config(cfg):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(cfg, f, indent=2)
    except Exception:
        pass

def load_high_scores():
    try:
        path = os.path.join(THIS_DIR, "zzboard_scores.json")
        with open(path, "r") as f:
            s = json.load(f)
        high_scores["snake"]  = s.get("snake", 0)
        high_scores["flappy"] = s.get("flappy", 0)
    except Exception:
        pass

def save_high_scores():
    try:
        path = os.path.join(THIS_DIR, "zzboard_scores.json")
        with open(path, "w") as f:
            json.dump(high_scores, f)
    except Exception:
        pass

# ── Safe restart ───────────────────────────────────────────────────────────────

def do_restart():
    args = [THIS_FILE, "--no-splash"] if IS_EXE else [sys.executable, THIS_FILE, "--no-splash"]
    try:
        subprocess.Popen(args, creationflags=subprocess.CREATE_NEW_CONSOLE if IS_EXE else 0)
    except Exception:
        subprocess.Popen(args)
    time.sleep(1.0)
    sys.exit(0)

def do_restart_fresh():
    args = [THIS_FILE] if IS_EXE else [sys.executable, THIS_FILE]
    try:
        subprocess.Popen(args, creationflags=subprocess.CREATE_NEW_CONSOLE if IS_EXE else 0)
    except Exception:
        subprocess.Popen(args)
    time.sleep(1.0)
    sys.exit(0)

# ── City reset countdown ───────────────────────────────────────────────────────

def city_reset_countdown():
    for i in range(5, 0, -1):
        t = Text(justify="center")
        t.append("\n\n\n")
        t.append("  City has been reset!\n\n",        style=f"bold {CLR['CLR_CLOCK']}")
        t.append(f"  Restarting in {i}...\n\n",       style=f"bold {CLR['CLR_WEATHER']}")
        t.append("  You will be asked for your new city\n", style=f"dim {CLR['CLR_DIM']}")
        with Live(Align.center(t, vertical="middle"), console=console, screen=True, refresh_per_second=2):
            time.sleep(1.0)
    do_restart_fresh()

# ── Changelog ─────────────────────────────────────────────────────────────────

ZZBOARD_LOGO = [
    "  ________ ______  ____  ____  ____  ____  ____  ",
    " |___  /  /  /  / / __ )/ __ \\/ __ \\/ __ \\/ __ \\ ",
    "    / /  /  /  / / __ )/ / / / / / / /_/ / / / / ",
    "   / /__/  /__/ / /_/ / /_/ / /_/ / _, _/ /_/ /  ",
    "  /____/__/__/ /_____/\\____/\\____/_/ |_/_____/    ",
]

def show_changelog():
    console.clear()
    try:
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getwch()
    except Exception:
        pass

    t = Text(justify="center")
    t.append("\n")
    colors = [CLR["CLR_CLOCK"],CLR["CLR_WEATHER"],CLR["CLR_MOON"],CLR["CLR_TASKS"],CLR["CLR_CPU"]]
    for i, line in enumerate(ZZBOARD_LOGO):
        t.append(line + "\n", style=f"bold {colors[i % len(colors)]}")
    t.append("\n")
    t.append("  WHATS NEW\n\n", style=f"bold {CLR['CLR_CLOCK']}")
    for version, changes in CHANGELOG:
        t.append(f"  {version}\n", style=f"bold {CLR['CLR_WEATHER']}")
        for change in changes:
            t.append(f"    + {change}\n", style=f"dim {CLR['CLR_MOON']}")
        t.append("\n")
    t.append("  ============================================\n", style=f"dim {CLR['CLR_DIM']}")
    t.append("  >>  Press ENTER to enter the dashboard  <<  \n", style=f"bold {CLR['CLR_CLOCK']} reverse")
    t.append("  ============================================\n", style=f"dim {CLR['CLR_DIM']}")

    console.print(Align.center(t, vertical="middle"))
    console.print()

    try:
        import msvcrt
        while True:
            ch = msvcrt.getwch()
            if ch == "\r":
                break
            time.sleep(0.05)
    except Exception:
        time.sleep(3.0)

# ── Multi-city selection ───────────────────────────────────────────────────────

def search_cities(city_name):
    """Search for cities and return list of options."""
    try:
        r = requests.get(
            f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=10",
            verify=False, timeout=5
        ).json()
        results = r.get("results", [])
        return results
    except Exception:
        return []

def get_weather_url_from_coords(lat, lon):
    return (f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
            f"&current=temperature_2m,weathercode,windspeed_10m,relative_humidity_2m"
            f"&daily=sunrise,sunset&temperature_unit=fahrenheit&windspeed_unit=mph&timezone=auto")

def first_launch_setup():
    console.clear()
    colors = [CLR["CLR_CLOCK"],CLR["CLR_WEATHER"],CLR["CLR_MOON"],CLR["CLR_TASKS"],CLR["CLR_CPU"]]
    logo   = [
        "  ________ ______  ____  ____  ____  ____  ____  ",
        " |___  /  /  /  / / __ )/ __ \\/ __ \\/ __ \\/ __ \\ ",
        "    / /  /  /  / / __ )/ / / / / / / /_/ / / / / ",
        "   / /__/  /__/ / /_/ / /_/ / /_/ / _, _/ /_/ /  ",
        "  /____/__/__/ /_____/\\____/\\____/_/ |_/_____/    ",
        "             P U B L I C  E D I T I O N           ",
    ]
    t = Text(justify="center")
    t.append("\n\n")
    for i, line in enumerate(logo):
        t.append(line + "\n", style=f"bold {colors[i % len(colors)]}")
    t.append("\n")
    t.append("  Made by @wtfplutolol with <3\n\n", style=f"dim {CLR['CLR_MOON']}")
    t.append("  Welcome! One-time setup\n\n", style=f"bold {CLR['CLR_CLOCK']}")
    console.print(Align.center(t))

    while True:
        city_input = console.input(f"  [{CLR['CLR_WEATHER']}]Your city for weather:[/{CLR['CLR_WEATHER']}] ").strip()
        if not city_input:
            city_input = "New York"

        console.print(f"  [{CLR['CLR_DIM']}]Searching...[/{CLR['CLR_DIM']}]")
        results = search_cities(city_input)

        if not results:
            console.print(f"  [bold #FF4444]No cities found for '{city_input}'. Please try again.[/bold #FF4444]")
            continue

        if len(results) == 1:
            chosen = results[0]
        else:
            console.print(f"\n  [{CLR['CLR_CLOCK']}]Multiple cities found — pick one:[/{CLR['CLR_CLOCK']}]\n")
            for i, r in enumerate(results):
                name    = r.get("name", "")
                state   = r.get("admin1", "")
                country = r.get("country", "")
                pop     = r.get("population", 0)
                pop_str = f"  pop {pop:,}" if pop else ""
                console.print(f"  [{CLR['CLR_WEATHER']}]{i+1}.[/{CLR['CLR_WEATHER']}] {name}, {state}, {country}{pop_str}")

            while True:
                pick = console.input(f"\n  [{CLR['CLR_CLOCK']}]Enter number (1-{len(results)}):[/{CLR['CLR_CLOCK']}] ").strip()
                if pick.isdigit() and 1 <= int(pick) <= len(results):
                    chosen = results[int(pick) - 1]
                    break
                console.print(f"  [bold #FF4444]Invalid choice.[/bold #FF4444]")

        name    = chosen.get("name", city_input)
        state   = chosen.get("admin1", "")
        country = chosen.get("country_code", "")
        lat     = chosen.get("latitude", 0)
        lon     = chosen.get("longitude", 0)

        console.print(f"  [bold {CLR['CLR_CLOCK']}]Selected: {name}, {state}, {country}[/bold {CLR['CLR_CLOCK']}]")
        break

    cfg = dict(DEFAULT_CONFIG)
    cfg.update({"city": name, "city_state": state, "city_country": country, "city_lat": lat, "city_lon": lon})
    save_config(cfg)
    console.print(f"\n  [bold {CLR['CLR_CLOCK']}]All set! Starting ZZBoard...[/bold {CLR['CLR_CLOCK']}]\n")
    time.sleep(1.5)
    return cfg

# ── Moon phase ─────────────────────────────────────────────────────────────────

MOON_ART = {
    "New Moon":        ["    _..._    ","  .' *** '.  "," / ******* \\ ","|  *******  |"," \\ ******* / ","  '._***_.'  ","    `---'    "],
    "Waxing Crescent": ["    _..._    ","  .'  ** '.  "," /    ***  \\ ","|     ****  |"," \\    ***  / ","  '.  **_.'  ","    `---'    "],
    "First Quarter":   ["    _..._    ","  .'    '.   "," /    ### \\ ","|     ####  |"," \\    ### / ","  '._  _.'   ","    `---'    "],
    "Waxing Gibbous":  ["    _..._    ","  .' ####'.  "," / ####### \\ ","| ########  |"," \\ ####### / ","  '.####_.'  ","    `---'    "],
    "Full Moon":       ["    _..._    ","  .#######.  "," /##########\\","|############|"," \\##########/","  '#######'  ","    `---'    "],
    "Waning Gibbous":  ["    _..._    ","  '.#####'.  "," /####### \\ ","|########   |"," \\####### / ","  '.#####.'  ","    `---'    "],
    "Last Quarter":    ["    _..._    ","  .'###  '.  "," /####    \\ ","|#####      |"," \\####    / ","  '.###_.'   ","    `---'    "],
    "Waning Crescent": ["    _..._    ","  .' **  '.  "," /  ***    \\ ","|  ****     |"," \\  ***    / ","  '.  **_.'  ","    `---'    "],
}

def get_moon_phase():
    now   = datetime.now(timezone.utc)
    ref   = datetime(2000, 1, 6, 18, 14, tzinfo=timezone.utc)
    pct   = ((now - ref).total_seconds() % (29.53058867 * 86400)) / (29.53058867 * 86400)
    names = ["New Moon","Waxing Crescent","First Quarter","Waxing Gibbous","Full Moon","Waning Gibbous","Last Quarter","Waning Crescent"]
    phase = names[int(pct * 8) % 8]
    illum = int(abs(math.sin(pct * math.pi)) * 100)
    days_into    = pct * 29.53
    days_to_full = abs(int(14.765 - days_into if days_into < 14.765 else 29.53 - days_into + 14.765))
    return phase, illum, days_to_full

def moon_panel():
    phase, illum, days = get_moon_phase()
    art = MOON_ART.get(phase, MOON_ART["Full Moon"])
    t   = Text()
    t.append("\n")
    for line in art:
        t.append(f"  {line}\n", style=CLR["CLR_MOON"])
    t.append(f"\n  {phase}\n",              style=f"bold {CLR['CLR_MOON']}")
    t.append(f"  {illum}% illuminated\n",   style=f"dim {CLR['CLR_MOON']}")
    t.append(f"\n  {days}d to full moon\n", style=f"italic dim {CLR['CLR_DIM']}")

    # Sunrise/sunset
    if sun_cache["sunrise"]:
        t.append(f"\n  sunrise  {sun_cache['sunrise']}\n", style=f"dim {CLR['CLR_WEATHER']}")
        t.append(f"  sunset   {sun_cache['sunset']}\n",    style=f"dim {CLR['CLR_WEATHER']}")
    else:
        t.append(f"\n  sunrise/sunset loading...\n", style=f"dim {CLR['CLR_DIM']}")

    return Panel(t, title=f"[{CLR['CLR_MOON']}]> MOON & SUN[/{CLR['CLR_MOON']}]", border_style=CLR["CLR_MOON"], box=box.ROUNDED)

# ── Weather ────────────────────────────────────────────────────────────────────

WEATHER_CODES = {
    0:("Clear sky","*"),1:("Mainly clear","*"),2:("Partly cloudy","~"),3:("Overcast","~"),
    45:("Foggy","."),48:("Icy fog","."),51:("Light drizzle",":"),53:("Drizzle",":"),
    55:("Heavy drizzle",":"),61:("Light rain",":"),63:("Rain",":"),65:("Heavy rain",":"),
    71:("Light snow","*"),73:("Snow","*"),75:("Heavy snow","*"),80:("Showers",":"),
    81:("Rain showers",":"),82:("Heavy showers","!"),95:("Thunderstorm","!"),
    96:("Hail storm","!"),99:("Hail storm","!"),
}

def fetch_weather(cfg):
    lat = cfg.get("city_lat")
    lon = cfg.get("city_lon")
    if not lat or not lon:
        weather_meta.update({"not_found": True})
        weather_cache["error"] = "No city set. Go to Settings > Reset City."
        return
    weather_meta.update({
        "url": get_weather_url_from_coords(lat, lon),
        "city": cfg.get("city",""),
        "country": cfg.get("city_country",""),
        "not_found": False,
        "lat": lat, "lon": lon,
    })
    while True:
        if time.time() - weather_cache["last"] > 300:
            try:
                r = requests.get(weather_meta["url"], verify=False, timeout=5)
                r.raise_for_status()
                data = r.json()
                weather_cache["data"]  = data
                weather_cache["error"] = None
                weather_cache["last"]  = time.time()
                # Parse sunrise/sunset
                try:
                    daily = data.get("daily", {})
                    sr = daily.get("sunrise", [None])[0]
                    ss = daily.get("sunset",  [None])[0]
                    if sr: sun_cache["sunrise"] = sr.split("T")[1] if "T" in sr else sr
                    if ss: sun_cache["sunset"]  = ss.split("T")[1] if "T" in ss else ss
                except Exception:
                    pass
            except Exception as e:
                weather_cache["error"] = str(e)[:40]
        time.sleep(30)

def weather_panel(temp_unit="F"):
    t = Text()
    t.append("\n")
    d = weather_cache["data"]
    if weather_meta.get("not_found"):
        t.append("  City not found!\n\n",          style="bold #FF4444")
        t.append("  Go to tab 6 SETTINGS\n",       style=f"dim {CLR['CLR_WEATHER']}")
        t.append("  and select Reset City\n",      style=f"dim {CLR['CLR_WEATHER']}")
    elif not d:
        t.append(f"  {weather_cache.get('error') or 'fetching...'}\n", style=f"dim {CLR['CLR_DIM']}")
    else:
        try:
            cur  = d["current"]
            temp = cur["temperature_2m"]
            if temp_unit == "C":
                temp = (temp - 32) * 5 / 9
            wind = cur["windspeed_10m"]
            hum  = cur["relative_humidity_2m"]
            desc, icon = WEATHER_CODES.get(cur["weathercode"], ("Unknown","?"))
            t.append(f"  [{icon}] ", style=f"bold {CLR['CLR_WEATHER']}")
            t.append(f"{temp:.0f}{temp_unit}", style=f"bold {CLR['CLR_WEATHER']}")
            t.append(f"   {desc}\n",           style=f"dim {CLR['CLR_WEATHER']}")
            t.append(f"\n  wind  {wind:.0f} mph\n",  style=f"dim {CLR['CLR_WEATHER']}")
            t.append(f"  humid {hum:.0f}%\n",         style=f"dim {CLR['CLR_WEATHER']}")
            city    = weather_meta["city"]
            country = weather_meta["country"]
            state   = _cfg_ref.get("city_state","")
            loc     = f"{city}, {state}, {country}" if state else f"{city}, {country}"
            t.append(f"\n  {loc}\n", style=f"italic dim {CLR['CLR_DIM']}")
        except Exception:
            t.append("  error reading data\n", style=f"dim {CLR['CLR_DIM']}")
    return Panel(t, title=f"[{CLR['CLR_WEATHER']}]> WEATHER[/{CLR['CLR_WEATHER']}]", border_style=CLR["CLR_WEATHER"], box=box.ROUNDED)

# ── Spotify ────────────────────────────────────────────────────────────────────

def init_spotify(client_id, client_secret):
    if not spotipy or not client_id or not client_secret:
        spotify_cache["error"] = "no keys" if spotipy else "pip install spotipy"
        return
    try:
        session = requests.Session()
        session.verify = False
        sp = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri="http://127.0.0.1:8888/callback",
                scope="user-read-playback-state user-read-currently-playing",
                open_browser=False,
                cache_path=SPOTIFY_CACHE,
                requests_session=session,
            ),
            requests_session=session,
        )
        sp.current_playback()
        spotify_cache["sp"]     = sp
        spotify_cache["authed"] = True
        spotify_cache["error"]  = None
    except Exception as e:
        spotify_cache["error"] = str(e)[:60]

def fetch_spotify(client_id, client_secret):
    init_spotify(client_id, client_secret)
    while True:
        sp = spotify_cache.get("sp")
        if sp:
            try:
                spotify_cache["data"]  = sp.current_playback()
                spotify_cache["error"] = None
            except Exception as e:
                spotify_cache["error"] = str(e)[:40]
        time.sleep(5)

def ms_to_str(ms):
    s = ms // 1000
    return f"{s // 60}:{s % 60:02d}"

def spotify_panel():
    t = Text()
    t.append("\n")
    cid = _cfg_ref.get("spotify_client_id","")
    if not cid:
        t.append("  Spotify not configured.\n\n",    style=f"dim {CLR['CLR_DIM']}")
        t.append("  Go to tab 6 > Advanced\n",       style=f"dim {CLR['CLR_SPOTIFY']}")
        t.append("  to enter your Spotify keys.\n",  style=f"dim {CLR['CLR_SPOTIFY']}")
        return Panel(t, title=f"[{CLR['CLR_SPOTIFY']}]> SPOTIFY[/{CLR['CLR_SPOTIFY']}]", border_style=CLR["CLR_SPOTIFY"], box=box.ROUNDED)
    if not spotify_cache["authed"]:
        err = spotify_cache.get("error","initializing...")
        t.append(f"  {err}\n", style=f"dim {CLR['CLR_DIM']}")
        return Panel(t, title=f"[{CLR['CLR_SPOTIFY']}]> SPOTIFY[/{CLR['CLR_SPOTIFY']}]", border_style=CLR["CLR_SPOTIFY"], box=box.ROUNDED)
    pb = spotify_cache.get("data")
    if not pb or not pb.get("item"):
        t.append("  [|] nothing playing\n", style=f"dim {CLR['CLR_DIM']}")
    elif not pb.get("is_playing"):
        t.append("  [|] paused\n",                                  style=f"dim {CLR['CLR_DIM']}")
        t.append(f"  {pb['item']['name'][:34]}\n",                   style=f"dim {CLR['CLR_SPOTIFY']}")
        t.append(f"  {pb['item']['artists'][0]['name'][:34]}\n",     style=f"dim {CLR['CLR_DIM']}")
    else:
        try:
            item     = pb["item"]
            progress = pb["progress_ms"]
            duration = item["duration_ms"]
            pct      = (progress / duration * 100) if duration else 0
            fill     = int(pct / 100 * 34)
            t.append("  [>] now playing\n",                                            style=f"bold {CLR['CLR_SPOTIFY']}")
            t.append(f"  {item['name'][:34]}\n",                                       style=f"bold {CLR['CLR_SPOTIFY']}")
            t.append(f"  {', '.join(a['name'] for a in item['artists'])[:34]}\n",      style=f"dim {CLR['CLR_SPOTIFY']}")
            t.append(f"  {item['album']['name'][:34]}\n\n",                            style=f"italic dim {CLR['CLR_DIM']}")
            t.append("  [",style=f"dim {CLR['CLR_DIM']}")
            t.append("#"*fill,style=f"bold {CLR['CLR_SPOTIFY']}")
            t.append("-"*(34-fill),style=f"dim {CLR['CLR_DIM']}")
            t.append(f"]  {ms_to_str(progress)}/{ms_to_str(duration)}\n",style=f"dim {CLR['CLR_DIM']}")
            vol    = pb.get("device",{}).get("volume_percent","?")
            device = pb.get("device",{}).get("name","")[:20]
            t.append(f"\n  vol {vol}%  {device}\n", style=f"dim {CLR['CLR_DIM']}")
        except Exception:
            t.append("  error reading track\n", style=f"dim {CLR['CLR_DIM']}")
    return Panel(t, title=f"[{CLR['CLR_SPOTIFY']}]> SPOTIFY[/{CLR['CLR_SPOTIFY']}]", border_style=CLR["CLR_SPOTIFY"], box=box.ROUNDED)

# ── Settings ───────────────────────────────────────────────────────────────────

SETTINGS_MAIN = [
    ("Theme",          "theme",          ["green","blue","pink","amber","red"]),
    ("Temperature",    "temp_unit",      ["F","C"]),
    ("Time format",    "time_format",    ["24","12"]),
    ("Speed interval", "speed_interval", [30, 60, 120, 0]),
    ("Reset city",     "_reset_city",    None),
    ("Force update",   "_force_update",  None),
    ("Advanced -->",   "_advanced",      None),
]

SETTINGS_ADV = [
    ("Spotify Client ID",     "spotify_client_id",     None),
    ("Spotify Client Secret", "spotify_client_secret", None),
    ("< Back",                "_back",                 None),
]

def settings_label(key, value):
    if key == "speed_interval": return "never" if value == 0 else f"{value} min"
    return str(value)

def settings_panel(cfg):
    section = settings_cursor["section"]
    items   = SETTINGS_ADV if section == "advanced" else SETTINGS_MAIN
    pos     = settings_cursor["pos"]

    t = Text()
    t.append("\n")

    if section == "advanced":
        t.append("  ADVANCED SETTINGS\n\n", style=f"bold {CLR['CLR_CLOCK']}")
        t.append("  Enter keys then press Enter to save\n\n", style=f"dim {CLR['CLR_DIM']}")
        for i, (label, key, _) in enumerate(items):
            selected = i == pos
            prefix   = "  [>] " if selected else "  [ ] "
            style    = f"bold {CLR['CLR_CLOCK']}" if selected else f"dim {CLR['CLR_DIM']}"
            if key in ("spotify_client_id","spotify_client_secret"):
                val = cfg.get(key,"")
                display = val[:6] + "..." if len(val) > 6 else (val or "not set")
                t.append(prefix, style=style)
                t.append(f"{label:<26}", style=style)
                t.append(f"{display}\n", style=f"dim {CLR['CLR_WEATHER']}")
            else:
                t.append(prefix, style=style)
                t.append(f"{label}\n", style=style)
    else:
        t.append("  Arrow keys navigate   Left/Right or Enter to change\n\n", style=f"dim {CLR['CLR_DIM']}")
        for i, (label, key, options) in enumerate(items):
            selected = i == pos
            prefix   = "  [>] " if selected else "  [ ] "
            style    = f"bold {CLR['CLR_CLOCK']}" if selected else f"dim {CLR['CLR_DIM']}"
            if options is None:
                t.append(prefix, style=style); t.append(f"{label}\n", style=style)
            else:
                val = cfg.get(key, options[0])
                t.append(prefix, style=style); t.append(f"{label:<20}", style=style)
                for opt in options:
                    opt_str = settings_label(key, opt)
                    if opt == val: t.append(f" [{opt_str}] ", style=f"bold {CLR['CLR_CLOCK']} reverse")
                    else: t.append(f"  {opt_str}  ", style=f"dim {CLR['CLR_DIM']}")
                t.append("\n")

    if settings_msg["text"] and time.time() - settings_msg["time"] < 4:
        t.append(f"\n  {settings_msg['text']}\n", style=f"bold {settings_msg['color']}")

    if section != "advanced":
        t.append(f"\n  Theme preview:\n", style=f"dim {CLR['CLR_DIM']}")
        for name, colors in THEMES.items():
            marker = " [*]" if name == cfg.get("theme","pink") else "  o "
            t.append(f"  {marker} {name}\n", style=f"bold {colors['CLR_CLOCK']}")

    title = "ADVANCED" if section == "advanced" else "SETTINGS"
    return Panel(t, title=f"[{CLR['CLR_CLOCK']}]> {title}[/{CLR['CLR_CLOCK']}]", border_style=CLR["CLR_CLOCK"], box=box.ROUNDED)

def handle_settings_input(ch, cfg):
    import msvcrt
    section = settings_cursor["section"]
    items   = SETTINGS_ADV if section == "advanced" else SETTINGS_MAIN
    pos     = settings_cursor["pos"]
    label, key, options = items[pos]

    if ch in ("\x00", "\xe0"):
        arrow = msvcrt.getwch()
        if arrow == "H": settings_cursor["pos"] = (pos - 1) % len(items)
        elif arrow == "P": settings_cursor["pos"] = (pos + 1) % len(items)
        elif arrow in ("K","M") and options:
            val     = cfg.get(key, options[0])
            idx     = options.index(val) if val in options else 0
            delta   = -1 if arrow == "K" else 1
            new_val = options[(idx + delta) % len(options)]
            cfg[key] = new_val; save_config(cfg)
            if key == "theme": apply_theme(new_val)
            settings_msg.update({"text": "Saved!", "color": CLR["CLR_CLOCK"], "time": time.time()})
        return

    if ch == "\r":
        if key == "_reset_city":
            cfg["city"] = ""; save_config(cfg)
            settings_msg.update({"text": "Restarting in 5 seconds...", "color": "#FF4444", "time": time.time()})
            threading.Thread(target=city_reset_countdown, daemon=False).start()
        elif key == "_force_update":
            update_status.update({"checked": False, "updated": False, "error": None, "log": []})
            threading.Thread(target=check_for_update, daemon=True).start()
            settings_msg.update({"text": "Checking for updates...", "color": CLR["CLR_SPEED"], "time": time.time()})
        elif key == "_advanced":
            settings_cursor["section"] = "advanced"
            settings_cursor["pos"]     = 0
        elif key == "_back":
            settings_cursor["section"] = "main"
            settings_cursor["pos"]     = 0
        elif key in ("spotify_client_id","spotify_client_secret"):
            # Input inline
            console.clear()
            console.print(f"\n  [{CLR['CLR_CLOCK']}]Enter {label}:[/{CLR['CLR_CLOCK']}]")
            console.print(f"  [{CLR['CLR_DIM']}](current: {cfg.get(key,'not set')[:20]})[/{CLR['CLR_DIM']}]\n")
            val = console.input(f"  [{CLR['CLR_WEATHER']}]>[/{CLR['CLR_WEATHER']}] ").strip()
            if val:
                cfg[key] = val; save_config(cfg)
                settings_msg.update({"text": "Saved! Restart to apply Spotify.", "color": CLR["CLR_SPOTIFY"], "time": time.time()})
            else:
                settings_msg.update({"text": "No change.", "color": CLR["CLR_DIM"], "time": time.time()})
        elif options:
            val     = cfg.get(key, options[0])
            idx     = options.index(val) if val in options else 0
            new_val = options[(idx + 1) % len(options)]
            cfg[key] = new_val; save_config(cfg)
            if key == "theme": apply_theme(new_val)
            settings_msg.update({"text": "Saved!", "color": CLR["CLR_CLOCK"], "time": time.time()})

# ── Game State ─────────────────────────────────────────────────────────────────
GAME_W, GAME_H = 50, 22

game_state = {
    "mode":"none",
    "snake_body":[],"snake_dir":(1,0),"snake_food":(0,0),"snake_score":0,"snake_alive":True,
    "flappy_y":11.0,"flappy_vel":0.0,"flappy_pipes":[],"flappy_score":0,"flappy_alive":True,
    "flappy_frame": 0,
}

def snake_init():
    cx,cy=GAME_W//2,GAME_H//2
    game_state.update({"snake_body":[(cx,cy),(cx-1,cy),(cx-2,cy)],"snake_dir":(1,0),"snake_score":0,"snake_alive":True})
    snake_place_food()

def snake_place_food():
    body=set(game_state["snake_body"])
    while True:
        f=(random.randint(1,GAME_W-2),random.randint(1,GAME_H-2))
        if f not in body: game_state["snake_food"]=f; break

def snake_tick():
    if not game_state["snake_alive"]: return
    dx,dy=game_state["snake_dir"]; hx,hy=game_state["snake_body"][0]; nx,ny=hx+dx,hy+dy
    if nx<=0 or nx>=GAME_W-1 or ny<=0 or ny>=GAME_H-1 or (nx,ny) in set(game_state["snake_body"]):
        game_state["snake_alive"]=False
        if game_state["snake_score"] > high_scores["snake"]:
            high_scores["snake"] = game_state["snake_score"]
            save_high_scores()
        return
    game_state["snake_body"].insert(0,(nx,ny))
    if (nx,ny)==game_state["snake_food"]: game_state["snake_score"]+=1; snake_place_food()
    else: game_state["snake_body"].pop()

def flappy_init():
    game_state.update({"flappy_y":float(GAME_H//2),"flappy_vel":0.0,"flappy_pipes":[],"flappy_score":0,"flappy_alive":True,"flappy_frame":0})
    for i in range(2): flappy_add_pipe(GAME_W+i*20)

def flappy_add_pipe(x):
    game_state["flappy_pipes"].append({"x":float(x),"gap":random.randint(3,GAME_H-8),"scored":False})

def flappy_tick():
    if not game_state["flappy_alive"]: return
    game_state["flappy_frame"] += 1
    # Smoother physics with smaller steps
    steps = 3
    for _ in range(steps):
        game_state["flappy_vel"] += 0.12 / steps
        game_state["flappy_y"]   += game_state["flappy_vel"] / steps
        by = game_state["flappy_y"]; bx = 6
        if by <= 0 or by >= GAME_H - 1:
            game_state["flappy_alive"] = False
            if game_state["flappy_score"] > high_scores["flappy"]:
                high_scores["flappy"] = game_state["flappy_score"]
                save_high_scores()
            return
        for p in game_state["flappy_pipes"]:
            p["x"] -= 0.4 / steps
            px = int(p["x"]); gap = p["gap"]
            if px == int(bx) and (by < gap or by > gap + 4):
                game_state["flappy_alive"] = False
                if game_state["flappy_score"] > high_scores["flappy"]:
                    high_scores["flappy"] = game_state["flappy_score"]
                    save_high_scores()
                return
            if p["x"] < bx and not p["scored"]:
                p["scored"] = True; game_state["flappy_score"] += 1
    game_state["flappy_pipes"] = [p for p in game_state["flappy_pipes"] if p["x"] > 0]
    if not game_state["flappy_pipes"] or game_state["flappy_pipes"][-1]["x"] < GAME_W - 15:
        flappy_add_pipe(GAME_W)

def render_snake():
    grid=[["." for _ in range(GAME_W)] for _ in range(GAME_H)]
    for x in range(GAME_W): grid[0][x]=grid[GAME_H-1][x]="-"
    for y in range(GAME_H): grid[y][0]=grid[y][GAME_W-1]="|"
    fx,fy=game_state["snake_food"]; grid[fy][fx]="o"
    for i,(bx,by) in enumerate(game_state["snake_body"]):
        if 0<=by<GAME_H and 0<=bx<GAME_W: grid[by][bx]="@" if i==0 else "#"
    t=Text()
    for row in grid: t.append("  "+"".join(row)+"\n",style=CLR["CLR_SNAKE"])
    if not game_state["snake_alive"]:
        t.append(f"\n  GAME OVER!  Score:{game_state['snake_score']}  Best:{high_scores['snake']}  Press S to restart\n",style=f"bold {CLR['CLR_SNAKE']}")
    else:
        t.append(f"\n  Score:{game_state['snake_score']}  Best:{high_scores['snake']}   WASD/arrows   Q to quit\n",style=f"dim {CLR['CLR_SNAKE']}")
    return t

def render_flappy():
    grid=[["." for _ in range(GAME_W)] for _ in range(GAME_H)]
    for x in range(GAME_W): grid[0][x]=grid[GAME_H-1][x]="-"
    for p in game_state["flappy_pipes"]:
        px=int(p["x"]); gap=p["gap"]
        if 0<=px<GAME_W:
            for y in range(GAME_H):
                if y<gap or y>gap+4: grid[y][px]="|"
    by=int(game_state["flappy_y"])
    # Bird animation
    frame  = game_state["flappy_frame"]
    bird   = ">" if frame % 4 < 2 else "}"
    if 0<=by<GAME_H: grid[by][6]=bird
    t=Text()
    for row in grid: t.append("  "+"".join(row)+"\n",style=CLR["CLR_FLAPPY"])
    if not game_state["flappy_alive"]:
        t.append(f"\n  GAME OVER!  Score:{game_state['flappy_score']}  Best:{high_scores['flappy']}  Press F to restart\n",style=f"bold {CLR['CLR_FLAPPY']}")
    else:
        t.append(f"\n  Score:{game_state['flappy_score']}  Best:{high_scores['flappy']}   SPACE to flap   Q to quit\n",style=f"dim {CLR['CLR_FLAPPY']}")
    return t

# ── Input handler ──────────────────────────────────────────────────────────────

def input_loop():
    try:
        import msvcrt
        while True:
            if msvcrt.kbhit():
                ch=msvcrt.getwch(); key=ch.lower(); mode=game_state["mode"]
                if key in ("1","2","3","4","5","6"):
                    current_tab["tab"]=int(key)
                    if key!="5": game_state["mode"]="none"
                elif current_tab["tab"]==6: handle_settings_input(ch,_cfg_ref)
                elif key=="s":
                    if mode!="snake": current_tab["tab"]=5; game_state["mode"]="snake"; snake_init()
                    elif not game_state["snake_alive"]: snake_init()
                elif key=="f":
                    if mode!="flappy": current_tab["tab"]=5; game_state["mode"]="flappy"; flappy_init()
                    elif not game_state["flappy_alive"]: flappy_init()
                elif key=="q": game_state["mode"]="none"
                elif mode=="snake":
                    if key=="a" and game_state["snake_dir"]!=(1,0): game_state["snake_dir"]=(-1,0)
                    elif key=="d" and game_state["snake_dir"]!=(-1,0): game_state["snake_dir"]=(1,0)
                    elif key=="w" and game_state["snake_dir"]!=(0,1): game_state["snake_dir"]=(0,-1)
                    elif ch in ("\x00","\xe0"):
                        a=msvcrt.getwch()
                        if a=="H" and game_state["snake_dir"]!=(0,1): game_state["snake_dir"]=(0,-1)
                        elif a=="P" and game_state["snake_dir"]!=(0,-1): game_state["snake_dir"]=(0,1)
                        elif a=="K" and game_state["snake_dir"]!=(1,0): game_state["snake_dir"]=(-1,0)
                        elif a=="M" and game_state["snake_dir"]!=(-1,0): game_state["snake_dir"]=(1,0)
                elif mode=="flappy":
                    if key in (" ","w"): game_state["flappy_vel"]=-2.2
            time.sleep(0.03)
    except Exception: pass

def game_loop():
    ls=lf=time.time()
    while True:
        now=time.time()
        if game_state["mode"]=="snake" and game_state["snake_alive"] and now-ls>0.13: snake_tick(); ls=now
        if game_state["mode"]=="flappy" and game_state["flappy_alive"] and now-lf>0.05: flappy_tick(); lf=now
        time.sleep(0.01)

# ── Helpers ────────────────────────────────────────────────────────────────────

def color_for(pct,base):
    if pct>=85: return "#FF4444"
    if pct>=60: return "#FFD93D"
    return base

def uptime_str():
    delta=datetime.now()-START_TIME; h,rem=divmod(int(delta.total_seconds()),3600); m,s=divmod(rem,60)
    return f"{h:02d}h {m:02d}m {s:02d}s"

def fmt_time(dt, fmt):
    if fmt == "12":
        return dt.strftime("%I:%M:%S %p")
    return dt.strftime("%H:%M:%S")

def file_hash(path):
    try:
        with open(path,"rb") as f: return hashlib.md5(f.read()).hexdigest()
    except Exception: return None

def smooth_bar(pct,width,color):
    t=Text(); fill=int(pct/100*width)
    t.append("[",style=f"dim {CLR['CLR_DIM']}"); t.append("#"*fill,style=f"bold {color}"); t.append("-"*(width-fill),style=f"dim {CLR['CLR_DIM']}"); t.append("]",style=f"dim {CLR['CLR_DIM']}")
    return t

def spark_line(history,width,color):
    t=Text(); bars=" ........||||||||"
    for v in list(history)[-width:]: t.append(bars[min(16,int(v/100*16))],style=color)
    return t

# ── Auto-updater ───────────────────────────────────────────────────────────────

def check_for_update():
    update_status["log"].append("connecting to github...")
    try:
        if IS_EXE:
            r = requests.get(GITHUB_LATEST_URL,verify=False,timeout=8); r.raise_for_status()
            data       = r.json(); latest_tag = data.get("tag_name","")
            update_status["new_version"] = latest_tag
            update_status["log"].append(f"latest:{latest_tag}  current:{CURRENT_VERSION}")
            if latest_tag and latest_tag != CURRENT_VERSION:
                update_status["log"].append("update found! downloading exe...")
                assets  = data.get("assets",[])
                exe_url = next((a["browser_download_url"] for a in assets if a["name"].endswith(".exe")), None)
                if exe_url:
                    tmp_path = THIS_FILE + ".new"
                    r2 = requests.get(exe_url,verify=False,timeout=60,stream=True); r2.raise_for_status()
                    with open(tmp_path,"wb") as f:
                        for chunk in r2.iter_content(chunk_size=8192): f.write(chunk)
                    bat_path = os.path.join(THIS_DIR,"zzboard_update.bat")
                    with open(bat_path,"w") as f:
                        f.write(f'@echo off\ntimeout /t 2 /nobreak >nul\nmove /y "{tmp_path}" "{THIS_FILE}"\nstart "" "{THIS_FILE}" --no-splash\ndel "%~f0"\n')
                    update_status["log"].append("update ready!"); update_status["updated"]=True; update_status["bat_path"]=bat_path
                else:
                    update_status["log"].append("no exe in release.")
            else:
                update_status["log"].append("already up to date.")
        else:
            r=requests.get(GITHUB_RAW_URL,verify=False,timeout=8); r.raise_for_status()
            remote_code=r.text; update_status["log"].append("comparing versions...")
            if file_hash(THIS_FILE)!=hashlib.md5(remote_code.encode()).hexdigest():
                update_status["log"].append("update found! downloading...")
                time.sleep(0.4)
                with open(THIS_FILE,"w",encoding="utf-8") as f: f.write(remote_code)
                update_status["log"].append("update applied!"); update_status["updated"]=True
            else:
                update_status["log"].append("already up to date.")
    except Exception: update_status["log"].append("update check failed.")
    update_status["checked"]=True

def apply_exe_update_and_restart():
    bat=update_status.get("bat_path")
    if bat and os.path.exists(bat):
        subprocess.Popen(["cmd","/c",bat],creationflags=subprocess.CREATE_NEW_CONSOLE)
        time.sleep(0.5); sys.exit(0)
    else: do_restart()

CAT_FRAMES = [
    ["         z z z          ","        z                ","   /\\_____/\\             ","  ( o  .  o )~~~~~~~~~~  ","   >   ^   <  zzzboard   ","  (_____)________________"],
    ["          Z z z         ","         z               ","   /\\_____/\\             ","  ( -  .  - )~~~~~~~~~~  ","   >   ^   <  zzzboard   ","  (_____)________________"],
    ["           Z Z z        ","          z              ","   /\\_____/\\             ","  ( o  .  - )~~~~~~~~~~  ","   >   ^   <  zzzboard   ","  (_____)________________"],
    ["         z Z z          ","        z                ","   /\\_____/\\             ","  ( ~  .  ~ )~~~~~~~~~~  ","   >   ^   <  zzzboard   ","  (_____)________________"],
]

LOADING_STEPS = ["booting up...","checking for updates...","fetching weather...","calculating moon phase...","warming up monitors...","all systems go  zzz..."]

def cat_screen(extra_line="",progress=None):
    t=Text(justify="center"); t.append("\n")
    colors=[CLR["CLR_CLOCK"],CLR["CLR_WEATHER"],CLR["CLR_MOON"],CLR["CLR_TASKS"],CLR["CLR_CPU"]]
    for i,line in enumerate(ZZBOARD_LOGO): t.append(line+"\n",style=f"bold {colors[i%len(colors)]}")
    t.append(f"{'  PUBLIC EDITION  -- made by @wtfplutolol with <3':^50}\n\n",style=f"dim {CLR['CLR_MOON']}")
    for line in CAT_FRAMES[int(time.time()*3)%len(CAT_FRAMES)]: t.append(line+"\n",style=CLR["CLR_CLOCK"])
    t.append("\n"); t.append(f"  {extra_line}\n",style=f"dim {CLR['CLR_WEATHER']}")
    if progress is not None:
        fill=int(progress)
        t.append("\n  [",style=f"dim {CLR['CLR_DIM']}"); t.append("#"*fill,style=CLR["CLR_CLOCK"])
        t.append("-"*(36-fill),style=f"dim {CLR['CLR_DIM']}"); t.append("]\n",style=f"dim {CLR['CLR_DIM']}")
    return Align.center(t,vertical="middle")

def show_update_screen():
    done=threading.Event()
    threading.Thread(target=lambda:[check_for_update(),done.set()],daemon=True).start()
    while not done.is_set():
        log=update_status["log"][-1] if update_status["log"] else "connecting..."
        with Live(cat_screen(f"> {log}"),console=console,screen=True,refresh_per_second=4): time.sleep(0.25)
    if update_status["updated"]:
        with Live(cat_screen("> update ready! showing changelog..."),console=console,screen=True,refresh_per_second=4): time.sleep(1.5)
        show_changelog()
        if IS_EXE: apply_exe_update_and_restart()
        else: do_restart()
    else:
        msg="> up to date!" if not update_status["error"] else "> continuing offline..."
        with Live(cat_screen(msg),console=console,screen=True,refresh_per_second=4): time.sleep(1.5)

def show_splash():
    for tick in range(36):
        step=LOADING_STEPS[min(tick//max(1,36//len(LOADING_STEPS)),len(LOADING_STEPS)-1)]
        with Live(cat_screen(f"> {step}",tick),console=console,screen=True,refresh_per_second=4): time.sleep(0.1)
    time.sleep(0.3)

# ── File watcher ───────────────────────────────────────────────────────────────

class ReloadHandler(FileSystemEventHandler):
    def on_modified(self,event):
        if os.path.abspath(event.src_path)==THIS_FILE: reload_flag.set()

def start_watcher():
    if IS_EXE or Observer is None: return
    h=ReloadHandler(); o=Observer()
    o.schedule(h,path=os.path.dirname(THIS_FILE) or ".",recursive=False); o.start()

# ── Speed test ─────────────────────────────────────────────────────────────────

def run_speed_test():
    if not speedtest_lib: speed_cache["error"]="pip install speedtest-cli"; return
    try:
        speed_cache["testing"]=True; speed_cache["error"]=None
        st=speedtest_lib.Speedtest(); st.get_best_server()
        speed_cache["ping"]=st.results.ping
        st.download(); speed_cache["download"]=st.results.download/1_000_000
        st.upload();   speed_cache["upload"]=st.results.upload/1_000_000
        speed_cache["last"]=time.time()
    except Exception as e: speed_cache["error"]=str(e)[:40]
    finally: speed_cache["testing"]=False

def fetch_speed():
    run_speed_test()
    while True:
        mins=_cfg_ref.get("speed_interval",30)
        if mins==0: time.sleep(60); continue
        time.sleep(mins*60); run_speed_test()

# ── System panels ──────────────────────────────────────────────────────────────

def clock_panel(time_format="24"):
    now=datetime.now(); sep=":" if int(time.time())%2 else " "
    t=Text(justify="center"); t.append("\n")
    if time_format=="12":
        h=now.strftime("%I"); m=now.strftime("%M"); s=now.strftime("%S"); ampm=now.strftime(" %p")
        t.append(f"{h}{sep}{m}{sep}{s}{ampm}",style=f"bold {CLR['CLR_CLOCK']}")
    else:
        t.append(f"{now.strftime('%H')}{sep}{now.strftime('%M')}{sep}{now.strftime('%S')}",style=f"bold {CLR['CLR_CLOCK']}")
    t.append("\n"); t.append(now.strftime("%A, %d %B %Y").upper(),style=f"dim {CLR['CLR_WEATHER']}")
    t.append("\n"); t.append(f"uptime  {uptime_str()}  |  {CURRENT_VERSION}",style=f"italic dim {CLR['CLR_DIM']}"); t.append("\n")
    return Panel(t,title=f"[{CLR['CLR_CLOCK']}]  -- Z Z B O A R D  PUBLIC {CURRENT_VERSION} -- made by @wtfplutolol --  [/{CLR['CLR_CLOCK']}]",border_style=CLR["CLR_CLOCK"],box=box.DOUBLE,padding=(0,2))

def cpu_panel():
    pct=psutil.cpu_percent(interval=None); freq=psutil.cpu_freq(); CPU_HIST.append(pct); col=color_for(pct,CLR["CLR_CPU"])
    t=Text(); t.append(f"\n  {pct:5.1f}%  {psutil.cpu_count()} cores",style=f"bold {col}")
    if freq: t.append(f"  {freq.current/1000:.2f} GHz",style=f"dim {CLR['CLR_CPU']}")
    t.append("\n\n  "); t.append_text(smooth_bar(pct,40,col))
    t.append("\n\n  "); t.append_text(spark_line(CPU_HIST,40,col))
    t.append("\n\n  ")
    for i,c in enumerate(psutil.cpu_percent(percpu=True,interval=None)):
        filled=int(c/100*4); t.append("#"*filled+"."*(4-filled),style=color_for(c,CLR["CLR_CPU"])); t.append(" ")
        if (i+1)%10==0: t.append("\n  ")
    t.append("\n")
    return Panel(t,title=f"[{CLR['CLR_CPU']}]> CPU[/{CLR['CLR_CPU']}]",border_style=CLR["CLR_CPU"],box=box.ROUNDED)

def mem_panel():
    vm=psutil.virtual_memory(); sw=psutil.swap_memory(); pct=vm.percent; MEM_HIST.append(pct); col=color_for(pct,CLR["CLR_MEM"])
    t=Text(); t.append(f"\n  {vm.used/1024**3:.1f} / {vm.total/1024**3:.1f} GB  {pct:.0f}%\n\n",style=f"bold {col}")
    t.append("  "); t.append_text(smooth_bar(pct,40,col))
    t.append("\n\n  "); t.append_text(spark_line(MEM_HIST,40,col))
    if sw.total>0:
        t.append(f"\n\n  swap  {sw.used/1024**3:.1f}/{sw.total/1024**3:.1f} GB\n  ")
        t.append_text(smooth_bar(sw.percent,40,color_for(sw.percent,CLR["CLR_MEM"])))
    t.append("\n\n")
    return Panel(t,title=f"[{CLR['CLR_MEM']}]> MEMORY[/{CLR['CLR_MEM']}]",border_style=CLR["CLR_MEM"],box=box.ROUNDED)

def disk_panel():
    t=Text(); t.append("\n")
    for p in psutil.disk_partitions(all=False)[:4]:
        try:
            u=psutil.disk_usage(p.mountpoint); col=color_for(u.percent,CLR["CLR_DISK"])
            t.append(f"  {p.mountpoint[:12].ljust(12)} "); t.append_text(smooth_bar(u.percent,28,col)); t.append(f" {u.percent:3.0f}%\n",style=col)
        except Exception: continue
    net=psutil.net_io_counters()
    t.append(f"\n  up   {net.bytes_sent/1024**2:>8.1f} MB\n",style=f"dim {CLR['CLR_DISK']}")
    t.append(f"  down {net.bytes_recv/1024**2:>8.1f} MB\n",style=CLR["CLR_DISK"])
    return Panel(t,title=f"[{CLR['CLR_DISK']}]> DISK & NET[/{CLR['CLR_DISK']}]",border_style=CLR["CLR_DISK"],box=box.ROUNDED)

def tasks_panel(tasks):
    t=Text(); t.append("\n")
    for task in tasks: t.append(f"  [ ]  {task}\n",style=CLR["CLR_TASKS"])
    t.append(f"\n  edit zzboard_config.json to change\n",style=f"italic dim {CLR['CLR_DIM']}")
    return Panel(t,title=f"[{CLR['CLR_TASKS']}]> TASKS[/{CLR['CLR_TASKS']}]",border_style=CLR["CLR_TASKS"],box=box.ROUNDED)

def procs_panel():
    procs=sorted(psutil.process_iter(["pid","name","cpu_percent","memory_percent"]),key=lambda p:p.info["cpu_percent"] or 0,reverse=True)[:8]
    t=Text(); t.append(f"\n  {'PID':>6}  {'NAME':<22}{'CPU':>6}  {'MEM':>6}\n",style=f"bold {CLR['CLR_PROCS']}")
    t.append(f"  {'─'*6}  {'─'*22}{'─'*6}  {'─'*6}\n",style=f"dim {CLR['CLR_DIM']}")
    for p in procs:
        cpu=p.info["cpu_percent"] or 0.0; mem=p.info["memory_percent"] or 0.0; name=(p.info["name"] or "?")[:22]
        t.append(f"  {p.info['pid']:>6}  {name:<22}{cpu:>5.1f}%  {mem:>5.1f}%\n",style=color_for(cpu,CLR["CLR_PROCS"]))
    t.append("\n")
    return Panel(t,title=f"[{CLR['CLR_PROCS']}]> TOP PROCESSES[/{CLR['CLR_PROCS']}]",border_style=CLR["CLR_PROCS"],box=box.ROUNDED)

def speed_panel():
    t=Text(); t.append("\n")
    if speed_cache["testing"]:
        t.append(f"  running speed test{'.'*(int(time.time()*2)%4)}\n",style=f"dim {CLR['CLR_SPEED']}")
    elif speed_cache["error"]:
        t.append(f"  {speed_cache['error']}\n",style=f"dim {CLR['CLR_DIM']}")
    elif speed_cache["download"] is None:
        t.append(f"  waiting for results{'.'*(int(time.time()*2)%4)}\n",style=f"dim {CLR['CLR_DIM']}")
    else:
        dl,ul,ping=speed_cache["download"],speed_cache["upload"],speed_cache["ping"]; mx=max(dl,ul,100)
        t.append(f"  down  "); t.append_text(smooth_bar(dl/mx*100,36,CLR["CLR_SPEED"])); t.append(f"  {dl:.1f} Mbps\n",style=f"bold {CLR['CLR_SPEED']}")
        t.append(f"\n  up    "); t.append_text(smooth_bar(ul/mx*100,36,CLR["CLR_SPEED"])); t.append(f"  {ul:.1f} Mbps\n",style=f"bold {CLR['CLR_SPEED']}")
        t.append(f"\n  ping  {ping:.0f} ms",style=f"dim {CLR['CLR_SPEED']}")
        if speed_cache["last"]: t.append(f"   tested {int((time.time()-speed_cache['last'])/60)}m ago\n",style=f"italic dim {CLR['CLR_DIM']}")
    return Panel(t,title=f"[{CLR['CLR_SPEED']}]> SPEED TEST[/{CLR['CLR_SPEED']}]",border_style=CLR["CLR_SPEED"],box=box.ROUNDED)

# ── Tab bar ────────────────────────────────────────────────────────────────────

def tab_bar():
    tab=current_tab["tab"]
    tabs=[(1,"1 SYSTEM",CLR["CLR_CPU"]),(2,"2 SKY",CLR["CLR_MOON"]),(3,"3 STORAGE",CLR["CLR_DISK"]),
          (4,"4 SPEED",CLR["CLR_SPEED"]),(5,"5 GAMES",CLR["CLR_SNAKE"]),(6,"6 SETTINGS",CLR["CLR_CLOCK"])]
    t=Text()
    for num,label,color in tabs:
        if num==tab: t.append(f" [{label}] ",style=f"bold {color} reverse")
        else: t.append(f"  {label}  ",style=f"dim {CLR['CLR_DIM']}")
        t.append(" ")
    return Panel(t,border_style=CLR["CLR_DIM"],box=box.SIMPLE,padding=(0,1))

# ── Tab layouts ────────────────────────────────────────────────────────────────

def build_tab1(cfg):
    has_spotify = bool(cfg.get("spotify_client_id"))
    layout = Layout()
    if has_spotify:
        layout.split_column(
            Layout(name="clock",   size=7),
            Layout(name="stats",   ratio=2),
            Layout(name="spotify", ratio=1),
        )
        layout["stats"].split_row(Layout(name="cpu",ratio=1),Layout(name="mem",ratio=1))
        layout["spotify"].update(spotify_panel())
    else:
        layout.split_column(Layout(name="clock",size=7),Layout(name="stats",ratio=1))
        layout["stats"].split_row(Layout(name="cpu",ratio=1),Layout(name="mem",ratio=1))
    layout["clock"].update(clock_panel(cfg.get("time_format","24")))
    layout["cpu"].update(cpu_panel())
    layout["mem"].update(mem_panel())
    return layout

def build_tab2(cfg):
    layout=Layout()
    layout.split_row(Layout(name="weather",ratio=1),Layout(name="moon",ratio=1))
    layout["weather"].update(weather_panel(cfg.get("temp_unit","F"))); layout["moon"].update(moon_panel())
    return layout

def build_tab3(cfg):
    layout=Layout()
    layout.split_row(Layout(name="disk",ratio=1),Layout(name="tasks",ratio=1),Layout(name="procs",ratio=2))
    layout["disk"].update(disk_panel()); layout["tasks"].update(tasks_panel(cfg.get("tasks",[]))); layout["procs"].update(procs_panel())
    return layout

def build_tab4(cfg): return speed_panel()

def build_tab5(cfg):
    mode=game_state["mode"]
    if mode=="snake": return Panel(render_snake(),title=f"[{CLR['CLR_SNAKE']}]> SNAKE  score:{game_state['snake_score']}  best:{high_scores['snake']}  Q=quit[/{CLR['CLR_SNAKE']}]",border_style=CLR["CLR_SNAKE"],box=box.ROUNDED)
    elif mode=="flappy": return Panel(render_flappy(),title=f"[{CLR['CLR_FLAPPY']}]> FLAPPY  score:{game_state['flappy_score']}  best:{high_scores['flappy']}  Q=quit[/{CLR['CLR_FLAPPY']}]",border_style=CLR["CLR_FLAPPY"],box=box.ROUNDED)
    else:
        t=Text(); t.append("\n\n")
        t.append("  Press S to play Snake\n\n",style=f"bold {CLR['CLR_SNAKE']}")
        t.append(f"     WASD or arrow keys   Best: {high_scores['snake']}\n\n",style=f"dim {CLR['CLR_SNAKE']}")
        t.append("  Press F to play Flappy Bird\n\n",style=f"bold {CLR['CLR_FLAPPY']}")
        t.append(f"     SPACE to flap   Best: {high_scores['flappy']}\n\n",style=f"dim {CLR['CLR_FLAPPY']}")
        t.append("  Q to quit back to dashboard\n",style=f"dim {CLR['CLR_DIM']}")
        return Panel(t,title=f"[{CLR['CLR_SNAKE']}]> MINI GAMES[/{CLR['CLR_SNAKE']}]",border_style=CLR["CLR_SNAKE"],box=box.ROUNDED)

def build_tab6(cfg): return settings_panel(cfg)

def build_layout(cfg):
    layout=Layout()
    layout.split_column(Layout(name="tabs",size=3),Layout(name="content",ratio=1))
    layout["tabs"].update(tab_bar())
    layout["content"].update({1:build_tab1,2:build_tab2,3:build_tab3,4:build_tab4,5:build_tab5,6:build_tab6}[current_tab["tab"]](cfg))
    return layout

# ── Entry ──────────────────────────────────────────────────────────────────────

def main():
    parser=argparse.ArgumentParser(description="ZZBoard Public v1.4")
    parser.add_argument("--no-splash",action="store_true")
    args=parser.parse_args()

    apply_theme("pink")
    cfg=load_config()
    if not cfg.get("city"): cfg=first_launch_setup()
    apply_theme(cfg.get("theme","pink"))
    _cfg_ref.update(cfg)
    load_high_scores()

    threading.Thread(target=lambda:fetch_weather(cfg),daemon=True).start()
    threading.Thread(target=fetch_speed,daemon=True).start()
    threading.Thread(target=input_loop,daemon=True).start()
    threading.Thread(target=game_loop,daemon=True).start()

    cid = cfg.get("spotify_client_id","")
    cs  = cfg.get("spotify_client_secret","")
    if cid and cs:
        threading.Thread(target=lambda:fetch_spotify(cid,cs),daemon=True).start()

    psutil.cpu_percent(interval=0.1,percpu=True)
    start_watcher()

    if not args.no_splash:
        show_update_screen()
        show_splash()

    try:
        with Live(build_layout(_cfg_ref),console=console,refresh_per_second=4,screen=True) as live:
            while True:
                if reload_flag.is_set(): do_restart()
                if update_status.get("updated") and update_status.get("checked"):
                    update_status["updated"]=False
                    show_changelog()
                    if IS_EXE: apply_exe_update_and_restart()
                    else: do_restart()
                time.sleep(0.25)
                live.update(build_layout(_cfg_ref))
    except KeyboardInterrupt:
        pass

    console.print(f"\n[bold {CLR['CLR_CLOCK']}]  ZZBOARD PUBLIC[/bold {CLR['CLR_CLOCK']}] [dim {CLR['CLR_DIM']}]terminated. sweet dreams. -- made by @wtfplutolol with <3[/dim {CLR['CLR_DIM']}]\n")

if __name__=="__main__":
    main()
