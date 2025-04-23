import configparser
import os
import time
import smtplib
import datetime as dt

# import psutil
import subprocess
import logging

DEFAULT_TIMESTAMP = "1970-01-01 00:00:00"

config = configparser.ConfigParser()
config.read("config.ini")

last_alert = configparser.ConfigParser()
last_alert.read("last_alert.ini")

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

# --------------------- ALERTS ---------------------


def send_alert(alert, subject):
    with smtplib.SMTP(f"{config['email']['smtp']}", 587) as connection:
        connection.starttls()
        connection.login(
            user=f"{config['email']['sender']}",
            password=f"{config['email']['app_password']}",
        )
        connection.sendmail(
            from_addr=config["email"]["sender"],
            to_addrs=config["email"]["recipient"],
            msg=f"Subject:{subject}\n\nThis is an automated message from your Pi monitor.\n\nPi has encountered an error:\n\n{alert}",
        )


def check_alerts(alert_type):
    if "alerts" not in last_alert:
        last_alert["alerts"] = {}
    if alert_type not in last_alert["alerts"]:
        last_alert["alerts"][alert_type] = DEFAULT_TIMESTAMP

    last_time = dt.datetime.strptime(
        last_alert["alerts"][alert_type], "%Y-%m-%d %H:%M:%S"
    )
    elapsed = (dt.datetime.now() - last_time).total_seconds()

    if elapsed > float(config["alerts"]["threshold"]):
        last_alert["alerts"][alert_type] = dt.datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        with open("last_alert.ini", "w") as alert_file:
            last_alert.write(alert_file)
        return False
    else:
        return True


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
        alert_sent = check_alerts("network")

        if alert_sent:
            logger.info(
                f"Alert previously sent on {last_alert['alerts']['network']}. Alert not resent."
            )
        else:
            logger.error("Max retries reached. Sending alert.")
            send_alert(result.stderr, "Pi network check failed.")


# --------------------- SYSTEM CHECKS ---------------------


check_connection()
