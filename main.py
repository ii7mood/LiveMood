import subprocess
import signal
from time import sleep
from scripts.common import logger, config
from sys import exit as SysExit

logger.name = __file__

processes = []
for identity, listener in config["listeners"].items():
    if not listener["enable"]:
        continue

    logger.info(f"Running {identity} module")
    processes.append(subprocess.Popen([config["python_executable"], listener["module_path"]]))
    sleep(3)

processes.append(subprocess.Popen([config["python_executable"], "scripts/Detector.py"]))


def signal_handler(sig, frame):
    logger.warning(f"Recieved {sig} signal. Stopping Gracefully..")
    for process in processes:
        process.terminate()
    sleep(2)  # give time for other scripts to do their thing before exiting (avoids race condition) 
    SysExit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


while True:
    sleep(10) #  Should terminate all processes within 10 seconds of receiving a SIGINT signal