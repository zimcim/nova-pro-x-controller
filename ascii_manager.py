import os
import glob
from config import ASCII_DIR, CHAR_LIMIT

class ASCIIArtManager:
    def __init__(self):
        self.ascii_dir = ASCII_DIR
        self.create_default_arts()
    
    def create_default_arts(self):
        if not os.path.exists(self.ascii_dir):
            os.makedirs(self.ascii_dir)
        
        arts = {
                "nova_logo.txt": [
                    "╔═══════════╗",
                    "║ NOVA PRO  ║",
                    "╚═══════════╝"
                ],
                "heart_full.txt": [
                    ". ♥     ♥  ",
                    " ♥  ♥ ♥  ♥ ",
                    "  ♥   ♥    "
                ],
                "star.txt": [
                    ".     ★     ",
                    "   ★   ★   ",
                    " ★       ★ "
                ],
                "anime_cat.txt": [
                    ". ∧＿∧    ",
                    " ( ･ω･)    ",
                    " (つ  つ    "
                ],
                "anime_girl.txt": [
                    ". ✿◕ ‿ ◕✿ ",
                    "  ╱|    |╲ ",
                    " ╱ |    | ╲"
                ],
                "kawaii.txt": [
                    ". (◡ ‿ ◡)  ",
                    "  <|   |>  ",
                    "  d|   |b  "
                ],
                "anime_eyes.txt": [
                    ".◉      ◉  ",
                    "    >      ",
                    "   ‿‿‿     "
                ],
                "uwu.txt": [
                    "           ",
                    "   U w U   ",
                    "           "
                ],
                "anime_bear.txt": [
                    ".ʕ•ᴥ•ʔ    ",
                    " (¨)__(¨)  ",
                    "           "
                ],
                "anime_bunny.txt": [
                    ".(\\_/)     ",
                    " ( •.•)    ",
                    " (¨)_(¨)   "
                ],
                "anime_star.txt": [
                    " ✧･ﾟ: *✧  ",
                    "  ･ﾟ:* ✧  ",
                    " ✧･ﾟ: *✧  "
                ],
                "snowflake.txt": [
                    "  ❄   ❄    ",
                    "    ❅      ",
                    "  ❄   ❄    "
                ],
                "anime_heart.txt": [
                    "  ♡ ♡ ♡    ",
                    " ♡ ≧◡≦ ♡  ",
                    "  ♡ ♡ ♡    "
                ],
                "pikachu.txt": [
                    ".◓ ◓       ",
                    "(  ◡  )    ",
                    " ￣￣￣     "
                ],
                "anime_star.txt": [
                    " ✧･ﾟ: *✧  ",
                    "  ･ﾟ:* ✧  ",
                    " ✧･ﾟ: *✧  "
                ],
                "snowflake.txt": [
                    "  ❄   ❄   ",
                    "    ❅      ",
                    "  ❄   ❄   "
                ],
                "anime_heart.txt": [
                    "   ♡ ♡ ♡   ",
                    " ♡ ≧◡≦ ♡ ",
                    "  ♡ ♡ ♡   "
                ],
                "neko.txt": [
                    "   =^.^=   ",
                    "  (¨)_(¨)  ",
                    "   Neko    "
                ],
                "kirby.txt": [
                    "  ⊂(◉‿◉)つ ",
                    "           ",
                    "           "
                ],
                "emoji_party.txt": [
                    "🎉 🎊 🎈 🎁 🎆",
                    " 🥳 🎂 🍰 🎵 ",
                    "🎶 🎪 🎨 🎯 🎮"
                ],
                "emoji_food.txt": [
                    "🍕 🍔 🍟 🌭 🥪",
                    " 🍣 🍜 🍝 🥘 ",
                    "🍩 🍪 🧁 🍫 🍬"
                ],
                "emoji_gaming.txt": [
                    "🎮 🕹️ 👾 🎯 🎲",
                    " 🏆 🥇 🏅 ⚔️ ",
                    "🛡️ 💎 💰 🗝️ 🎪"
                ]
            }
            
        for filename, lines in arts.items():
            filepath = os.path.join(self.ascii_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
    
    def load_ascii_arts(self):
        arts = {}
        txt_files = glob.glob(os.path.join(self.ascii_dir, "*.txt"))
        
        for filepath in txt_files:
            filename = os.path.basename(filepath)
            name = os.path.splitext(filename)[0]
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    lines = f.read().strip().split('\n')
                    lines = [line[:CHAR_LIMIT] for line in lines[:3]]
                    while len(lines) < 3:
                        lines.append("")
                    
                    arts[name] = {
                        "name": name.replace('_', ' ').title(),
                        "type": "static",
                        "lines": lines
                    }
            except:
                pass
        
        return arts

class PresetManager:
    @staticmethod
    def get_all_presets(ascii_arts):
        presets = {
            "Animations": {
                "japanese_rain": {"name": "Matrix Rain", "type": "animation", "func": "japanese_rain_animation"},
                "regular_rain": {"name": "Rain", "type": "animation", "func": "regular_rain_animation"},
                "snowflake": {"name": "Snowflakes", "type": "animation", "func": "snowflake_animation"},
                "pulse": {"name": "Pulse", "type": "animation", "func": "pulse_animation"},
                "sparkle": {"name": "Sparkles", "type": "animation", "func": "sparkle_animation"},
                "rainbow": {"name": "Rainbow", "type": "animation", "func": "rainbow_animation"},
                "fire": {"name": "Fire Effect", "type": "animation", "func": "fire_animation"},
                "wave": {"name": "Ocean Wave", "type": "animation", "func": "wave_animation"},
                "glitch": {"name": "Glitch Matrix", "type": "animation", "func": "glitch_animation"},
                "binary": {"name": "Binary Stream", "type": "animation", "func": "binary_stream_animation"},
            },
            "Gaming": {
                "loading": {"name": "Loading Bar", "type": "animation", "func": "loading_bar_animation"},
                "radar": {"name": "Radar Sweep", "type": "animation", "func": "radar_animation"},
                "snake": {"name": "Snake Game", "type": "animation", "func": "snake_game_animation"},
            },
            "Anime": {
                "anime_faces": {"name": "Anime Faces", "type": "animation", "func": "anime_faces_animation"},
                "anime_sparkle": {"name": "Anime Sparkles", "type": "animation", "func": "anime_sparkle_animation"},
                "cat_standing": {"name": "Standing Cat", "type": "animation", "func": "cat_standing_animation"},
                "cat_walking": {"name": "Walking Cat", "type": "animation", "func": "cat_walking_animation"},
                "mouse_running": {"name": "Running Mouse", "type": "animation", "func": "mouse_running_animation"},
            },
            "System": {
                "clock": {"name": "Clock", "type": "dynamic", "func": "show_clock"},
                "gpu_cpu_ram": {"name": "GPU CPU & RAM", "type": "dynamic", "func": "show_gpu_cpu_ram"},
                "ram_net_uptime": {"name": "RAM, NETWORK & UPTIME", "type": "dynamic", "func": "show_ram_network_uptime"},
                "temperatures": {"name": "Temperatures", "type": "dynamic", "func": "show_temperatures"},
            },
            "ASCII Art": ascii_arts
        }
        
        return presets