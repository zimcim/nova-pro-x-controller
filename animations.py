import random
import time
from datetime import datetime
from config import CHAR_LIMIT
import subprocess
import sys

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

try:
    import struct
    import mmap
    HAS_MMAP = True
except ImportError:
    HAS_MMAP = False

try:
    import wmi
    import pythoncom
    HAS_WMI = True
except ImportError:
    HAS_WMI = False

def get_gpu_info():
    try:
        if sys.platform == "win32":
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow = subprocess.SW_HIDE
            
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=utilization.gpu,temperature.gpu,name", "--format=csv,noheader,nounits"],
                capture_output=True,
                text=True,
                startupinfo=si,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        else:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=utilization.gpu,temperature.gpu,name", "--format=csv,noheader,nounits"],
                capture_output=True,
                text=True
            )
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if lines and lines[0]:
                values = lines[0].split(', ')
                if len(values) >= 3:
                    return {
                        "load": float(values[0]) / 100,
                        "temperature": float(values[1]),
                        "name": values[2]
                    }
    except:
        pass
    
    return None

class AnimationFunctions:
    def __init__(self):
        self.reset_all()
        self.mouse_position = -10
        self._last_net_recv = 0
        self._last_net_sent = 0
        self._last_net_time = time.time()
        self._wmi_initialized = False
        self._wmi_lock = False
    
    def reset_all(self):
        self.cpu_history = [0] * CHAR_LIMIT
        self.japanese_rain = [[' ' for _ in range(CHAR_LIMIT)] for _ in range(3)]
        self.japanese_chars = "あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん"
        self.rain_positions = [random.randint(0, 10) for _ in range(CHAR_LIMIT)]
        self.pulse_state = 0
        self.sparkle_positions = set()
        self.rainbow_offset = 0
        self.fire_state = [[0 for _ in range(CHAR_LIMIT)] for _ in range(3)]
        self.wave_offset = 0
        self.loading_pos = 0
        self.glitch_counter = 0
        self.radar_angle = 0
        self.typing_pos = 0
        self.typing_messages = [
            "GG EZ", "HEADSHOT!", "VICTORY!", "FLAWLESS", "DOMINATED",
            "LEGENDARY", "GODLIKE", "UNSTOPPABLE", "RAMPAGE", "SAVAGE"
        ]
        self.current_typing_msg = random.choice(self.typing_messages)
        self.binary_offset = 0
        self.snake_segments = [(1, 7)]
        self.snake_direction = 1
        self.regular_rain = [[' ' for _ in range(CHAR_LIMIT)] for _ in range(3)]
        self.rain_drops = [random.randint(0, 10) for _ in range(CHAR_LIMIT)]
        self.snow_positions = [(random.randint(0, 2), random.randint(0, CHAR_LIMIT-1)) for _ in range(5)]
        self.snow_counter = 0
        self.anime_face = 0
        self.anime_sparkle_pos = []
        self.cat_walk_frame = 0
        self.cat_position = 0
        self.mouse_position = CHAR_LIMIT - 1
        self.mouse_frame = 0
    
    def show_clock(self):
        now = datetime.now()
        return [
            now.strftime("%H:%M:%S"),
            now.strftime("%A")[:CHAR_LIMIT],
            now.strftime("%d %B %Y")[:CHAR_LIMIT]
        ]
    
    def show_gpu_cpu_ram(self):
        if HAS_PSUTIL:
            try:
                cpu = psutil.cpu_percent(interval=0.1)
                mem = psutil.virtual_memory()
                
                gpu_text = "GPU: N/A"
                gpu_info = get_gpu_info()
                if gpu_info:
                    gpu_text = f"GPU: {gpu_info['load'] * 100:.0f}%"
                
                return [
                    gpu_text,
                    f"CPU: {cpu:.0f}%",
                    f"RAM: {mem.percent:.0f}%"
                ]
            except Exception as e:
                return ["System Error", str(e)[:15], ""]
        else:
            return ["Install psutil", "pip install", "psutil"]
    
    def show_ram_network_uptime(self):
        if HAS_PSUTIL:
            try:
                mem = psutil.virtual_memory()
                
                net_io = psutil.net_io_counters()
                current_time = time.time()
                time_delta = current_time - self._last_net_time
                
                if time_delta > 0:
                    recv_speed = (net_io.bytes_recv - self._last_net_recv) / time_delta / 1024 / 1024
                    sent_speed = (net_io.bytes_sent - self._last_net_sent) / time_delta / 1024 / 1024
                    net_speed = recv_speed + sent_speed
                else:
                    net_speed = 0
                
                self._last_net_recv = net_io.bytes_recv
                self._last_net_sent = net_io.bytes_sent
                self._last_net_time = current_time
                
                boot_time = psutil.boot_time()
                uptime = time.time() - boot_time
                hours = int(uptime // 3600)
                mins = int((uptime % 3600) // 60)
                
                return [
                    f"RAM: {mem.percent:.0f}%",
                    f"NET: {net_speed:.1f} MB/s",
                    f"UP: {hours}h {mins}m"
                ]
            except Exception as e:
                return ["Error", str(e)[:15], ""]
        else:
            return ["Install psutil", "pip install", "psutil"]
    
    def get_cpu_temperature(self):
        if HAS_WMI and sys.platform == "win32":
            try:
                import threading
                current_thread = threading.current_thread()
                
                if not hasattr(current_thread, '_com_initialized'):
                    pythoncom.CoInitialize()
                    current_thread._com_initialized = True
                
                c = wmi.WMI(namespace="root\\OpenHardwareMonitor")
                cpu_temps = []
                
                for sensor in c.Sensor():
                    if sensor.SensorType == "Temperature":
                        if any(keyword in sensor.Name.upper() for keyword in ["CPU", "CORE", "PROCESSOR"]):
                            temp = float(sensor.Value)
                            if 0 < temp < 150:
                                cpu_temps.append(temp)
                
                if cpu_temps:
                    return sum(cpu_temps) / len(cpu_temps)
                    
            except:
                pass
        
        if HAS_WMI and sys.platform == "win32":
            try:
                import threading
                current_thread = threading.current_thread()
                
                if not hasattr(current_thread, '_com_initialized'):
                    pythoncom.CoInitialize()
                    current_thread._com_initialized = True
                
                c = wmi.WMI(namespace="root\\wmi")
                for thermal in c.MSAcpi_ThermalZoneTemperature():
                    temp = thermal.CurrentTemperature / 10.0 - 273.15
                    if 0 < temp < 150:
                        return temp
            except:
                pass
        
        if HAS_PSUTIL:
            try:
                if hasattr(psutil, "sensors_temperatures"):
                    temps = psutil.sensors_temperatures()
                    if temps:
                        for name, entries in temps.items():
                            if any(keyword in name.upper() for keyword in ["CPU", "CORE", "PROCESSOR"]):
                                for entry in entries:
                                    temp = entry.current
                                    if 0 < temp < 150:
                                        return temp
            except:
                pass
        
        try:
            for i in range(10):
                try:
                    with open(f"/sys/class/thermal/thermal_zone{i}/temp", 'r') as f:
                        temp = int(f.read().strip()) / 1000.0
                        if 0 < temp < 150:
                            return temp
                except:
                    continue
        except:
            pass
        
        if sys.platform == "win32" and HAS_MMAP:
            try:
                with mmap.mmap(-1, 1024, tagname="CoreTempMappingObject", access=mmap.ACCESS_READ) as mm:
                    mm.seek(0)
                    data = mm.read(256)
                    if len(data) >= 256:
                        cpu_count = struct.unpack('I', data[0:4])[0]
                        if cpu_count > 0 and cpu_count < 64:
                            temp_data_start = 160
                            temp = struct.unpack('f', data[temp_data_start:temp_data_start+4])[0]
                            if 0 < temp < 150:
                                return temp
            except:
                pass
        
        if sys.platform == "win32" and HAS_MMAP:
            try:
                with mmap.mmap(-1, 10240, tagname="HWiNFO_SENSORS_SM2", access=mmap.ACCESS_READ) as mm:
                    mm.seek(0)
                    header = mm.read(16)
                    if len(header) >= 16:
                        signature = header[:4]
                        if signature == b'HWiS':
                            sensor_count = struct.unpack('I', header[8:12])[0]
                            for i in range(min(sensor_count, 100)):
                                sensor_offset = 16 + i * 88
                                mm.seek(sensor_offset + 4)
                                sensor_name = mm.read(64).decode('ascii', errors='ignore').strip('\x00')
                                if 'CPU' in sensor_name.upper() and 'TEMP' in sensor_name.upper():
                                    mm.seek(sensor_offset + 76)
                                    temp = struct.unpack('d', mm.read(8))[0]
                                    if 0 < temp < 150:
                                        return temp
            except:
                pass
        
        return None
    
    def show_temperatures(self):
        cpu_temp = "CPU: N/A"
        gpu_temp = "GPU: N/A"
        
        cpu_temperature = self.get_cpu_temperature()
        if cpu_temperature:
            cpu_temp = f"CPU: {int(cpu_temperature)}°C"
        
        gpu_info = get_gpu_info()
        if gpu_info and 'temperature' in gpu_info:
            gpu_temp = f"GPU: {gpu_info['temperature']:.0f}°C"
        
        return [
            cpu_temp,
            gpu_temp,
            "Temperatures"
        ]
    
    def show_system(self):
        return self.show_gpu_cpu_ram()
    
    def get_uptime(self):
        if HAS_PSUTIL:
            try:
                boot_time = psutil.boot_time()
                uptime = time.time() - boot_time
                hours = int(uptime // 3600)
                mins = int((uptime % 3600) // 60)
                return f"{hours}h {mins}m"
            except:
                return "N/A"
        else:
            return "N/A"
    
    def show_cpu_graph(self):
        if HAS_PSUTIL:
            try:
                cpu = psutil.cpu_percent(interval=0.5)
                self.cpu_history.pop(0)
                self.cpu_history.append(int(cpu / 12.5))
                
                bar_chars = " ▁▂▃▄▅▆▇█"
                graph = ""
                for val in self.cpu_history:
                    graph += bar_chars[min(max(val, 0), 8)]
                
                return [
                    graph[:CHAR_LIMIT],
                    f"CPU: {cpu:.1f}%",
                    "History Graph"
                ]
            except Exception as e:
                return ["CPU Error", str(e)[:15], ""]
        else:
            return ["CPU Graph", "Install psutil", "pip install psutil"]
    
    def show_network(self):
        try:
            import socket
            hostname = socket.gethostname()[:CHAR_LIMIT]
            ip = socket.gethostbyname(socket.gethostname())
            
            return [
                f"Host: {hostname[:10]}",
                f"IP: {ip}",
                "Connected"
            ]
        except:
            return ["Network Info", "Disconnected", ""]
    
    def japanese_rain_animation(self):
        for col in range(CHAR_LIMIT):
            if self.rain_positions[col] > 0:
                if self.rain_positions[col] <= 3:
                    row = self.rain_positions[col] - 1
                    self.japanese_rain[row][col] = random.choice(self.japanese_chars)
                
                if self.rain_positions[col] > 1 and self.rain_positions[col] <= 4:
                    prev_row = self.rain_positions[col] - 2
                    if prev_row >= 0:
                        self.japanese_rain[prev_row][col] = ' '
                
                self.rain_positions[col] += 1
                
                if self.rain_positions[col] > 6:
                    self.rain_positions[col] = 0
                    for row in range(3):
                        self.japanese_rain[row][col] = ' '
            else:
                if random.random() > 0.7:
                    self.rain_positions[col] = 1
        
        return [''.join(row) for row in self.japanese_rain]
    
    def pulse_animation(self):
        try:
            chars = " ░▒▓█▓▒░ "
            self.pulse_state = (self.pulse_state + 1) % len(chars)
            char = chars[self.pulse_state]
            
            center = CHAR_LIMIT // 2
            lines = []
            
            for row in range(3):
                line = ""
                for col in range(CHAR_LIMIT):
                    dist = abs(col - center) + abs(row - 1)
                    if dist <= self.pulse_state % 8:
                        line += char
                    else:
                        line += " "
                lines.append(line)
            
            return lines
        except Exception as e:
            print(f"Pulse animation error: {e}")
            return ["Error", "Pulse Failed", ""]
    
    def sparkle_animation(self):
        grid = [[' ' for _ in range(CHAR_LIMIT)] for _ in range(3)]
        sparkles = ['·', '•', '*', '✦', '✧', '★']
        
        to_remove = set()
        for pos in self.sparkle_positions:
            if random.random() > 0.7:
                to_remove.add(pos)
        self.sparkle_positions -= to_remove
        
        for _ in range(random.randint(0, 3)):
            if len(self.sparkle_positions) < 10:
                row = random.randint(0, 2)
                col = random.randint(0, CHAR_LIMIT - 1)
                self.sparkle_positions.add((row, col))
        
        for row, col in self.sparkle_positions:
            grid[row][col] = random.choice(sparkles)
        
        return [''.join(row) for row in grid]
    
    def rainbow_animation(self):
        colors = "░▒▓█▓▒░"
        lines = []
        
        for row in range(3):
            line = ""
            for col in range(CHAR_LIMIT):
                idx = (col + self.rainbow_offset + row * 2) % len(colors)
                line += colors[idx]
            lines.append(line)
        
        self.rainbow_offset += 1
        return lines
    
    def fire_animation(self):
        fire_chars = [' ', '·', ':', '▪', '▫', '▬', '▲', '▼']
        
        for col in range(CHAR_LIMIT):
            self.fire_state[2][col] = random.randint(4, 7)
            
            if col > 0 and col < CHAR_LIMIT - 1:
                avg = (self.fire_state[2][col-1] + self.fire_state[2][col] + self.fire_state[2][col+1]) // 3
                self.fire_state[1][col] = max(0, avg + random.randint(-2, 1))
                
                avg = (self.fire_state[1][col-1] + self.fire_state[1][col] + self.fire_state[1][col+1]) // 3
                self.fire_state[0][col] = max(0, avg + random.randint(-2, 0))
        
        lines = []
        for row in range(3):
            line = ""
            for col in range(CHAR_LIMIT):
                intensity = min(7, self.fire_state[row][col])
                line += fire_chars[intensity]
            lines.append(line)
        
        return lines
    
    def wave_animation(self):
        wave_chars = " ·~≈≋━"
        lines = []
        
        for row in range(3):
            line = ""
            for col in range(CHAR_LIMIT):
                wave_val = abs(int(5 * (0.5 + 0.5 * 
                    (1 if row == 0 else 0.7 if row == 1 else 0.4) * 
                    (0.5 + 0.5 * (col / CHAR_LIMIT)) *
                    (0.5 + 0.5 * abs((self.wave_offset + col * 2) % 20 - 10) / 10))))
                
                wave_val = min(len(wave_chars) - 1, wave_val)
                line += wave_chars[wave_val]
            lines.append(line)
        
        self.wave_offset += 1
        return lines
    
    def loading_bar_animation(self):
        self.loading_pos = (self.loading_pos + 1) % (CHAR_LIMIT * 2)
        progress = min(CHAR_LIMIT, self.loading_pos)
        
        bar = ""
        for i in range(CHAR_LIMIT):
            if i < progress:
                bar += "█"
            elif i == progress:
                bar += "▓"
            else:
                bar += "░"
        
        percent = int((progress / CHAR_LIMIT) * 100)
        
        percent_str = f"{percent}%"
        padding = (CHAR_LIMIT - len(percent_str)) // 2
        percent_line = "█" * padding + percent_str + "█" * (CHAR_LIMIT - padding - len(percent_str))
        
        return [
            "██LOADING...█",
            bar,
            percent_line[:CHAR_LIMIT]
        ]
    
    def glitch_animation(self):
        glitch_chars = "01!@#$%^&*()<>?"
        self.glitch_counter += 1
        
        lines = []
        for row in range(3):
            line = ""
            for col in range(CHAR_LIMIT):
                if random.random() > 0.3:
                    if (self.glitch_counter + col + row * 5) % 10 < 3:
                        line += random.choice("01")
                    else:
                        line += " "
                else:
                    line += random.choice(glitch_chars)
            lines.append(line)
        
        return lines
    
    def radar_animation(self):
        self.radar_angle = (self.radar_angle + 15) % 360
        center_x = CHAR_LIMIT // 2
        center_y = 1
        
        grid = [[' ' for _ in range(CHAR_LIMIT)] for _ in range(3)]
        
        for row in range(3):
            for col in range(CHAR_LIMIT):
                dist = ((col - center_x) ** 2 + (row - center_y) ** 2) ** 0.5
                
                if 2.5 < dist < 3.5 or 5.5 < dist < 6.5:
                    grid[row][col] = '·'
                
                import math
                angle_rad = math.radians(self.radar_angle)
                sweep_x = int(center_x + 5 * math.cos(angle_rad))
                sweep_y = int(center_y + 2 * math.sin(angle_rad))
                
                if 0 <= sweep_y < 3 and 0 <= sweep_x < CHAR_LIMIT:
                    grid[sweep_y][sweep_x] = '█'
        
        if 0 <= center_y < 3 and 0 <= center_x < CHAR_LIMIT:
            grid[center_y][center_x] = '●'
        
        return [''.join(row) for row in grid]
    
    def typing_animation(self):
        self.typing_pos += 1
        
        if self.typing_pos > len(self.current_typing_msg) + 10:
            self.typing_pos = 0
            self.current_typing_msg = random.choice(self.typing_messages)
        
        displayed = self.current_typing_msg[:self.typing_pos]
        cursor = "█" if self.typing_pos % 2 == 0 else "_"
        
        if self.typing_pos <= len(self.current_typing_msg):
            displayed += cursor
        
        line_length = len(displayed)
        if line_length < CHAR_LIMIT:
            padding_left = (CHAR_LIMIT - line_length) // 2
            padding_right = CHAR_LIMIT - line_length - padding_left
            displayed = "█" * padding_left + displayed + "█" * padding_right
        
        return [
            "█████████████",
            displayed[:CHAR_LIMIT],
            "█████████████"
        ]
    
    def binary_stream_animation(self):
        self.binary_offset += 1
        lines = []
        
        for row in range(3):
            line = ""
            for col in range(CHAR_LIMIT):
                pos = (col + self.binary_offset + row * 3) % 8
                if pos < 4:
                    line += random.choice("01")
                else:
                    line += " "
            lines.append(line)
        
        return lines
    
    def snake_game_animation(self):
        grid = [[' ' for _ in range(CHAR_LIMIT)] for _ in range(3)]
        
        head_row, head_col = self.snake_segments[0]
        new_col = head_col + self.snake_direction
        
        if new_col >= CHAR_LIMIT - 1 or new_col <= 0:
            self.snake_direction *= -1
            new_col = head_col + self.snake_direction
        
        self.snake_segments.insert(0, (head_row, new_col))
        
        if len(self.snake_segments) > 5:
            self.snake_segments.pop()
        
        for i, (row, col) in enumerate(self.snake_segments):
            if 0 <= row < 3 and 0 <= col < CHAR_LIMIT:
                if i == 0:
                    grid[row][col] = '●'
                else:
                    grid[row][col] = '○'
        
        return [''.join(row) for row in grid]
    
    def regular_rain_animation(self):
        rain_chars = ['|', '¦', '┆', '┊', '╎', '╏']
        
        for col in range(CHAR_LIMIT):
            if self.rain_drops[col] > 0:
                if self.rain_drops[col] <= 3:
                    row = self.rain_drops[col] - 1
                    self.regular_rain[row][col] = random.choice(rain_chars)
                
                if self.rain_drops[col] > 1 and self.rain_drops[col] <= 4:
                    prev_row = self.rain_drops[col] - 2
                    if prev_row >= 0:
                        self.regular_rain[prev_row][col] = ' '
                
                self.rain_drops[col] += 1
                
                if self.rain_drops[col] > 6:
                    self.rain_drops[col] = 0
                    for row in range(3):
                        self.regular_rain[row][col] = ' '
            else:
                if random.random() > 0.8:
                    self.rain_drops[col] = 1
        
        return [''.join(row) for row in self.regular_rain]
    
    def snowflake_animation(self):
        grid = [[' ' for _ in range(CHAR_LIMIT)] for _ in range(3)]
        snowflakes = ['❄', '❅', '❆', '*', '·', '◦']
        
        self.snow_counter += 1
        
        new_positions = []
        for row, col in self.snow_positions:
            new_row = row + 1
            if self.snow_counter % 2 == 0:
                new_col = col + random.choice([-1, 0, 1])
            else:
                new_col = col
            
            if new_row < 3 and 0 <= new_col < CHAR_LIMIT:
                new_positions.append((new_row, new_col))
        
        if len(new_positions) < 8 and random.random() > 0.6:
            new_positions.append((0, random.randint(0, CHAR_LIMIT-1)))
        
        self.snow_positions = new_positions
        
        for row, col in self.snow_positions:
            if 0 <= row < 3 and 0 <= col < CHAR_LIMIT:
                grid[row][col] = random.choice(snowflakes)
        
        return [''.join(row) for row in grid]
    
    def anime_faces_animation(self):
        faces = [
            ["  ◕ ‿ ◕    ", "    ___    ", "   \\___/   "],
            ["  ^ _ ^    ", "    ___    ", "   \\___/   "],
            ["  ◕ ‿ ~    ", "    ___    ", "   \\___/   "],
            ["  - ‿ ◕    ", "    ___    ", "   \\___/   "],
            ["  ★ ‿ ★    ", "    ___    ", "   \\___/   "],
            ["  ♥ ‿ ♥    ", "    ___    ", "   \\___/   "],
            ["  - _ -    ", "    ___    ", "   \\___/   "],
            ["  ˘ _ ˘    ", "    ___    ", "   \\___/   "],
            ["  O _ O    ", "    ___    ", "   \\___/   "],
            ["  ◉ _ ◉    ", "    ___    ", "   \\___/   "],
        ]
        
        self.anime_face = (self.anime_face + 1) % (len(faces) * 15)
        face_index = self.anime_face // 15
        
        return faces[face_index]
    
    def anime_sparkle_animation(self):
        grid = [[' ' for _ in range(CHAR_LIMIT)] for _ in range(3)]
        sparkles = ['✧', '✦', '✩', '✪', '⋆', '｡', '°', '∘']
        
        if len(self.anime_sparkle_pos) < 6 and random.random() > 0.7:
            self.anime_sparkle_pos.append({
                'row': random.randint(0, 2),
                'col': random.randint(0, CHAR_LIMIT-1),
                'life': 0,
                'char': random.choice(sparkles)
            })
        
        new_sparkles = []
        for sparkle in self.anime_sparkle_pos:
            sparkle['life'] += 1
            if sparkle['life'] < 15:
                if sparkle['life'] % 3 == 0:
                    sparkle['char'] = random.choice(sparkles)
                
                row, col = sparkle['row'], sparkle['col']
                if 0 <= row < 3 and 0 <= col < CHAR_LIMIT:
                    grid[row][col] = sparkle['char']
                
                new_sparkles.append(sparkle)
        
        self.anime_sparkle_pos = new_sparkles
        
        return [''.join(row) for row in grid]
    
    def cat_standing_animation(self):
        frames = [
            ["    /\\_/\\    ", "   ( o.o )   ", "    > ^ <    "],
            ["    /\\_/\\    ", "   ( o.o )   ", "    > ~ <    "],
            ["    /\\_/\\    ", "   ( o.o )   ", "    > v <    "],
            ["    /\\_/\\    ", "   ( o.o )   ", "    > ~ <    "],
        ]
        
        self.cat_walk_frame = (self.cat_walk_frame + 1) % (len(frames) * 10)
        frame_index = self.cat_walk_frame // 10
        
        return frames[frame_index]
    
    def cat_walking_animation(self):
        self.cat_walk_frame = (self.cat_walk_frame + 1) % 4
        self.cat_position = (self.cat_position + 1) % (CHAR_LIMIT + 10)
        
        grid = [[' ' for _ in range(CHAR_LIMIT)] for _ in range(3)]
        
        cat_frames = [
            ["∧_∧", "(='.'=)", "(¨)_(¨)"],
            ["∧_∧", "(='.'=)", "(_¨)(¨)"],
            ["∧_∧", "(='.'=)", "(¨)_(¨)"],
            ["∧_∧", "(='.'=)", "(¨)(_¨)"],
        ]
        
        current_frame = cat_frames[self.cat_walk_frame]
        
        for row in range(3):
            cat_line = current_frame[row]
            start_pos = self.cat_position - len(cat_line)
            
            for i, char in enumerate(cat_line):
                pos = start_pos + i
                if 0 <= pos < CHAR_LIMIT:
                    grid[row][pos] = char
        
        return [''.join(row) for row in grid]
    
    def mouse_running_animation(self):
        self.mouse_frame = (self.mouse_frame + 1) % 3
        self.mouse_position += 2
        
        if self.mouse_position > CHAR_LIMIT + 5:
            self.mouse_position = -10
        
        grid = [[' ' for _ in range(CHAR_LIMIT)] for _ in range(3)]
        
        mouse_frames = [
            ["", "ᘛ⁐ᕐᐷ...", ""],
            ["", ".ᘛ⁐ᕐᐷ..", ""],
            ["", "..ᘛ⁐ᕐᐷ.", ""],
        ]
        
        mouse = mouse_frames[self.mouse_frame]
        for row in range(3):
            if mouse[row]:
                for i, char in enumerate(mouse[row]):
                    pos = self.mouse_position + i
                    if 0 <= pos < CHAR_LIMIT:
                        grid[row][pos] = char
        
        for i in range(3):
            trail_pos = self.mouse_position - i - 1
            if 0 <= trail_pos < CHAR_LIMIT:
                grid[1][trail_pos] = '-'
        
        return [''.join(row) for row in grid]