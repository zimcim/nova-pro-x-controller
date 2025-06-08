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
- SteelSeries device with OLED display (Apex Pro, Rival 700/710, etc.)

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
pyinstaller --onefile --windowed --name "NovaProXController" --icon="icon.ico" --add-data "ascii_arts;ascii_arts" --collect-all customtkinter main.py
```

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

## Author

Created by Zimcim

## License

This project is licensed under the MIT License.
