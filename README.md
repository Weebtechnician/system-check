# System Check 🖥️📡

A lightweight Python-based system and network monitoring script for Linux systems, designed to run in the background and alert you when connectivity or resource thresholds are triggered.

---

## 🚀 Features

- 🧠 Monitors internet connectivity with ping
- 🧾 Logs status codes, output, and errors to `logs/monitor.log`
- 🛡️ Handles unreachable networks gracefully
- 🧰 Configurable through `config.ini`
- 🔁 Designed to run on a schedule with `systemd` or `cron`

---

## 📁 Project Structure

```plaintext
system-check/
├── monitor.py          # Main script
├── config.ini          # Configuration file (target IP, thresholds, etc.)
├── logs/
│   └── monitor.log     # Log output (auto-generated)
├── .gitignore          # Git rules
└── README.md           # You're here
```
## ⚙️ Usage

1. Install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Configure your target in config.ini:

```bash
[network]
ping_target = 8.8.8.8
```

3. Run the script:

``` bash
python monitor.py
```


## 📓 Notes

    Create the logs/ directory or include a .gitkeep to track it with Git.

    You can hook this script into a systemd timer or cron job to automate checks.

## 🔒 Security Considerations

    Always validate and sanitize dynamic input if you extend this script.

## 📬 Future Features

    System resource monitoring (CPU, disk, memory)

    Email alerts via Gmail SMTP

    Retry logic for flaky connections

    RTT/latency analysis and alerting
