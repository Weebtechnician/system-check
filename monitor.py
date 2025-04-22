import configparser
import os

# import psutil
import subprocess
import logging

config = configparser.ConfigParser()
config.read("config.ini")

logger = logging.getLogger("monitor")

# Ensure logs folder exists
if not os.path.exists("logs"):
    os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    filename="logs/monitor.log",
    encoding="utf-8",
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
)

# --------------------- NETWORK CHECK ---------------------


def check_connection():
    global config

    result = subprocess.run(
        ["ping", "-c", "1", f"{config['network']['ping_target']}"],
        capture_output=True,
        text=True,
    )
    logger.info("NETWORK STATUS")
    logger.debug(f"Command: {' '.join(result.args)}")

    stdout = None

    for line in result.stdout.splitlines():
        if "bytes from" in line:
            stdout = line
            break

    if stdout is None:
        stdout = result.stdout.strip()

    logger.debug(stdout)
    logger.debug(f"Status code: {result.returncode}")

    if result.returncode != 0:
        logger.error(f"Ping failed: {result.stderr.strip()}")


# --------------------- SYSTEM ---------------------
check_connection()
