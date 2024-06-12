import subprocess
import signal
import sys
import os
from time import sleep
from scripts.common import logger, config

logger.name = __file__
if os.name == "nt":
    VENV_PYTHON_PATH = "venv\\Scripts\\python.exe"
elif os.name == "posix":
    VENV_PYTHON_PATH = "venv/bin/python"
else:
    VENV_PYTHON_PATH = "venv/bin/python"
    logger.warning("OS is neither Unix-like nor Windows. Defaulting to Unix-like behavior.")

processes = []
for identity, listener in config["listeners"].items():
    if not listener["enable"]:
        continue

    logger.info(f"Running {identity} module")
    processes.append(subprocess.Popen([VENV_PYTHON_PATH, listener["module_path"]]))
    sleep(3)

processes.append(subprocess.Popen([VENV_PYTHON_PATH, "scripts/Detector.py"]))


def signal_handler(sig, frame):
    logger.warning(f"Recieved {sig} signal. Stopping Gracefully..")
    for process in processes:
        process.terminate()
    sleep(2)  # give time for other scripts to do their thing before exiting (avoids race condition.. i think) 
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


while True:
    sleep(10) #  Should terminate all processes within 10 seconds of receiving a SIGINT signal