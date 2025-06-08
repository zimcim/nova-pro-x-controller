import tkinter as tk
import customtkinter as ctk
import platform
from config import *

class NovaUI:
    def __init__(self, root, controller, on_preset_load, on_custom_send, on_clear, on_stop, on_speed_change, on_speed_release=None):
        self.root = root
        self.controller = controller
        self.on_preset_load = on_preset_load
        self.on_custom_send = on_custom_send
        self.on_clear = on_clear
        self.on_stop = on_stop
        self.on_speed_change = on_speed_change
        self.on_speed_release = on_speed_release
        
        self.preset_buttons = {}
        self.all_presets = {}
        
        self.create_ui()
    
    def create_ui(self):
        main = ctk.CTkFrame(self.root)
        main.pack(fill="both", expand=True, padx=10, pady=10)
        
        left = ctk.CTkFrame(main, width=300)
        left.pack(side="left", fill="y", padx=(0, 10))
        
        ctk.CTkLabel(left, text="NOVA PRO X", font=("Arial", 24, "bold")).pack(pady=(10, 5))
        ctk.CTkLabel(left, text="Ultimate OLED Controller", font=("Arial", 12)).pack(pady=(0, 10))
        
        self.status_frame = ctk.CTkFrame(left)
        self.status_frame.pack(fill="x", padx=10, pady=10)
        
        status_row = ctk.CTkFrame(self.status_frame)
        status_row.pack(fill="x", pady=5)
        
        self.status_dot = ctk.CTkLabel(status_row, text="●", font=("Arial", 16))
        self.status_dot.pack(side="left", padx=5)
        
        self.status_text = ctk.CTkLabel(status_row, text="Disconnected", font=("Arial", 12))
        self.status_text.pack(side="left")
        
        self.device_info = ctk.CTkLabel(self.status_frame, text="", font=("Arial", 10), text_color="gray")
        self.device_info.pack(pady=5)
        
        self.pc_info = ctk.CTkLabel(self.status_frame, text="", font=("Arial", 10), text_color="gray")
        self.pc_info.pack(pady=(0, 5))
        
        self.tabs = ctk.CTkTabview(left, width=280, height=380)
        self.tabs.pack(fill="both", expand=True, padx=10, pady=10)
        
        right = ctk.CTkFrame(main)
        right.pack(side="right", fill="both", expand=True)
        
        preview_frame = ctk.CTkFrame(right)
        preview_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(preview_frame, text="OLED Preview", font=("Arial", 16, "bold")).pack(pady=10)
        
        self.oled_frame = ctk.CTkFrame(preview_frame, fg_color=OLED_BACKGROUND, width=300, height=120)
        self.oled_frame.pack(padx=20, pady=10)
        
        self.preview_lines = []
        for i in range(3):
            label = ctk.CTkLabel(
                self.oled_frame,
                text="",
                font=("Consolas", 18),
                text_color=OLED_PREVIEW_COLOR,
                fg_color=OLED_BACKGROUND
            )
            label.pack(pady=5)
            self.preview_lines.append(label)
        
        custom_frame = ctk.CTkFrame(right)
        custom_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(custom_frame, text="Custom Text", font=("Arial", 16, "bold")).pack(pady=10)
        
        self.line_entries = []
        for i in range(3):
            frame = ctk.CTkFrame(custom_frame)
            frame.pack(fill="x", pady=5)
            
            ctk.CTkLabel(frame, text=f"Line {i+1}:", width=60).pack(side="left", padx=10)
            
            entry = ctk.CTkEntry(frame, width=200, placeholder_text=f"Max {CHAR_LIMIT} characters")
            entry.pack(side="left", padx=10)
            entry.bind("<KeyRelease>", self.preview_custom)
            self.line_entries.append(entry)
        
        btn_frame = ctk.CTkFrame(custom_frame)
        btn_frame.pack(pady=20)
        
        ctk.CTkButton(btn_frame, text="Send to OLED", command=self.send_custom, width=120).pack(side="left", padx=5)
        
        self.stop_btn = ctk.CTkButton(btn_frame, text="Stop Animation", command=self.on_stop, state="disabled", width=120)
        self.stop_btn.pack(side="left", padx=5)
        
        ctk.CTkButton(btn_frame, text="Clear", command=self.on_clear, width=120).pack(side="left", padx=5)
        
        settings_frame = ctk.CTkFrame(right)
        settings_frame.pack(fill="x", padx=20, pady=10)
        
        self.auto_start = ctk.CTkCheckBox(
            settings_frame,
            text="Auto-start last preset on launch"
        )
        self.auto_start.pack(pady=5)
        self.auto_start.select()
        
        speed_frame = ctk.CTkFrame(settings_frame)
        speed_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(speed_frame, text="Animation Speed (ms):").pack(side="left", padx=10)
        
        self.speed_slider = ctk.CTkSlider(speed_frame, from_=MIN_SPEED_MS, to=MAX_SPEED_MS, command=self.update_speed)
        self.speed_slider.pack(side="left", fill="x", expand=True, padx=10)
        self.speed_slider.set(DEFAULT_SPEED_MS)
        
        
        if self.on_speed_release:
            self.speed_slider.bind("<ButtonRelease-1>", self.on_speed_release)
        
        self.speed_label = ctk.CTkLabel(speed_frame, text=f"{DEFAULT_SPEED_MS}ms")
        self.speed_label.pack(side="left", padx=10)
        
        footer_frame = ctk.CTkFrame(self.root)
        footer_frame.pack(side="bottom", fill="x", pady=5)
        
        left_footer = ctk.CTkLabel(
            footer_frame, 
            text=f"created by {DEVELOPER.lower()}", 
            font=("Arial", 10), 
            text_color="gray"
        )
        left_footer.pack(side="left", padx=20)
        
        right_footer = ctk.CTkLabel(
            footer_frame, 
            text=VERSION, 
            font=("Arial", 10), 
            text_color="gray"
        )
        right_footer.pack(side="right", padx=20)
    
    def update_speed(self, value):
        self.speed_label.configure(text=f"{int(value)}ms")
        self.on_speed_change(value)
    
    def set_presets(self, presets):
        self.all_presets = presets
        
        for category, preset_dict in presets.items():
            tab = self.tabs.add(category)
            
            if category == "ASCII Art":
                self.ascii_scroll = ctk.CTkScrollableFrame(tab, height=300)
                self.ascii_scroll.pack(fill="both", expand=True)
                parent = self.ascii_scroll
            else:
                parent = tab
            
            for preset_id, preset_data in preset_dict.items():
                pid = str(preset_id)
                pdata = dict(preset_data)
                
                btn = ctk.CTkButton(
                    parent,
                    text=pdata["name"],
                    command=lambda p=pid, d=pdata: self.on_preset_load(p, d),
                    height=30
                )
                btn.pack(fill="x", pady=2)
                self.preset_buttons[pid] = btn
    
    def update_preview(self, l1="", l2="", l3=""):
        lines = [
            l1.replace(' ', BLANK_SPACE_CHAR),
            l2.replace(' ', BLANK_SPACE_CHAR),
            l3.replace(' ', BLANK_SPACE_CHAR)
        ]
        for i, label in enumerate(self.preview_lines):
            label.configure(text=lines[i])
    
    def preview_custom(self, event=None):
        lines = [e.get()[:CHAR_LIMIT] for e in self.line_entries]
        self.update_preview(*lines)
    
    def send_custom(self):
        lines = [e.get()[:CHAR_LIMIT] for e in self.line_entries]
        self.on_custom_send(lines)
    
    def set_status(self, connected, text=""):
        if connected:
            self.status_dot.configure(text_color="green")
            self.status_text.configure(text="Connected")
        else:
            self.status_dot.configure(text_color="red")
            self.status_text.configure(text=text or "Disconnected")
    
    def update_device_info(self):
        try:
            self.device_info.configure(text="Nova Pro X")
            pc_name = platform.node()[:15]
            pc_os = platform.system()
            self.pc_info.configure(text=f"{pc_name} ({pc_os})")
        except:
            pass
    
    def update_button_colors(self, active_preset_id=None):
        for pid, btn in self.preset_buttons.items():
            try:
                if str(pid) == str(active_preset_id):
                    btn.configure(fg_color=BUTTON_COLOR_ACTIVE)
                else:
                    btn.configure(fg_color=BUTTON_COLOR_DEFAULT)
            except:
                pass
    
    def clear_custom_text(self):
        for e in self.line_entries:
            e.delete(0, tk.END)
    
    def reload_ascii_arts(self, ascii_arts):
        for widget in self.ascii_scroll.winfo_children():
            widget.destroy()
        
        self.all_presets["ASCII Art"] = ascii_arts
        
        for preset_id, preset_data in ascii_arts.items():
            pid = str(preset_id)
            pdata = dict(preset_data)
            
            btn = ctk.CTkButton(
                self.ascii_scroll,
                text=pdata["name"],
                command=lambda p=pid, d=pdata: self.on_preset_load(p, d),
                height=30
            )
            btn.pack(fill="x", pady=2)
            self.preset_buttons[pid] = btn