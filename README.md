# System Check 🖥️📡

A lightweight Python-based system and network monitoring script for Linux systems, designed to run in the background and alert you when connectivity or resource thresholds are triggered.

---

## 🚀 Features

- Full system health monitoring (CPU, RAM, Disk, Network)
- Automatic email alerts for failures
- Detailed logging of system events and statuses
- Fully configurable via `config.ini`
- Cross-platform: Linux, Windows, macOS


---

## 📁 Project Structure

```plaintext
system-check/
├── monitor.py          # Main system monitor script
├── config.ini          # Configuration file (thresholds, email settings, ping targets)
├── last_alert.ini      # Tracks last sent alerts to avoid spamming
├── logs/
│   └── monitor.log     # Log file for system status, warnings, and errors
├── .gitignore          # Git ignore rules (logs, temp files, etc.)
└── README.md           # Project overview and setup instructions
```

## ⚙️ Usage

1. Create and activate a virtual environment:

    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

2. Install required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

    *(Note: If you don't have a `requirements.txt` yet, it would just include `psutil`.)*

3. Configure your settings in `config.ini`:

    ```ini
    [network]
    ping_target = 8.8.8.8

    [email]
    smtp = smtp.gmail.com
    sender = youremail@example.com
    app_password = yourapppassword
    recipient = recipient@example.com

    [thresholds]
    cpu = 90
    ram = 90
    disk = 90

    [alerts]
    threshold = 3600  # Minimum seconds between repeated alerts
    ```

4. Run the monitor:

    ```bash
    python monitor.py
    ```

## 📓 Notes

Make sure the logs/ directory exists. Use a .gitkeep file if you want Git to track empty folders.

You can hook this script into a systemd timer or cron job to automate checks.

## 🔒 Security Considerations

Always validate and sanitize dynamic input if you extend this script.

If using email alerts, use app-specific passwords (not your main password) when possible.

## 📬 Future Features

Dynamic mount discovery for Disk Usage

RTT/latency analysis and alerting

Expand email alerts to include basic system summary reports.
