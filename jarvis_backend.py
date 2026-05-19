"""
╔══════════════════════════════════════════════════════════════╗
║           JARVIS — ULTIMATE PC VOICE CONTROLLER v2.0         ║
║              FastAPI Backend + React Dashboard               ║
╚══════════════════════════════════════════════════════════════╝


RUN:
    uvicorn jarvis_backend:app --reload --port 8000
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from dotenv import load_dotenv
load_dotenv()
import speech_recognition as sr
import pyttsx3
from google import genai
from google.genai import types

import json, os, sys, time, subprocess, webbrowser
import threading, datetime, random, platform, ctypes
import pyautogui, psutil, requests, pyperclip

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

GEMINI_API_KEY  = os.getenv("GEMINI_API_KEY")  
WEATHER_API_KEY = ""   
YOUR_CITY       = ""                     

# ✅ FIXED: naya google-genai client
gemini_client = genai.Client(api_key=GEMINI_API_KEY)
GEMINI_MODEL  = "gemini-2.0-flash"   # free + fast

# Speech recognizer
recognizer = sr.Recognizer()
recognizer.energy_threshold        = 100
recognizer.dynamic_energy_threshold = False
recognizer.pause_threshold          = 0.3
recognizer.non_speaking_duration    = 0.1
recognizer.phrase_threshold         = 0.1

pyautogui.FAILSAFE = True
pyautogui.PAUSE    = 0.05

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  📁  APP PATHS & WEBSITES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

APP_PATHS = {
    "chrome":             r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "firefox":            r"C:\Program Files\Mozilla Firefox\firefox.exe",
    "edge":               r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "notepad":            "notepad.exe",
    "calculator":         "calc.exe",
    "paint":              "mspaint.exe",
    "explorer":           "explorer.exe",
    "file explorer":      "explorer.exe",
    "word":               r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
    "excel":              r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
    "powerpoint":         r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE",
    "outlook":            r"C:\Program Files\Microsoft Office\root\Office16\OUTLOOK.EXE",
    "vscode":             r"C:\Users\%USERNAME%\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "vs code":            r"C:\Users\%USERNAME%\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "visual studio code": r"C:\Users\%USERNAME%\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "spotify":            r"C:\Users\%USERNAME%\AppData\Roaming\Spotify\Spotify.exe",
    "discord":            r"C:\Users\%USERNAME%\AppData\Local\Discord\Update.exe",
    "vlc":                r"C:\Program Files\VideoLAN\VLC\vlc.exe",
    "steam":              r"C:\Program Files (x86)\Steam\Steam.exe",
    "zoom":               r"C:\Users\%USERNAME%\AppData\Roaming\Zoom\bin\Zoom.exe",
    "telegram":           r"C:\Users\%USERNAME%\AppData\Roaming\Telegram Desktop\Telegram.exe",
    "cmd":                "cmd.exe",
    "command prompt":     "cmd.exe",
    "powershell":         "powershell.exe",
    "task manager":       "taskmgr.exe",
    "settings":           "ms-settings:",
    "control panel":      "control.exe",
    "snipping tool":      "snippingtool.exe",
    "obs":                r"C:\Program Files\obs-studio\bin\64bit\obs64.exe",
}

WEBSITES = {
    "youtube":       "https://youtube.com",
    "google":        "https://google.com",
    "github":        "https://github.com",
    "gmail":         "https://mail.google.com",
    "google drive":  "https://drive.google.com",
    "google docs":   "https://docs.google.com",
    "google sheets": "https://sheets.google.com",
    "google maps":   "https://maps.google.com",
    "whatsapp":      "https://web.whatsapp.com",
    "chatgpt":       "https://chat.openai.com",
    "claude":        "https://claude.ai",
    "gemini":        "https://gemini.google.com",
    "netflix":       "https://netflix.com",
    "hotstar":       "https://hotstar.com",
    "twitter":       "https://twitter.com",
    "instagram":     "https://instagram.com",
    "facebook":      "https://facebook.com",
    "linkedin":      "https://linkedin.com",
    "reddit":        "https://reddit.com",
    "stackoverflow": "https://stackoverflow.com",
    "wikipedia":     "https://wikipedia.org",
    "amazon":        "https://amazon.in",
    "flipkart":      "https://flipkart.com",
    "spotify":       "https://open.spotify.com",
    "leetcode":      "https://leetcode.com",
    "canva":         "https://canva.com",
    "notion":        "https://notion.so",
}

JOKES = [
    "Why do programmers prefer dark mode? Because light attracts bugs, sir.",
    "A SQL query walks into a bar and asks two tables — can I join you?",
    "Why did the computer go to the doctor? Because it had a virus, sir.",
    "Why do Java developers wear glasses? Because they don't C sharp.",
    "There are 10 types of people — those who understand binary, and those who don't.",
    "How do you comfort a JavaScript bug? You console it, sir.",
]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  🗣️  TTS — SPEAK
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def speak_text(text: str):
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[0].id)
        engine.setProperty('rate', 175)
        engine.setProperty('volume', 1.0)
        engine.say(text)
        engine.runAndWait()
        engine.stop()
    except Exception as e:
        print(f"[TTS Error] {e}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  🎤  LISTEN HELPERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def send(ws: WebSocket, status: str, text: str, extra: dict = {}):
    payload = {"status": status, "text": text, **extra}
    await ws.send_text(json.dumps(payload))

async def quick_listen(timeout=6, phrase_limit=10) -> str:
    def _listen():
        with sr.Microphone() as source:
            try:
                audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_limit)
                return recognizer.recognize_google(audio).lower().strip()
            except:
                return ""
    return await asyncio.to_thread(_listen)

async def ask_and_listen(ws: WebSocket, question: str) -> str:
    await send(ws, "speaking", question)
    await asyncio.to_thread(speak_text, question)
    await send(ws, "listening", "Listening...")
    return await quick_listen()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  🧠  GEMINI AI  ✅ FIXED — naya google-genai SDK
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Conversation history Gemini ke liye
gemini_history = []

async def ask_gemini(query: str) -> str:
    global gemini_history

    system_prompt = (
        "You are Jarvis, an elite AI assistant like Iron Man's Jarvis. "
        "Be sharp, concise, and professional. Address user as 'sir'. "
        "Keep answers under 2-3 sentences. Never refuse. Be helpful always."
    )

    try:
        
        def _call():
            response = gemini_client.models.generate_content(
                model=GEMINI_MODEL,
                contents=query,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    max_output_tokens=300,
                    temperature=0.7,
                )
            )
            return response.text.strip()

        return await asyncio.to_thread(_call)

    except Exception as e:
        print(f"[Gemini Error] {e}")
        return "I'm having trouble reaching my AI brain, sir. Please check your Gemini API key."

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ⚡  COMMAND PROCESSOR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def process_command(cmd: str, ws: WebSocket) -> str:
    c = cmd.strip().lower()

    # ── EXIT ────────────────────────────────────────────────────
    if any(w in c for w in ["goodbye", "bye jarvis", "stop jarvis", "turn off jarvis", "go offline"]):
        await send(ws, "speaking", "Goodbye, sir. Jarvis going offline.")
        await asyncio.to_thread(speak_text, "Goodbye, sir. Jarvis going offline.")
        os._exit(0)

    # ── JOKES & PERSONALITY ──────────────────────────────────────
    if "joke" in c:
        return random.choice(JOKES)
    if any(w in c for w in ["flip a coin", "coin flip", "heads or tails"]):
        return f"It's {random.choice(['Heads', 'Tails'])}, sir."
    if "roll a dice" in c or "roll dice" in c:
        return f"You rolled a {random.randint(1,6)}, sir."
    if any(w in c for w in ["who are you", "introduce yourself", "what are you"]):
        return "I am Jarvis, your personal AI-powered PC assistant, always at your service, sir."
    if "how are you" in c:
        return "All systems running at peak efficiency, sir. Thank you for asking."
    if "thank you" in c or "thanks" in c:
        return random.choice(["Always at your service, sir.", "My pleasure, sir.", "Anytime, sir."])
    if "good morning" in c: return "Good morning, sir. Ready to dominate the day?"
    if "good night" in c:   return "Good night, sir. Rest well."
    if "hello" in c or "hi jarvis" in c: return "Hello, sir. How can I help you today?"

    # ── TIME & DATE ──────────────────────────────────────────────
    if "what time" in c or c in ["time", "the time"]:
        return f"It's {datetime.datetime.now().strftime('%I:%M %p')}, sir."
    if any(w in c for w in ["what day", "what date", "today's date", "what is today"]):
        return f"Today is {datetime.datetime.now().strftime('%A, %B %d, %Y')}, sir."

    # ── REMINDER ─────────────────────────────────────────────────
    if "remind me" in c or "set reminder" in c:
        msg = await ask_and_listen(ws, "What shall I remind you about, sir?")
        mins_str = await ask_and_listen(ws, "In how many minutes, sir?")
        try:
            mins = int("".join(ch for ch in mins_str if ch.isdigit()))
            def _remind():
                time.sleep(mins * 60)
                speak_text(f"Reminder, sir: {msg}")
            threading.Thread(target=_remind, daemon=True).start()
            return f"Reminder set for {mins} minutes, sir."
        except:
            return "Couldn't parse the time, sir."

    # ── TIMER ────────────────────────────────────────────────────
    if "set timer" in c or "timer for" in c or "start timer" in c:
        nums = [int(w) for w in c.split() if w.isdigit()]
        if not nums:
            m = await ask_and_listen(ws, "How many minutes, sir?")
            try: nums = [int("".join(ch for ch in m if ch.isdigit()))]
            except: return "Couldn't understand the time, sir."
        mins = nums[0]
        def _timer():
            time.sleep(mins * 60)
            speak_text(f"Sir, your {mins}-minute timer is complete!")
        threading.Thread(target=_timer, daemon=True).start()
        return f"Timer set for {mins} minutes, sir."

    # ── WEATHER ──────────────────────────────────────────────────
    if any(w in c for w in ["weather", "temperature", "forecast"]):
        city = YOUR_CITY
        if " in " in c: city = c.split(" in ")[-1].strip()
        try:
            url = (f"http://api.openweathermap.org/data/2.5/weather"
                   f"?q={city}&appid={WEATHER_API_KEY}&units=metric")
            d = requests.get(url, timeout=5).json()
            if d.get("cod") == 200:
                return (f"In {city}: {d['main']['temp']}°C, feels like {d['main']['feels_like']}°C, "
                        f"{d['weather'][0]['description']}, humidity {d['main']['humidity']}%, sir.")
            return f"No weather data for {city}, sir."
        except:
            return "Weather service unavailable, sir. Check your API key."

    # ── SYSTEM INFO ──────────────────────────────────────────────
    if "battery" in c:
        b = psutil.sensors_battery()
        if b:
            status = "plugged in" if b.power_plugged else "on battery"
            return f"Battery is at {int(b.percent)}%, {status}, sir."
        return "No battery found — desktop PC, sir."

    if "cpu" in c or "processor" in c:
        return f"CPU is at {psutil.cpu_percent(interval=1)}% across {psutil.cpu_count()} cores, sir."

    if "ram" in c or "memory" in c:
        r = psutil.virtual_memory()
        return f"Using {round(r.used/(1024**3),1)} GB of {round(r.total/(1024**3),1)} GB RAM ({r.percent}%), sir."

    if any(w in c for w in ["disk space", "storage", "free space"]):
        u = psutil.disk_usage("/")
        return f"You have {round(u.free/(1024**3),1)} GB free out of {round(u.total/(1024**3),1)} GB. Disk is {u.percent}% full, sir."

    if any(w in c for w in ["ip address", "my ip", "public ip"]):
        try:
            ip = requests.get("https://api.ipify.org", timeout=5).text
            return f"Your public IP is {ip}, sir."
        except:
            return "Couldn't fetch IP address, sir."

    if any(w in c for w in ["internet", "wifi", "network connection"]):
        try:
            requests.get("https://google.com", timeout=3)
            return "Internet connection is active, sir."
        except:
            return "No internet detected, sir."

    # ── SCREENSHOT ───────────────────────────────────────────────
    if any(w in c for w in ["screenshot", "capture screen", "take screenshot"]):
        if any(w in c for w in ["snip", "select area", "region"]):
            pyautogui.hotkey("win", "shift", "s")
            return "Snipping tool open. Select your area, sir."
        fname = f"screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        path = os.path.join(os.path.expanduser("~"), "Desktop", fname)
        pyautogui.screenshot().save(path)
        return f"Screenshot saved to Desktop as {fname}, sir."

    # ── SHUTDOWN / RESTART / SLEEP / LOCK ────────────────────────
    if any(w in c for w in ["shutdown", "shut down", "turn off pc"]):
        os.system("shutdown /s /t 10")
        return "Shutting down in 10 seconds, sir."
    if any(w in c for w in ["restart", "reboot"]):
        os.system("shutdown /r /t 5")
        return "Restarting now, sir."
    if any(w in c for w in ["sleep", "hibernate"]):
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        return "Sleeping now, sir."
    if "lock" in c:
        ctypes.windll.user32.LockWorkStation()
        return "Locking, sir."
    if any(w in c for w in ["sign out", "log out", "logoff"]):
        os.system("shutdown /l")
        return "Signing out, sir."

    # ── VOLUME & MEDIA ───────────────────────────────────────────
    if "mute" in c or "unmute" in c:
        pyautogui.press("volumemute"); return "Done, sir."
    if any(w in c for w in ["volume up", "louder", "increase volume", "turn up"]):
        [pyautogui.press("volumeup") for _ in range(8)]; return "Volume up, sir."
    if any(w in c for w in ["volume down", "quieter", "lower volume", "turn down"]):
        [pyautogui.press("volumedown") for _ in range(8)]; return "Volume down, sir."
    if any(w in c for w in ["next song", "next track", "skip song"]):
        pyautogui.press("nexttrack"); return "Next track, sir."
    if any(w in c for w in ["previous song", "previous track"]):
        pyautogui.press("prevtrack"); return "Previous track, sir."
    if any(w in c for w in ["pause music", "play music", "pause", "resume"]):
        pyautogui.press("playpause"); return "Done, sir."

    # ── WINDOW CONTROL ───────────────────────────────────────────
    if "minimize all" in c or "show desktop" in c:
        pyautogui.hotkey("win","d"); return "Showing desktop, sir."
    if "minimize" in c:
        pyautogui.hotkey("win","down"); return "Minimized, sir."
    if "maximize" in c:
        pyautogui.hotkey("win","up"); return "Maximized, sir."
    if "close tab" in c:
        pyautogui.hotkey("ctrl","w"); return "Tab closed, sir."
    if "new tab" in c:
        pyautogui.hotkey("ctrl","t"); return "New tab opened, sir."
    if "switch window" in c or "alt tab" in c:
        pyautogui.hotkey("alt","tab"); return "Switching windows, sir."
    if "snap left" in c:
        pyautogui.hotkey("win","left"); return "Snapped left, sir."
    if "snap right" in c:
        pyautogui.hotkey("win","right"); return "Snapped right, sir."
    if "full screen" in c or "fullscreen" in c:
        pyautogui.press("f11"); return "Full screen toggled, sir."
    if "refresh" in c or "reload" in c:
        pyautogui.press("f5"); return "Refreshed, sir."
    if any(w in c for w in ["close window","close this","close app","close current"]):
        pyautogui.hotkey("alt","F4"); return "Window closed, sir."

    # ── KEYBOARD SHORTCUTS ───────────────────────────────────────
    shortcuts = {
        "select all": ("ctrl","a"), "undo": ("ctrl","z"), "redo": ("ctrl","y"),
        "save": ("ctrl","s"), "find": ("ctrl","f"), "copy": ("ctrl","c"),
        "paste": ("ctrl","v"), "cut": ("ctrl","x"), "print": ("ctrl","p"),
        "zoom in": ("ctrl","="), "zoom out": ("ctrl","-"),
        "task view": ("win","tab"), "file manager": ("win","e"),
        "search bar": ("win","s"), "snipping tool": ("win","shift","s"),
        "emoji picker": ("win","."), "run dialog": ("win","r"),
    }
    for action, keys in shortcuts.items():
        if action in c:
            pyautogui.hotkey(*keys)
            return f"{action.title()}, sir."

    # ── TYPE TEXT ────────────────────────────────────────────────
    if any(w in c for w in ["type", "write", "input"]):
        text = ""
        for trigger in ["type", "write", "input"]:
            if trigger in c:
                text = c.split(trigger, 1)[-1].strip()
                break
        if not text:
            text = await ask_and_listen(ws, "What should I type, sir?")
        if text:
            pyperclip.copy(text)
            await asyncio.sleep(0.3)
            pyautogui.hotkey("ctrl","v")
            return "Done typing, sir."

    # ── CLIPBOARD ────────────────────────────────────────────────
    if "clear clipboard" in c:
        pyperclip.copy(""); return "Clipboard cleared, sir."
    if "what" in c and "clipboard" in c:
        content = pyperclip.paste()
        return f"Clipboard: {content[:100] if content else 'empty'}, sir."

    # ── FILES & FOLDERS ──────────────────────────────────────────
    home = os.path.expanduser("~")
    folders = {
        "desktop":   os.path.join(home,"Desktop"),
        "documents": os.path.join(home,"Documents"),
        "downloads": os.path.join(home,"Downloads"),
        "pictures":  os.path.join(home,"Pictures"),
        "music":     os.path.join(home,"Music"),
        "videos":    os.path.join(home,"Videos"),
    }
    for name, path in folders.items():
        if f"open {name}" in c or f"show {name}" in c:
            os.startfile(path); return f"Opening {name}, sir."

    if any(w in c for w in ["create folder","new folder","make folder"]):
        name = (c.replace("create folder","").replace("new folder","")
                 .replace("make folder","").replace("called","").replace("named","").strip())
        name = name if name else f"NewFolder_{int(time.time())}"
        os.makedirs(os.path.join(home,"Desktop",name), exist_ok=True)
        return f"Folder '{name}' created on Desktop, sir."

    # ── CLOSE APP ────────────────────────────────────────────────
    if "close" in c:
        kill_map = {
            "chrome":"chrome.exe", "firefox":"firefox.exe",
            "notepad":"notepad.exe", "calculator":"Calculator.exe",
            "spotify":"Spotify.exe", "discord":"Discord.exe",
            "vlc":"vlc.exe", "vscode":"Code.exe",
            "vs code":"Code.exe", "steam":"steam.exe",
            "zoom":"Zoom.exe", "edge":"msedge.exe",
            "word":"WINWORD.EXE", "excel":"EXCEL.EXE",
            "powerpoint":"POWERPNT.EXE", "telegram":"Telegram.exe",
        }
        for name, proc in kill_map.items():
            if name in c:
                os.system(f"taskkill /f /im {proc} >nul 2>&1")
                return f"Closed {name}, sir."

    # ── YOUTUBE SEARCH ────────────────────────────────────────────
    if "youtube" in c and any(w in c for w in ["search","play","find","watch"]):
        q = (c.replace("youtube","").replace("search","").replace("play","")
              .replace("find","").replace("watch","").replace("on","").strip())
        if q:
            webbrowser.open(f"https://www.youtube.com/results?search_query={q.replace(' ','+')}")
            return f"Searching '{q}' on YouTube, sir."

    # ── GOOGLE MAPS ───────────────────────────────────────────────
    if any(w in c for w in ["directions to","navigate to","map of","where is"]):
        loc = (c.replace("directions to","").replace("navigate to","")
                .replace("map of","").replace("where is","").strip())
        webbrowser.open(f"https://maps.google.com/?q={loc.replace(' ','+')}")
        return f"Opening map for {loc}, sir."

    # ── GOOGLE SEARCH ─────────────────────────────────────────────
    if any(w in c for w in ["search for","search","google","look up"]):
        q = (c.replace("search for","").replace("search","")
              .replace("google","").replace("look up","").strip())
        if q and len(q) > 2:
            webbrowser.open(f"https://google.com/search?q={q.replace(' ','+')}")
            return f"Searching '{q}' on Google, sir."

    # ── OPEN APP ──────────────────────────────────────────────────
    if any(w in c for w in ["open","launch","start","run"]):
        for name, path in APP_PATHS.items():
            if name in c:
                try:
                    exp = os.path.expandvars(path)
                    if path.startswith("ms-") or path.endswith(":"):
                        os.startfile(path)
                    elif path.endswith(".msc"):
                        subprocess.Popen(["mmc", exp])
                    else:
                        subprocess.Popen(exp)
                    return f"Opening {name}, sir."
                except:
                    return f"Couldn't open {name}, sir. Please check the path."
        for site, url in WEBSITES.items():
            if site in c:
                webbrowser.open(url)
                return f"Opening {site}, sir."

    # ── MATH ──────────────────────────────────────────────────────
    if any(w in c for w in ["calculate","compute","how much is","what is"]):
        expr = (c.replace("calculate","").replace("compute","")
                 .replace("how much is","").replace("what is","")
                 .replace("plus","+").replace("minus","-")
                 .replace("times","*").replace("multiplied by","*")
                 .replace("divided by","/").replace("power of","**").strip())
        safe = "".join(ch for ch in expr if ch in "0123456789+-*/(). ")
        try:
            result = round(eval(safe), 8)
            return f"The answer is {result}, sir."
        except:
            pass

    # ── SPEED TEST ────────────────────────────────────────────────
    if "speed test" in c or "internet speed" in c:
        webbrowser.open("https://fast.com"); return "Speed test opened, sir."

    # ── EMPTY RECYCLE BIN ─────────────────────────────────────────
    if "empty recycle bin" in c:
        os.system("rd /s /q %systemdrive%\\$Recycle.bin >nul 2>&1")
        return "Recycle bin cleared, sir."

    # ── GEMINI AI — handles everything else ✅ ────────────────────
    return await ask_gemini(c)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  🌀  MAIN JARVIS LOOP
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def jarvis_loop(ws: WebSocket):
    await send(ws, "speaking", "Jarvis online. All systems at full power, sir.")
    await asyncio.to_thread(speak_text, "Jarvis online. All systems at full power, sir.")

    while True:
        try:
            await send(ws, "idle", "Sleeping... Say 'Hey Jarvis'")

            def _wait_wake():
                with sr.Microphone() as source:
                    while True:
                        try:
                            audio = recognizer.listen(source, timeout=1, phrase_time_limit=3)
                            text = recognizer.recognize_google(audio).lower().strip()
                            if "jarvis" in text:
                                return text
                        except (sr.WaitTimeoutError, sr.UnknownValueError):
                            continue
                        except Exception:
                            time.sleep(0.2)

            wake_text = await asyncio.to_thread(_wait_wake)
            cmd = (wake_text.replace("hey jarvis","").replace("ok jarvis","")
                            .replace("hi jarvis","").replace("jarvis","").strip())

            await send(ws, "active", "Yes, sir?")
            await asyncio.to_thread(speak_text, "Yes, sir?")

            if not cmd:
                await send(ws, "listening", "Listening for command...")
                cmd = await quick_listen(timeout=7, phrase_limit=12)

            if not cmd:
                await send(ws, "speaking", "I didn't catch that, sir. Call me again.")
                await asyncio.to_thread(speak_text, "I didn't catch that, sir.")
                continue

            await send(ws, "thinking", f"Processing: {cmd}")
            reply = await process_command(cmd, ws)

            if reply:
                print(f"[Jarvis] {reply}")
                await send(ws, "speaking", reply)
                await asyncio.to_thread(speak_text, reply)

            await asyncio.sleep(0.5)

        except WebSocketDisconnect:
            print("[WebSocket] Dashboard disconnected.")
            break
        except Exception as e:
            print(f"[Loop Error] {e}")
            await asyncio.sleep(1)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  🌐  ENDPOINTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    print("[Jarvis] React Dashboard Connected!")
    await jarvis_loop(ws)

@app.get("/")
def root():
    return {"status": "Jarvis Backend Running ✅", "ws": "ws://localhost:8000/ws"}