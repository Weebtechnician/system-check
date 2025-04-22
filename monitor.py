import configparser
# import psutil
import os
import subprocess

config = configparser.ConfigParser()
config.read("config.ini")


# --------------------- NETWORK CHECK ---------------------

def check_connection():
    global config

    result = subprocess.run(["ping", "-c", "1", f"{config['network']['ping_target']}"], capture_output=True, text=True)

    if result.returncode != 0:
        pass

# --------------------- SYSTEM ---------------------
check_connection()