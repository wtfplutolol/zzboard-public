# -*- coding: utf-8 -*-
#!/usr/bin/env python3
# ZZBoard Public v1.2
# https://github.com/wtfplutolol/zzboard-public
# Made by @wtfplutolol with <3
# Requirements: pip install psutil rich requests speedtest-cli watchdog
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
    print("Run: pip install psutil rich requests speedtest-cli watchdog")
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
    print("Run: pip install psutil rich requests speedtest-cli watchdog")
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
CONFIG_FILE    = os.path.join(THIS_DIR, "zzboard_config.json")
GITHUB_RAW_URL = "https://raw.githubusercontent.com/wtfplutolol/zzboard-public/main/zzboard_public.py"

# ── Changelog ─────────────────────────────────────────────────────────────────
CHANGELOG = [
    ("v1.2", [
        "Pink is now the default theme",
        "City reset now shows a 5 second countdown then auto-restarts",
        "City not found now shows a clear error instead of loading forever",
        "Changelog screen added after updates",
        "Enter key to dismiss changelog and enter dashboard",
    ]),
    ("v1.1", [
        "Settings tab added (tab 6)",
        "Theme switcher: green, blue, pink, amber, red",
        "Temperature unit toggle (F/C)",
        "Speed test interval setting",
        "Force update check from settings",
        "City reset from settings",
    ]),
    ("v1.0", [
        "Initial public release",
        "5 tabs: System, Sky, Storage, Speed, Games",
        "Moon phase with ASCII art",
        "Weather by city",
        "Snake + Flappy Bird mini games",
        "Auto-updater from GitHub",
    ]),
]

# ── Themes ─────────────────────────────────────────────────────────────────────
THEMES = {
    "green": {
        "CLR_CLOCK":"#00FFB2","CLR_CPU":"#FF6B6B","CLR_MEM":"#FFD93D",
        "CLR_WEATHER":"#6BCBFF","CLR_MOON":"#E0E0FF","CLR_DISK":"#A8FF78",
        "CLR_TASKS":"#BD93F9","CLR_PROCS":"#FF9F43","CLR_SPEED":"#00CEC9",
        "CLR_SNAKE":"#00FF00","CLR_FLAPPY":"#FFD700","CLR_DIM":"#555566",
    },
    "blue": {
        "CLR_CLOCK":"#00BFFF","CLR_CPU":"#87CEEB","CLR_MEM":"#4169E1",
        "CLR_WEATHER":"#00CED1","CLR_MOON":"#E0E8FF","CLR_DISK":"#1E90FF",
        "CLR_TASKS":"#6495ED","CLR_PROCS":"#00BFFF","CLR_SPEED":"#40E0D0",
        "CLR_SNAKE":"#00FF7F","CLR_FLAPPY":"#87CEFA","CLR_DIM":"#334455",
    },
    "pink": {
        "CLR_CLOCK":"#FF79C6","CLR_CPU":"#FF6B9D","CLR_MEM":"#FFB3DE",
        "CLR_WEATHER":"#FF85C8","CLR_MOON":"#FFE0F0","CLR_DISK":"#FF69B4",
        "CLR_TASKS":"#DA70D6","CLR_PROCS":"#FF1493","CLR_SPEED":"#FF82AB",
        "CLR_SNAKE":"#FF69B4","CLR_FLAPPY":"#FFB6C1","CLR_DIM":"#553344",
    },
    "amber": {
        "CLR_CLOCK":"#FFB000","CLR_CPU":"#FF8C00","CLR_MEM":"#FFD700",
        "CLR_WEATHER":"#FFA500","CLR_MOON":"#FFEEBB","CLR_DISK":"#FFCC00",
        "CLR_TASKS":"#FF9F43","CLR_PROCS":"#FF6347","CLR_SPEED":"#FFC125",
        "CLR_SNAKE":"#ADFF2F","CLR_FLAPPY":"#FFD700","CLR_DIM":"#554433",
    },
    "red": {
        "CLR_CLOCK":"#FF4444","CLR_CPU":"#FF6B6B","CLR_MEM":"#FF8080",
        "CLR_WEATHER":"#FF6666","CLR_MOON":"#FFE0E0","CLR_DISK":"#FF5555",
        "CLR_TASKS":"#CC3333","CLR_PROCS":"#FF0000","CLR_SPEED":"#FF3333",
        "CLR_SNAKE":"#FF6666","CLR_FLAPPY":"#FFB3B3","CLR_DIM":"#553333",
    },
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
settings_cursor = {"pos": 0}
settings_msg    = {"text": "", "color": "#FF79C6", "time": 0}

weather_cache = {"data": None, "error": None, "last": 0}
speed_cache   = {"download": None, "upload": None, "ping": None, "testing": False, "last": 0, "error": None}
update_status = {"checked": False, "updated": False, "error": None, "log": []}
weather_meta  = {"url": None, "city": "Unknown", "country": "", "not_found": False}
_cfg_ref      = {}

# ── Config helpers ─────────────────────────────────────────────────────────────

DEFAULT_CONFIG = {
    "city": "", "theme": "pink", "temp_unit": "F",
    "speed_interval": 30, "tasks": ["Review pull requests", "Update dependencies", "Write docs"]
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
    """Restart without --no-splash so setup runs again."""
    args = [THIS_FILE] if IS_EXE else [sys.executable, THIS_FILE]
    try:
        subprocess.Popen(args, creationflags=subprocess.CREATE_NEW_CONSOLE if IS_EXE else 0)
    except Exception:
        subprocess.Popen(args)
    time.sleep(1.0)
    sys.exit(0)

# ── City reset with countdown ──────────────────────────────────────────────────

def city_reset_countdown():
    """Show a 5 second countdown then restart for city setup."""
    for i in range(5, 0, -1):
        t = Text(justify="center")
        t.append("\n\n\n")
        t.append("  City has been reset!\n\n", style=f"bold {CLR['CLR_CLOCK']}")
        t.append(f"  Restarting in {i}...\n\n", style=f"bold {CLR['CLR_WEATHER']}")
        t.append("  You will be asked for your new city\n", style=f"dim {CLR['CLR_DIM']}")
        with Live(Align.center(t, vertical="middle"), console=console, screen=True, refresh_per_second=10):
            time.sleep(1.0)
    do_restart_fresh()

# ── Changelog screen ───────────────────────────────────────────────────────────

def show_changelog():
    """Show changelog after an update. User must press Enter to continue."""
    while True:
        t = Text(justify="center")
        t.append("\n")
        colors = [CLR["CLR_CLOCK"], CLR["CLR_WEATHER"], CLR["CLR_MOON"], CLR["CLR_TASKS"], CLR["CLR_CPU"]]
        for i, line in enumerate(ZZBOARD_LOGO):
            t.append(line + "\n", style=f"bold {colors[i % len(colors)]}")
        t.append("\n")
        t.append("  WHATS NEW\n\n", style=f"bold {CLR['CLR_CLOCK']}")

        for version, changes in CHANGELOG:
            t.append(f"  {version}\n", style=f"bold {CLR['CLR_WEATHER']}")
            for change in changes:
                t.append(f"    + {change}\n", style=f"dim {CLR['CLR_MOON']}")
            t.append("\n")

        t.append("\n")
        t.append("  ----------------------------------------\n", style=f"dim {CLR['CLR_DIM']}")
        t.append("  Press ENTER to go to the dashboard  >>  \n", style=f"bold {CLR['CLR_CLOCK']} reverse")
        t.append("  ----------------------------------------\n", style=f"dim {CLR['CLR_DIM']}")

        with Live(Align.center(t, vertical="middle"), console=console, screen=True, refresh_per_second=2):
            time.sleep(0.1)

        # Check for Enter key
        try:
            import msvcrt
            if msvcrt.kbhit():
                ch = msvcrt.getwch()
                if ch == "\r":
                    break
        except Exception:
            break

        time.sleep(0.1)

# ── First launch setup ─────────────────────────────────────────────────────────

def first_launch_setup():
    console.clear()
    colors = [CLR["CLR_CLOCK"], CLR["CLR_WEATHER"], CLR["CLR_MOON"], CLR["CLR_TASKS"], CLR["CLR_CPU"]]
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
        city = console.input(f"  [{CLR['CLR_WEATHER']}]Your city for weather (e.g. London, Tokyo, New York):[/{CLR['CLR_WEATHER']}] ").strip()
        if not city:
            city = "New York"

        # Validate city exists
        console.print(f"  [{CLR['CLR_DIM']}]Checking city...[/{CLR['CLR_DIM']}]")
        url, name, country = get_weather_url(city)
        if url:
            console.print(f"  [bold {CLR['CLR_CLOCK']}]Found: {name}, {country}[/bold {CLR['CLR_CLOCK']}]")
            break
        else:
            console.print(f"  [bold #FF4444]City '{city}' not found! Please try again.[/bold #FF4444]")

    cfg = dict(DEFAULT_CONFIG)
    cfg["city"] = name
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
    return Panel(t, title=f"[{CLR['CLR_MOON']}]> MOON PHASE[/{CLR['CLR_MOON']}]", border_style=CLR["CLR_MOON"], box=box.ROUNDED)

# ── Weather ────────────────────────────────────────────────────────────────────

WEATHER_CODES = {
    0:("Clear sky","*"),1:("Mainly clear","*"),2:("Partly cloudy","~"),3:("Overcast","~"),
    45:("Foggy","."),48:("Icy fog","."),51:("Light drizzle",":"),53:("Drizzle",":"),
    55:("Heavy drizzle",":"),61:("Light rain",":"),63:("Rain",":"),65:("Heavy rain",":"),
    71:("Light snow","*"),73:("Snow","*"),75:("Heavy snow","*"),80:("Showers",":"),
    81:("Rain showers",":"),82:("Heavy showers","!"),95:("Thunderstorm","!"),
    96:("Hail storm","!"),99:("Hail storm","!"),
}

def get_weather_url(city):
    try:
        geo = requests.get(
            f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1",
            verify=False, timeout=5
        ).json()
        results = geo.get("results")
        if not results:
            return None, city, ""
        r   = results[0]
        lat, lon = r["latitude"], r["longitude"]
        url = (f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
               f"&current=temperature_2m,weathercode,windspeed_10m,relative_humidity_2m"
               f"&temperature_unit=fahrenheit&windspeed_unit=mph&timezone=auto")
        return url, r.get("name", city), r.get("country_code", "")
    except Exception:
        return None, city, ""

def fetch_weather(city):
    url, name, country = get_weather_url(city)
    if not url:
        weather_meta.update({"url": None, "city": city, "country": "", "not_found": True})
        weather_cache["error"] = f"City '{city}' not found. Go to Settings > Reset City."
        return
    weather_meta.update({"url": url, "city": name, "country": country, "not_found": False})
    while True:
        if time.time() - weather_cache["last"] > 300:
            try:
                r = requests.get(weather_meta["url"], verify=False, timeout=5)
                r.raise_for_status()
                weather_cache["data"]  = r.json()
                weather_cache["error"] = None
                weather_cache["last"]  = time.time()
            except Exception as e:
                weather_cache["error"] = str(e)[:40]
        time.sleep(30)

def weather_panel(temp_unit="F"):
    t = Text()
    t.append("\n")
    d = weather_cache["data"]

    if weather_meta.get("not_found"):
        t.append(f"  City not found!\n\n",               style=f"bold #FF4444")
        t.append(f"  '{weather_meta['city']}' could not be located.\n\n", style=f"dim {CLR['CLR_DIM']}")
        t.append(f"  Go to tab 6 SETTINGS\n",            style=f"dim {CLR['CLR_WEATHER']}")
        t.append(f"  and select Reset City\n",           style=f"dim {CLR['CLR_WEATHER']}")
        t.append(f"  to enter a new city.\n",            style=f"dim {CLR['CLR_WEATHER']}")
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
            t.append(f"\n  {weather_meta['city']}, {weather_meta['country']}\n", style=f"italic dim {CLR['CLR_DIM']}")
        except Exception:
            t.append("  error reading data\n", style=f"dim {CLR['CLR_DIM']}")
    return Panel(t, title=f"[{CLR['CLR_WEATHER']}]> WEATHER[/{CLR['CLR_WEATHER']}]", border_style=CLR["CLR_WEATHER"], box=box.ROUNDED)

# ── ASCII Art ──────────────────────────────────────────────────────────────────

ZZBOARD_LOGO = [
    "  ________ ______  ____  ____  ____  ____  ____  ",
    " |___  /  /  /  / / __ )/ __ \\/ __ \\/ __ \\/ __ \\ ",
    "    / /  /  /  / / __ )/ / / / / / / /_/ / / / / ",
    "   / /__/  /__/ / /_/ / /_/ / /_/ / _, _/ /_/ /  ",
    "  /____/__/__/ /_____/\\____/\\____/_/ |_/_____/    ",
]

CAT_FRAMES = [
    ["         z z z          ","        z                ","   /\\_____/\\             ","  ( o  .  o )~~~~~~~~~~  ","   >   ^   <  zzzboard   ","  (_____)________________"],
    ["          Z z z         ","         z               ","   /\\_____/\\             ","  ( -  .  - )~~~~~~~~~~  ","   >   ^   <  zzzboard   ","  (_____)________________"],
    ["           Z Z z        ","          z              ","   /\\_____/\\             ","  ( o  .  - )~~~~~~~~~~  ","   >   ^   <  zzzboard   ","  (_____)________________"],
    ["         z Z z          ","        z                ","   /\\_____/\\             ","  ( ~  .  ~ )~~~~~~~~~~  ","   >   ^   <  zzzboard   ","  (_____)________________"],
]

LOADING_STEPS = ["booting up...","checking for updates...","fetching weather...","calculating moon phase...","warming up monitors...","all systems go  zzz..."]

# ── Game State ─────────────────────────────────────────────────────────────────
GAME_W, GAME_H = 50, 22

game_state = {
    "mode":"none",
    "snake_body":[],"snake_dir":(1,0),"snake_food":(0,0),"snake_score":0,"snake_alive":True,
    "flappy_y":11.0,"flappy_vel":0.0,"flappy_pipes":[],"flappy_score":0,"flappy_alive":True,
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
        game_state["snake_alive"]=False; return
    game_state["snake_body"].insert(0,(nx,ny))
    if (nx,ny)==game_state["snake_food"]: game_state["snake_score"]+=1; snake_place_food()
    else: game_state["snake_body"].pop()

def flappy_init():
    game_state.update({"flappy_y":float(GAME_H//2),"flappy_vel":0.0,"flappy_pipes":[],"flappy_score":0,"flappy_alive":True})
    for i in range(2): flappy_add_pipe(GAME_W+i*20)

def flappy_add_pipe(x):
    game_state["flappy_pipes"].append({"x":x,"gap":random.randint(3,GAME_H-8),"scored":False})

def flappy_tick():
    if not game_state["flappy_alive"]: return
    game_state["flappy_vel"]+=0.35; game_state["flappy_y"]+=game_state["flappy_vel"]
    by,bx=int(game_state["flappy_y"]),6
    if by<=0 or by>=GAME_H-1: game_state["flappy_alive"]=False; return
    for p in game_state["flappy_pipes"]:
        p["x"]-=1
        if p["x"]==bx and (by<p["gap"] or by>p["gap"]+4): game_state["flappy_alive"]=False; return
        if p["x"]<bx and not p["scored"]: p["scored"]=True; game_state["flappy_score"]+=1
    game_state["flappy_pipes"]=[p for p in game_state["flappy_pipes"] if p["x"]>0]
    if not game_state["flappy_pipes"] or game_state["flappy_pipes"][-1]["x"]<GAME_W-15: flappy_add_pipe(GAME_W)

def render_snake():
    grid=[["." for _ in range(GAME_W)] for _ in range(GAME_H)]
    for x in range(GAME_W): grid[0][x]=grid[GAME_H-1][x]="-"
    for y in range(GAME_H): grid[y][0]=grid[y][GAME_W-1]="|"
    fx,fy=game_state["snake_food"]; grid[fy][fx]="o"
    for i,(bx,by) in enumerate(game_state["snake_body"]):
        if 0<=by<GAME_H and 0<=bx<GAME_W: grid[by][bx]="@" if i==0 else "#"
    t=Text()
    for row in grid: t.append("  "+"".join(row)+"\n",style=CLR["CLR_SNAKE"])
    if not game_state["snake_alive"]: t.append(f"\n  GAME OVER!  Score:{game_state['snake_score']}  Press S to restart\n",style=f"bold {CLR['CLR_SNAKE']}")
    else: t.append(f"\n  Score:{game_state['snake_score']}   WASD/arrows   Q to quit\n",style=f"dim {CLR['CLR_SNAKE']}")
    return t

def render_flappy():
    grid=[["." for _ in range(GAME_W)] for _ in range(GAME_H)]
    for x in range(GAME_W): grid[0][x]=grid[GAME_H-1][x]="-"
    for p in game_state["flappy_pipes"]:
        px,gap=p["x"],p["gap"]
        if 0<=px<GAME_W:
            for y in range(GAME_H):
                if y<gap or y>gap+4: grid[y][px]="|"
    by=int(game_state["flappy_y"])
    if 0<=by<GAME_H: grid[by][6]=">"
    t=Text()
    for row in grid: t.append("  "+"".join(row)+"\n",style=CLR["CLR_FLAPPY"])
    if not game_state["flappy_alive"]: t.append(f"\n  GAME OVER!  Score:{game_state['flappy_score']}  Press F to restart\n",style=f"bold {CLR['CLR_FLAPPY']}")
    else: t.append(f"\n  Score:{game_state['flappy_score']}   SPACE to flap   Q to quit\n",style=f"dim {CLR['CLR_FLAPPY']}")
    return t

# ── Settings ───────────────────────────────────────────────────────────────────

SETTINGS_ITEMS = [
    ("Theme",          "theme",          ["green","blue","pink","amber","red"]),
    ("Temperature",    "temp_unit",      ["F","C"]),
    ("Speed interval", "speed_interval", [30, 60, 120, 0]),
    ("Reset city",     "_reset_city",    None),
    ("Force update",   "_force_update",  None),
]

def settings_label(key, value):
    if key == "speed_interval":
        return "never" if value == 0 else f"{value} min"
    return str(value)

def settings_panel(cfg):
    t = Text()
    t.append("\n")
    t.append("  Arrow keys navigate   Left/Right or Enter to change\n\n", style=f"dim {CLR['CLR_DIM']}")
    pos = settings_cursor["pos"]

    for i, (label, key, options) in enumerate(SETTINGS_ITEMS):
        selected = i == pos
        prefix   = "  [>] " if selected else "  [ ] "
        style    = f"bold {CLR['CLR_CLOCK']}" if selected else f"dim {CLR['CLR_DIM']}"

        if options is None:
            t.append(prefix, style=style)
            t.append(f"{label}\n", style=style)
        else:
            val = cfg.get(key, options[0])
            t.append(prefix, style=style)
            t.append(f"{label:<20}", style=style)
            for opt in options:
                opt_str = settings_label(key, opt)
                if opt == val:
                    t.append(f" [{opt_str}] ", style=f"bold {CLR['CLR_CLOCK']} reverse")
                else:
                    t.append(f"  {opt_str}  ", style=f"dim {CLR['CLR_DIM']}")
            t.append("\n")

    if settings_msg["text"] and time.time() - settings_msg["time"] < 4:
        t.append(f"\n  {settings_msg['text']}\n", style=f"bold {settings_msg['color']}")

    t.append(f"\n  Theme preview:\n", style=f"dim {CLR['CLR_DIM']}")
    for name, colors in THEMES.items():
        marker = " [*]" if name == cfg.get("theme","pink") else "  o "
        t.append(f"  {marker} {name}\n", style=f"bold {colors['CLR_CLOCK']}")

    return Panel(t, title=f"[{CLR['CLR_CLOCK']}]> SETTINGS[/{CLR['CLR_CLOCK']}]", border_style=CLR["CLR_CLOCK"], box=box.ROUNDED)

def handle_settings_input(ch, cfg):
    import msvcrt
    pos   = settings_cursor["pos"]
    label, key, options = SETTINGS_ITEMS[pos]

    if ch in ("\x00", "\xe0"):
        arrow = msvcrt.getwch()
        if arrow == "H":
            settings_cursor["pos"] = (pos - 1) % len(SETTINGS_ITEMS)
        elif arrow == "P":
            settings_cursor["pos"] = (pos + 1) % len(SETTINGS_ITEMS)
        elif arrow in ("K","M") and options:
            val     = cfg.get(key, options[0])
            idx     = options.index(val) if val in options else 0
            delta   = -1 if arrow == "K" else 1
            new_val = options[(idx + delta) % len(options)]
            cfg[key] = new_val
            save_config(cfg)
            if key == "theme": apply_theme(new_val)
            settings_msg.update({"text": "Saved!", "color": CLR["CLR_CLOCK"], "time": time.time()})
        return

    if ch == "\r":
        if key == "_reset_city":
            cfg["city"] = ""
            save_config(cfg)
            settings_msg.update({"text": "Restarting in 5 seconds...", "color": "#FF4444", "time": time.time()})
            threading.Thread(target=city_reset_countdown, daemon=False).start()
        elif key == "_force_update":
            update_status.update({"checked": False, "updated": False, "error": None, "log": []})
            threading.Thread(target=check_for_update, daemon=True).start()
            settings_msg.update({"text": "Checking for updates...", "color": CLR["CLR_SPEED"], "time": time.time()})
        elif options:
            val     = cfg.get(key, options[0])
            idx     = options.index(val) if val in options else 0
            new_val = options[(idx + 1) % len(options)]
            cfg[key] = new_val
            save_config(cfg)
            if key == "theme": apply_theme(new_val)
            settings_msg.update({"text": "Saved!", "color": CLR["CLR_CLOCK"], "time": time.time()})

# ── Input handler ──────────────────────────────────────────────────────────────

def input_loop():
    try:
        import msvcrt
        while True:
            if msvcrt.kbhit():
                ch   = msvcrt.getwch()
                key  = ch.lower()
                mode = game_state["mode"]

                if key in ("1","2","3","4","5","6"):
                    current_tab["tab"] = int(key)
                    if key != "5": game_state["mode"] = "none"

                elif current_tab["tab"] == 6:
                    handle_settings_input(ch, _cfg_ref)

                elif key == "s":
                    if mode != "snake": current_tab["tab"]=5; game_state["mode"]="snake"; snake_init()
                    elif not game_state["snake_alive"]: snake_init()
                elif key == "f":
                    if mode != "flappy": current_tab["tab"]=5; game_state["mode"]="flappy"; flappy_init()
                    elif not game_state["flappy_alive"]: flappy_init()
                elif key == "q":
                    game_state["mode"] = "none"

                elif mode == "snake":
                    if key=="a" and game_state["snake_dir"]!=(1,0): game_state["snake_dir"]=(-1,0)
                    elif key=="d" and game_state["snake_dir"]!=(-1,0): game_state["snake_dir"]=(1,0)
                    elif key=="w" and game_state["snake_dir"]!=(0,1): game_state["snake_dir"]=(0,-1)
                    elif ch in ("\x00","\xe0"):
                        a=msvcrt.getwch()
                        if a=="H" and game_state["snake_dir"]!=(0,1): game_state["snake_dir"]=(0,-1)
                        elif a=="P" and game_state["snake_dir"]!=(0,-1): game_state["snake_dir"]=(0,1)
                        elif a=="K" and game_state["snake_dir"]!=(1,0): game_state["snake_dir"]=(-1,0)
                        elif a=="M" and game_state["snake_dir"]!=(-1,0): game_state["snake_dir"]=(1,0)

                elif mode == "flappy":
                    if key in (" ","w"): game_state["flappy_vel"]=-2.8

            time.sleep(0.03)
    except Exception: pass

def game_loop():
    ls=lf=time.time()
    while True:
        now=time.time()
        if game_state["mode"]=="snake" and game_state["snake_alive"] and now-ls>0.13: snake_tick(); ls=now
        if game_state["mode"]=="flappy" and game_state["flappy_alive"] and now-lf>0.07: flappy_tick(); lf=now
        time.sleep(0.01)

# ── Helpers ────────────────────────────────────────────────────────────────────

def color_for(pct, base):
    if pct>=85: return "#FF4444"
    if pct>=60: return "#FFD93D"
    return base

def uptime_str():
    delta=datetime.now()-START_TIME; h,rem=divmod(int(delta.total_seconds()),3600); m,s=divmod(rem,60)
    return f"{h:02d}h {m:02d}m {s:02d}s"

def file_hash(path):
    try:
        with open(path,"rb") as f: return hashlib.md5(f.read()).hexdigest()
    except Exception: return None

def smooth_bar(pct, width, color):
    t=Text(); fill=int(pct/100*width)
    t.append("[",style=f"dim {CLR['CLR_DIM']}"); t.append("#"*fill,style=f"bold {color}"); t.append("-"*(width-fill),style=f"dim {CLR['CLR_DIM']}"); t.append("]",style=f"dim {CLR['CLR_DIM']}")
    return t

def spark_line(history, width, color):
    t=Text(); bars=" ........||||||||"
    for v in list(history)[-width:]: t.append(bars[min(16,int(v/100*16))],style=color)
    return t

# ── Auto-updater ───────────────────────────────────────────────────────────────

def check_for_update():
    update_status["log"].append("connecting to github...")
    try:
        r=requests.get(GITHUB_RAW_URL,verify=False,timeout=8); r.raise_for_status()
        remote_code=r.text; update_status["log"].append("comparing versions...")
        script_path=os.path.join(THIS_DIR,"zzboard_public.py") if IS_EXE else THIS_FILE
        if file_hash(script_path)!=hashlib.md5(remote_code.encode()).hexdigest():
            update_status["log"].append("update found! downloading...")
            time.sleep(0.4)
            with open(script_path,"w",encoding="utf-8") as f: f.write(remote_code)
            update_status["log"].append("update applied!")
            update_status["updated"]=True
        else:
            update_status["log"].append("already up to date.")
    except Exception:
        update_status["log"].append("update check failed.")
    update_status["checked"]=True

def cat_screen(extra_line="", progress=None):
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
        with Live(cat_screen(f"> {log}"),console=console,screen=True,refresh_per_second=10): time.sleep(0.15)
    if update_status["updated"]:
        with Live(cat_screen("> update applied! loading changelog..."),console=console,screen=True,refresh_per_second=10): time.sleep(2.0)
        console.clear()
        show_changelog()
        do_restart()
    else:
        msg="> up to date!" if not update_status["error"] else "> continuing offline..."
        with Live(cat_screen(msg),console=console,screen=True,refresh_per_second=10): time.sleep(1.5)
def show_splash():
    for tick in range(36):
        step=LOADING_STEPS[min(tick//max(1,36//len(LOADING_STEPS)),len(LOADING_STEPS)-1)]
        with Live(cat_screen(f"> {step}",tick),console=console,screen=True,refresh_per_second=10): time.sleep(0.1)
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

def clock_panel():
    now=datetime.now(); sep=":" if int(time.time())%2 else " "
    t=Text(justify="center"); t.append("\n")
    t.append(f"{now.strftime('%H')}{sep}{now.strftime('%M')}{sep}{now.strftime('%S')}",style=f"bold {CLR['CLR_CLOCK']}")
    t.append("\n"); t.append(now.strftime("%A, %d %B %Y").upper(),style=f"dim {CLR['CLR_WEATHER']}")
    t.append("\n"); t.append(f"uptime  {uptime_str()}",style=f"italic dim {CLR['CLR_DIM']}"); t.append("\n")
    return Panel(t,title=f"[{CLR['CLR_CLOCK']}]  -- Z Z B O A R D  PUBLIC v1.2 -- made by @wtfplutolol --  [/{CLR['CLR_CLOCK']}]",border_style=CLR["CLR_CLOCK"],box=box.DOUBLE,padding=(0,2))

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
    layout=Layout()
    layout.split_column(Layout(name="clock",size=7),Layout(name="stats",ratio=1))
    layout["stats"].split_row(Layout(name="cpu",ratio=1),Layout(name="mem",ratio=1))
    layout["clock"].update(clock_panel()); layout["cpu"].update(cpu_panel()); layout["mem"].update(mem_panel())
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
    if mode=="snake": return Panel(render_snake(),title=f"[{CLR['CLR_SNAKE']}]> SNAKE  score:{game_state['snake_score']}  Q=quit[/{CLR['CLR_SNAKE']}]",border_style=CLR["CLR_SNAKE"],box=box.ROUNDED)
    elif mode=="flappy": return Panel(render_flappy(),title=f"[{CLR['CLR_FLAPPY']}]> FLAPPY BIRD  score:{game_state['flappy_score']}  Q=quit[/{CLR['CLR_FLAPPY']}]",border_style=CLR["CLR_FLAPPY"],box=box.ROUNDED)
    else:
        t=Text(); t.append("\n\n")
        t.append("  Press S to play Snake\n\n",style=f"bold {CLR['CLR_SNAKE']}")
        t.append("     WASD or arrow keys to move\n     Eat [o] to grow\n     Avoid walls and yourself\n\n",style=f"dim {CLR['CLR_SNAKE']}")
        t.append("  Press F to play Flappy Bird\n\n",style=f"bold {CLR['CLR_FLAPPY']}")
        t.append("     SPACE to flap\n     Avoid the pipes [|]\n     How far can you go?\n\n",style=f"dim {CLR['CLR_FLAPPY']}")
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
    parser=argparse.ArgumentParser(description="ZZBoard Public v1.2")
    parser.add_argument("--no-splash",action="store_true")
    args=parser.parse_args()

    # Apply pink as default theme for splash
    apply_theme("pink")

    cfg=load_config()
    if not cfg.get("city"): cfg=first_launch_setup()

    # Apply saved theme
    apply_theme(cfg.get("theme","pink"))
    _cfg_ref.update(cfg)

    threading.Thread(target=lambda:fetch_weather(cfg["city"]),daemon=True).start()
    threading.Thread(target=fetch_speed,daemon=True).start()
    threading.Thread(target=input_loop,daemon=True).start()
    threading.Thread(target=game_loop,daemon=True).start()
    psutil.cpu_percent(interval=0.1,percpu=True)
    start_watcher()

    if not args.no_splash:
        show_update_screen()

        # Show changelog if updated
        if update_status["updated"]:
            show_changelog()
            do_restart()

        show_splash()

    # Handle force update applied while running
    try:
        with Live(build_layout(_cfg_ref),console=console,refresh_per_second=4,screen=True) as live:
            while True:
                if reload_flag.is_set(): do_restart()
                if update_status.get("updated") and update_status.get("checked"):
                    # Force update was triggered from settings
                    update_status["updated"] = False
                    show_changelog()
                    do_restart()
                time.sleep(0.25)
                live.update(build_layout(_cfg_ref))
    except KeyboardInterrupt:
        pass

    console.print(f"\n[bold {CLR['CLR_CLOCK']}]  ZZBOARD PUBLIC[/bold {CLR['CLR_CLOCK']}] [dim {CLR['CLR_DIM']}]terminated. sweet dreams. -- made by @wtfplutolol with <3[/dim {CLR['CLR_DIM']}]\n")

if __name__=="__main__":
    main()
