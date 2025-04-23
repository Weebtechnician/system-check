import configparser
import os
import time

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
    retry_count = 0
    max_retry = 5

    while retry_count < max_retry:
        result = subprocess.run(
            ["ping", "-c", "1", f"{config['network']['ping_target']}"],
            capture_output=True,
            text=True,
        )

        logger.info("NETWORK STATUS")
        logger.debug(f"Command: {' '.join(result.args)}")
        logger.debug(f"Status code: {result.returncode}")

        if result.returncode == 0:
            # Grab important line from stdout if it exists
            stdout = None

            for line in result.stdout.splitlines():
                if "bytes from" in line:
                    stdout = line
                    break

            if stdout is None:
                stdout = result.stdout.strip()

            logger.debug(stdout)
            break

        logger.error(f"Ping failed: {result.stderr.strip()}")
        logger.info(f"Retrying ping. Attempt {retry_count + 1}/{max_retry}.")
        time.sleep(5 + retry_count * 2)
        retry_count += 1
    else:
        logger.error("Max retries reached. Sending alert.")


# --------------------- SYSTEM ---------------------
check_connection()
