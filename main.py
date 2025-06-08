import customtkinter as ctk
import json
import requests
import time
import os
import threading
import queue
import configparser
from config import *
from animations import AnimationFunctions
from ascii_manager import ASCIIArtManager, PresetManager
from ui import NovaUI

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def get_server_url():
    try:
        if os.name == 'nt':
            config_path = os.path.join(os.environ.get('PROGRAMDATA', 'C:\\ProgramData'), 
                                     'SteelSeries', 'SteelSeries Engine 3', 'coreProps.json')
        else:
            config_path = os.path.expanduser('~/Library/Application Support/SteelSeries Engine 3/coreProps.json')
        
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
                return f"http://{config['address']}"
    except:
        pass
    
    return DEFAULT_SERVER_URL

class OLEDController:
    def __init__(self):
        self.server_url = get_server_url()
        self.game_name = GAME_NAME
        self.current_value = 0
        self.is_connected = False
        
    def setup(self):
        self.is_connected = False
        try:
            requests.post(f"{self.server_url}/remove_game", json={"game": self.game_name}, timeout=2)
            time.sleep(0.2)
            
            metadata = {
                "game": self.game_name,
                "game_display_name": GAME_DISPLAY_NAME,
                "developer": DEVELOPER
            }
            requests.post(f"{self.server_url}/game_metadata", json=metadata, timeout=2)
            
            bind_data = {
                "game": self.game_name,
                "event": "DISPLAY",
                "handlers": [{
                    "device-type": "screened",
                    "zone": "one",
                    "mode": "screen",
                    "datas": [{
                        "lines": [
                            {"has-text": True, "context-frame-key": "l1"},
                            {"has-text": True, "context-frame-key": "l2"},
                            {"has-text": True, "context-frame-key": "l3"}
                        ]
                    }]
                }]
            }
            response = requests.post(f"{self.server_url}/bind_game_event", json=bind_data, timeout=2)
            self.is_connected = response.status_code == 200
            return self.is_connected
        except:
            self.is_connected = False
            return False
    
    def display(self, line1="", line2="", line3=""):
        if not self.is_connected:
            return False
            
        self.current_value = (self.current_value + 1) % 100
        
        line1_display = str(line1).replace(' ', BLANK_SPACE_CHAR)
        line2_display = str(line2).replace(' ', BLANK_SPACE_CHAR)
        line3_display = str(line3).replace(' ', BLANK_SPACE_CHAR)
        
        data = {
            "game": self.game_name,
            "event": "DISPLAY",
            "data": {
                "value": self.current_value,
                "frame": {
                    "l1": line1_display[:CHAR_LIMIT],
                    "l2": line2_display[:CHAR_LIMIT],
                    "l3": line3_display[:CHAR_LIMIT]
                }
            }
        }
        
        try:
            response = requests.post(f"{self.server_url}/game_event", json=data, timeout=0.5)
            return response.status_code == 200
        except Exception as e:
            return False
    
    def cleanup(self):
        try:
            for _ in range(3):
                self.display("", "", "")
                time.sleep(0.01)
            requests.post(f"{self.server_url}/remove_game", json={"game": self.game_name}, timeout=1)
        except:
            pass

class NovaProUltimateGUI:
    def __init__(self):
        self.controller = OLEDController()
        self.animations = AnimationFunctions()
        self.ascii_manager = ASCIIArtManager()
        self.current_preset = None
        self.animation_thread = None
        self.animation_running = False
        self.update_queue = queue.Queue(maxsize=100)
        self.current_speed = DEFAULT_SPEED_MS
        self.settings_loaded = False  
        
        self.config = configparser.ConfigParser()
        self.config_file = CONFIG_FILE
        
        ascii_arts = self.ascii_manager.load_ascii_arts()
        self.all_presets = PresetManager.get_all_presets(ascii_arts)
        
        self.root = ctk.CTk()
        self.root.title("Nova Pro X Ultimate Controller")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        
        self.ui = NovaUI(
            self.root,
            self.controller,
            self.load_preset,
            self.send_custom,
            self.clear_display,
            self.stop_animation,
            self.on_speed_change,
            self.on_speed_release  
        )
        
        self.ui.set_presets(self.all_presets)
        self.load_settings()
        self.connect_device()
        self.process_queue()
        
    def connect_device(self):
        try:
            if self.controller.setup():
                self.ui.set_status(True)
                self.ui.update_device_info()
                
                self.controller.display("", "", "")
                self.ui.update_preview("", "", "")
                
                
                if hasattr(self.ui, 'auto_start') and self.ui.auto_start.get():
                    last_preset = getattr(self, 'loaded_last_preset', '')
                    if last_preset:
                        
                        self.root.after(500, self.load_last_preset)
            else:
                self.ui.set_status(False)
        except:
            self.ui.set_status(False, "Error")
    
    def process_queue(self):
        if not hasattr(self, 'root') or not self.root.winfo_exists():
            return
            
        try:
            for _ in range(10):
                try:
                    lines = self.update_queue.get_nowait()
                    if lines and len(lines) == 3:
                        self.ui.update_preview(*lines)
                except queue.Empty:
                    break
        except:
            pass
        
        try:
            self.root.after(50, self.process_queue)
        except:
            pass
    
    def on_speed_change(self, value):
        
        
        if hasattr(self.ui, 'speed_label'):
            self.ui.speed_label.configure(text=f"{int(value)}ms")
    
    def on_speed_release(self, event=None):
        
        if hasattr(self.ui, 'speed_slider'):
            value = self.ui.speed_slider.get()
            self.current_speed = value
            
            
            if hasattr(self, 'settings_loaded') and self.settings_loaded:
                self.save_settings()
            
            
            if self.animation_running and self.current_preset:
                print(f"Restarting animation with new speed: {int(value)}ms")
                
                
                current_preset_id = self.current_preset
                current_preset_data = None
                
                
                if current_preset_id == "custom_text":
                    
                    lines = [entry.get()[:CHAR_LIMIT] for entry in self.ui.line_entries]
                    self.send_custom(lines)
                    return
                else:
                    
                    for category, presets in self.all_presets.items():
                        if current_preset_id in presets:
                            current_preset_data = presets[current_preset_id]
                            break
                
                
                if current_preset_data:
                    self.load_preset(current_preset_id, current_preset_data)
    
    def stop_animation(self):
        self.animation_running = False
        
        try:
            if hasattr(self.ui, 'stop_btn') and self.ui.stop_btn:
                self.ui.stop_btn.configure(state="disabled")
        except:
            pass
        
        if self.animation_thread:
            if self.animation_thread.is_alive():
                self.animation_thread.join(timeout=1.0)
        
        self.animation_thread = None
        
        cleared = 0
        try:
            while not self.update_queue.empty() and cleared < 100:
                self.update_queue.get_nowait()
                cleared += 1
        except:
            pass
        
        self.controller.display("", "", "")
        self.ui.update_preview("", "", "")
        
        time.sleep(0.1)
    
    def load_preset(self, preset_id, preset_data):
        try:
            self.stop_animation()
            
            self.controller.display("", "", "")
            self.ui.update_preview("", "", "")
            time.sleep(0.05)
            
            self.animations.reset_all()
            self.current_preset = preset_id
            
            while not self.update_queue.empty():
                try:
                    self.update_queue.get_nowait()
                except:
                    break
            
            self.ui.update_button_colors(preset_id)
            
            if preset_data["type"] == "static":
                lines = preset_data["lines"]
                
                def make_static_display(static_lines):
                    def static_display():
                        return list(static_lines)
                    return static_display
                
                static_func = make_static_display(lines)
                static_func.__name__ = 'static_display'
                
                self.animation_running = True
                if hasattr(self.ui, 'stop_btn') and self.ui.stop_btn:
                    self.ui.stop_btn.configure(state="normal")
                
                self.controller.display(*lines)
                self.ui.update_preview(*lines)
                
                self.start_animation_thread(static_func, self.current_speed)
                
            elif preset_data["type"] in ["dynamic", "animation"]:
                self.animation_running = True
                
                if hasattr(self.ui, 'stop_btn') and self.ui.stop_btn:
                    self.ui.stop_btn.configure(state="normal")
                
                func_name = preset_data["func"]
                
                try:
                    func = getattr(self.animations, func_name)
                    
                    try:
                        test_result = func()
                        if not test_result or len(test_result) != 3:
                            print(f"Invalid function result: {test_result}")
                            self.animation_running = False
                            return
                    except Exception as test_e:
                        print(f"Function test failed: {test_e}")
                        self.animation_running = False
                        return
                    
                    self.start_animation_thread(func, self.current_speed)
                    
                except Exception as e:
                    print(f"Error in animation setup: {e}")
                    self.animation_running = False
                    if hasattr(self.ui, 'stop_btn') and self.ui.stop_btn:
                        self.ui.stop_btn.configure(state="disabled")
            
            self.save_settings()
            
        except Exception as e:
            print(f"ERROR in load_preset: {e}")
            import traceback
            traceback.print_exc()
            self.animation_running = False
    
    def start_animation_thread(self, func, speed):
        try:
            if self.animation_thread and self.animation_thread.is_alive():
                self.animation_thread.join(timeout=1.0)
            
            self.animation_thread = threading.Thread(
                target=self.run_animation,
                args=(func, speed),
                daemon=True,
                name=f"Animation-{func.__name__ if hasattr(func, '__name__') else 'unknown'}"
            )
            self.animation_thread.start()
        except Exception as e:
            print(f"Error starting thread: {e}")
            self.animation_running = False
            self.root.after(0, lambda: self.ui.stop_btn.configure(state="disabled"))
    
    def run_animation(self, func, speed_ms):
        func_name = func.__name__ if hasattr(func, '__name__') else 'unknown'
        
        if func_name == 'show_clock':
            interval = 1.0
        elif func_name == 'show_gpu_cpu_ram':
            interval = 1.0
        elif func_name == 'show_ram_network_uptime':
            interval = 1.0
        elif func_name == 'show_temperatures':
            interval = 2.0
        elif func_name == 'show_system':
            interval = 2.0
        elif func_name == 'show_network':
            interval = 5.0
        elif func_name == 'static_display':
            interval = 1.0
        elif func_name == 'custom_display':
            interval = 1.0
        elif 'show_' in func_name:
            interval = 1.0
        else:
            interval = self.current_speed / 1000.0
        
        error_count = 0
        max_errors = 5
        
        while self.animation_running and error_count < max_errors:
            try:
                if not self.animation_running:
                    break
                
                lines = func()
                if not lines or not isinstance(lines, (list, tuple)) or len(lines) != 3:
                    error_count += 1
                    continue
                
                if self.controller.is_connected:
                    self.controller.display(*lines)
                
                try:
                    self.update_queue.put(lines, block=False)
                except queue.Full:
                    pass
                
                error_count = 0
                
            except Exception as e:
                error_count += 1
                if error_count == 1:
                    print(f"Animation error: {e}")
            
            time.sleep(interval)
    
    def send_custom(self, lines):
        self.stop_animation()
        self.current_preset = "custom_text"
        
        
        def make_custom_display(custom_lines):
            def custom_display():
                return list(custom_lines)
            return custom_display
        
        custom_func = make_custom_display(lines)
        custom_func.__name__ = 'custom_display'
        
        self.animation_running = True
        if hasattr(self.ui, 'stop_btn') and self.ui.stop_btn:
            self.ui.stop_btn.configure(state="normal")
        
        
        self.controller.display(*lines)
        self.ui.update_preview(*lines)
        
        
        self.start_animation_thread(custom_func, self.current_speed)
        
        self.ui.update_button_colors(None)
        self.save_settings()
    
    def clear_display(self):
        self.stop_animation()
        self.animations.reset_all()
        self.current_preset = None
        self.controller.display("", "", "")
        self.ui.update_preview("", "", "")
        self.ui.clear_custom_text()
        self.ui.update_button_colors(None)
        self.save_settings()  
    
    def save_settings(self):
        try:
            
            if not hasattr(self, 'ui') or not hasattr(self.ui, 'line_entries'):
                print("UI not ready, skipping save")
                return
                
            if not self.config.has_section('Settings'):
                self.config.add_section('Settings')
            
            if hasattr(self.ui, 'auto_start'):
                self.config.set('Settings', 'auto_start', str(self.ui.auto_start.get()))
            
            self.config.set('Settings', 'last_preset', self.current_preset or '')
            
            
            for i, entry in enumerate(self.ui.line_entries):
                self.config.set('Settings', f'custom_line_{i+1}', entry.get())
            
            if hasattr(self.ui, 'speed_slider'):
                self.config.set('Settings', 'speed', str(self.ui.speed_slider.get()))
            
            print(f"Saving settings - Last preset: {self.current_preset}")
            with open(self.config_file, 'w') as f:
                self.config.write(f)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def load_settings(self):
        if os.path.exists(self.config_file):
            try:
                
                self.config.read(self.config_file)
                
                
                self.loaded_last_preset = self.config.get('Settings', 'last_preset', fallback='')
                print(f"Config file found. Last preset: {self.loaded_last_preset}")
                
                
                self.current_preset = self.loaded_last_preset if self.loaded_last_preset else None
                
                if hasattr(self.ui, 'auto_start') and self.config.has_option('Settings', 'auto_start'):
                    if self.config.getboolean('Settings', 'auto_start'):
                        self.ui.auto_start.select()
                    else:
                        self.ui.auto_start.deselect()
                else:
                    if hasattr(self.ui, 'auto_start'):
                        self.ui.auto_start.select()
                
                if hasattr(self.ui, 'speed_slider') and self.config.has_option('Settings', 'speed'):
                    speed = self.config.getfloat('Settings', 'speed')
                    self.ui.speed_slider.set(speed)
                    self.ui.update_speed(speed)
                    self.current_speed = speed
                
                
                custom_lines_loaded = []
                for i in range(3):
                    if self.config.has_option('Settings', f'custom_line_{i+1}'):
                        text = self.config.get('Settings', f'custom_line_{i+1}')
                        self.ui.line_entries[i].delete(0, 'end')
                        self.ui.line_entries[i].insert(0, text)
                        custom_lines_loaded.append(text)
                    else:
                        custom_lines_loaded.append("")
                        
                print(f"Custom lines loaded from config: {custom_lines_loaded}")
                print(f"Settings loaded successfully")
                
                
                self.settings_loaded = True
                
            except Exception as e:
                print(f"Error loading settings: {e}")
                import traceback
                traceback.print_exc()
                self.loaded_last_preset = ''
                self.settings_loaded = True
        else:
            self.loaded_last_preset = ''
            self.settings_loaded = True
            print("No settings file found")
    
    def load_last_preset(self):
        """Load the last preset that was saved"""
        last_preset = getattr(self, 'loaded_last_preset', '')
        print(f"Loading last preset: {last_preset}")
        
        if last_preset == "custom_text":
            
            def load_custom():
                
                lines = [entry.get()[:CHAR_LIMIT] for entry in self.ui.line_entries]
                print(f"Entry field contents: {lines}")
                
                if any(lines):
                    print(f"Restoring custom text: {lines}")
                    self.send_custom(lines)
                else:
                    print("No custom text found in entry fields")
            
            
            self.root.after(200, load_custom)
        elif last_preset:
            for category, presets in self.all_presets.items():
                if last_preset in presets:
                    self.load_preset(last_preset, presets[last_preset])
                    break
    
    def run(self):
        try:
            self.root.protocol("WM_DELETE_WINDOW", self.on_close)
            
            self.root.mainloop()
        except Exception as e:
            print(f"Runtime error: {e}")
            import traceback
            traceback.print_exc()
            self.on_close()
    
    def on_close(self):
        try:
            self.stop_animation()
            self.controller.cleanup()
            self.save_settings()
            self.root.destroy()
        except:
            try:
                self.root.destroy()
            except:
                pass

def main():
    print(f"\n=== Nova Pro X Ultimate Controller {VERSION} ===\n")
    
    required = ["customtkinter", "requests"]
    optional = ["psutil"]
    
    missing = []
    for pkg in required:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    
    if missing:
        print(f"Missing required packages: {', '.join(missing)}")
        print("Install with: pip install customtkinter requests")
        return
    
    print(f"Character limit: {CHAR_LIMIT}")
    print(f"Space display: Unicode blank ({BLANK_SPACE_CHAR})")
    
    if 'psutil' in optional:
        try:
            import psutil
        except ImportError:
            print("Note: Install psutil for system monitoring")
            print("      pip install psutil")
    
    print("\nStarting application...\n")
    
    try:
        app = NovaProUltimateGUI()
        app.run()
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        print("\nPossible causes:")
        print("1. SteelSeries Engine 3 not running")
        print("2. CustomTkinter version incompatible")
        print("3. Missing dependencies")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()