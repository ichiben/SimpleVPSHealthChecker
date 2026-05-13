# Simple VPS Health Checker

A lightweight, terminal-based Python application to monitor the health of your Virtual Private Servers (VPS) or any remote endpoints. It features a beautiful interactive CLI and runs a background daemon that periodically checks your configured hosts/ports, sending a Telegram alert if a server becomes unreachable.

## Features

- **Rich CLI Interface**: Beautiful, intuitive, interactive text-based menu for easy configuration.
- **Background Daemon**: Runs quietly in the background without needing to keep the terminal open.
- **Telegram Alerts**: Get notified instantly on your mobile device when a server drops offline.
- **Customizable Checks**: Define how often to check and how many consecutive times a check must fail before triggering an alert (prevents false alarms).
- **Lightweight Config**: Uses a simple `config.yaml` file to store targets and secrets.

## Prerequisites

- Python 3.7+
- A Telegram Bot Token (Create one via [BotFather](https://t.me/botfather) on Telegram)
- Your Telegram Chat ID

## Installation

1. Clone this repository or download the source code:
   ```bash
   git clone https://github.com/ichiben/SimpleVPSHealthChecker.git
   cd SimpleVPSHealthChecker
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Start the main interactive menu:
```bash
python main.py
```

From the menu, you can:
1. **Configure Telegram Bot**: Enter your Bot Token and your personal Chat ID so the app knows where to send alerts.
2. **Add Target**: Add a new VPS by specifying its hostname/IP, the port to check (e.g., 80 for HTTP, 22 for SSH), the check interval in seconds, and the maximum number of retries before alerting.
3. **Start Monitor**: This will launch the background monitoring process. You can safely close your terminal once it is running.
4. **Stop Monitor**: Terminates the background daemon.

## How It Works

- The `main.py` script acts as your control panel.
- When you start the monitor, it spawns `monitor.py` as a detached background process.
- The daemon reads from `config.yaml` and performs standard TCP socket connections to your targets.
- All events (online, offline, retries) are logged to `vps_health.log` in the same directory.
- If a target fails the connection check consecutively for the number of `max_retries` you defined, it triggers `notifier.py` to send a Telegram message via the official API.

## License

This project is licensed under the MIT License.
