# Nova Pro X Controller

Ultimate OLED display controller for SteelSeries devices with animated effects and system monitoring.

## Features

- 🎮 **Gaming Animations**: Loading bars, radar sweep, snake game
- 🌊 **Visual Effects**: Matrix rain, fire, ocean waves, rainbow patterns
- 📊 **System Monitoring**:
  - GPU, CPU & RAM usage
  - Network speed and uptime
  - Temperature monitoring (requires OpenHardwareMonitor)
- 🎨 **ASCII Art Support**: Custom ASCII art library
- ⚡ **Real-time Updates**: Live system stats on your OLED display

## Requirements

- Windows 10/11
- Python 3.8+
- SteelSeries Engine 3
- SteelSeries Nova Pro X (other OLED devices may work but untested)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/nova-pro-x-controller.git
cd nova-pro-x-controller
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the application:

```bash
python main.py
```

## Building Executable

To create a standalone executable:

```bash
pyinstaller --onefile --windowed --name "NovaProXController" --icon="icon.ico" --collect-all customtkinter main.py
```

The program will automatically create the `ascii_arts` folder with default ASCII art files on first run.

## Temperature Monitoring

For CPU temperature monitoring, install and run one of these programs:

- [OpenHardwareMonitor](https://openhardwaremonitor.org/) (recommended)
- [HWiNFO64](https://www.hwinfo.com/)

## Usage

1. Make sure SteelSeries Engine 3 is running
2. Launch Nova Pro X Controller
3. Select animations or system monitors from the tabs
4. Customize animation speed with the slider
5. Create custom text displays in the Custom Text section

## Dependencies

- `customtkinter` - Modern UI framework
- `psutil` - System monitoring
- `GPUtil` - GPU monitoring
- `wmi` - Windows Management Instrumentation
- `requests` - API communication

## Custom ASCII Art

You can add your own ASCII art to the program:

1. Create a `.txt` file in the `ascii_arts` folder (created automatically on first run)
2. Each file must contain exactly 3 lines
3. Each line must be 15 characters or less
4. Restart the program to load new ASCII art

Example (`my_art.txt`):

```
   ╭─────╮
   │ HI! │
   ╰─────╯
```

## Known Issues

- Sometimes animations may flicker between two different animations. Use the Clear button to fix this issue.

## Author

Created by Zimcim

## License

This project is licensed under the MIT License.
