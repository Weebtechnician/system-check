import configparser
import os
import time
import smtplib
import datetime as dt
import platform
import psutil
import subprocess
import logging

DEFAULT_TIMESTAMP = "1970-01-01 00:00:00"

config = configparser.ConfigParser()
config.read("config.ini")

last_alert = configparser.ConfigParser()
last_alert.read("last_alert.ini")

logging.basicConfig(
    filename="logs/monitor.log",
    encoding="utf-8",
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
)

logger = logging.getLogger("monitor")

# Ensure logs folder exists
if not os.path.exists("logs"):
    os.makedirs("logs", exist_ok=True)


# --------------------- ALERTS ---------------------


def send_alert(error, subject):
    with smtplib.SMTP(f"{config['email']['smtp']}", 587) as connection:
        connection.starttls()
        connection.login(
            user=f"{config['email']['sender']}",
            password=f"{config['email']['app_password']}",
        )
        connection.sendmail(
            from_addr=config["email"]["sender"],
            to_addrs=config["email"]["recipient"],
            msg=f"Subject:{subject}\n\nThis is an automated message from your Pi monitor.\n\nPi has encountered an error:\n\n{error}",
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
        logger.info(
            f"Alert previously sent on {last_alert['alerts'][f'{alert_type}']}. Alert not resent."
        )
        return True


# --------------------- NETWORK CHECK ---------------------


def check_connection():
    retry_count = 0
    max_retry = 5

    while retry_count < max_retry:
        if platform.system() == "Windows":
            command = ["ping", "-n", "1", f"{config['network']['ping_target']}"]
        else:
            command = ["ping", "-c", "1", f"{config['network']['ping_target']}"]
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
        )

        logger.info("CHECKING NETWORK...")
        logger.debug(f"Command: {' '.join(result.args)}")
        logger.debug(f"Status code: {result.returncode}")

        if result.returncode == 0:
            # Grab important line from stdout if it exists
            stdout = None

            for line in result.stdout.splitlines():
                if "bytes from" or "Reply from" in line:
                    stdout = line
                    break

            if stdout is None:
                stdout = result.stdout.strip()

            logger.debug(stdout)
            logger.info("Network OK")
            break

        logger.error(f"Ping failed: {result.stderr.strip()}")
        logger.info(f"Retrying ping. Attempt {retry_count + 1}/{max_retry}.")
        time.sleep(5 + retry_count * 2)
        retry_count += 1
    else:
        if not check_alerts("network"):
            logger.error("Max retries reached. Sending alert.")
            send_alert(result.stderr, "Pi network check failed.")


# --------------------- SYSTEM CHECKS ---------------------
def check_system():
    # CPU
    logger.info("CHECKING CPU USAGE...")
    cpu_percent = psutil.cpu_percent(interval=None)
    if cpu_percent > float(config["thresholds"]["cpu"]):
        logger.warning("CPU usage over threshold. Sending alert.")
        get_top_processes("cpu")
    else:
        logger.info("CPU OK")
    # MEMORY
    logger.info("CHECKING MEMORY USAGE...")
    ram_percent = psutil.virtual_memory()[2]
    if ram_percent > float(config["thresholds"]["ram"]):
        logger.warning("RAM percent over threshold. Sending alert.")
        get_top_processes("memory")

    else:
        logger.info("MEMORY OK")
    # DISK
    check_disk_space()


def get_top_processes(metric):
    process_list = []
    for proc in psutil.process_iter():
        try:
            proc.cpu_percent(interval=1)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    time.sleep(1)

    for proc in psutil.process_iter():
        try:
            with proc.oneshot():
                info = {
                    "pid": proc.pid,
                    "name": proc.name(),
                    "username": proc.username(),
                }

                if metric == "cpu":
                    info["value"] = proc.cpu_percent(interval=1)
                elif metric == "memory":
                    info["value"] = proc.memory_info().rss / (1024 * 1024)
                else:
                    continue

                process_list.append(info)

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    format_processes(process_list, metric)


def format_processes(processes, metric, top_n=5):
    top_processes = sorted(processes, key=lambda p: p["value"], reverse=True)[:top_n]
    formatted_processes = []

    for process in top_processes:
        name_field = f"{process['username']}@{process['name']}".ljust(25)
        pid_field = f"(PID {process['pid']})".rjust(12)

        if metric == "cpu":
            unit = "%"
        elif metric == "memory":
            unit = "MB"
        else:
            unit = ""

        value_field = f"{process['value']:>6.2f} {unit}"

        line = f"{name_field} {pid_field} : {value_field}"

        formatted_processes.append(line)
    top_processes_str = "\n".join(str(process) for process in formatted_processes)
    logger.debug(f"Top {metric.upper()} consuming processes:\n{top_processes_str}")
    if not check_alerts(f"{metric}"):
        send_alert(
            f"{metric} over threshold.\n\n{top_processes_str}",
            f"{metric.capitalize()} over threshold.",
        )
    else:
        logger.info("Alert already sent.")


def check_disk_space():
    for mount in get_mounts():
        try:
            usage = psutil.disk_usage(mount)
            if usage.percent > float(config["thresholds"]["disk"]):
                logger.warning(
                    f"Disk usage past threshold of {config['thresholds']['disk']} on {mount}. Current usage is {usage.percent}"
                )
                if not check_alerts("disk"):
                    send_alert(
                        f"'{mount}' mount over threshold.\n\nCurrent usage is {usage.percent}",
                        f"{mount} over threshold.",
                    )
                else:
                    logger.info("Alert already sent.")
            else:
                logger.info(f"'{mount}' OK. USAGE: {usage.percent}")
        except PermissionError:
            logger.warning(f"Permission denied when checking {mount}. Skipping.")


def get_mounts():
    # research psutil.disk_partitions to maybe make this more dynamic, current function is hardcoded
    system = platform.system()

    if system == "Linux":
        return ["/", "/home", "/var", "/boot"]
    elif system == "Windows":
        # Add more drives here if needed
        return ["C:\\"]
    elif system == "Darwin":
        # Add more drives here if needed
        return ["/"]
    else:
        return []


check_connection()
check_system()
