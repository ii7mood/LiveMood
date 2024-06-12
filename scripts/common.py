import logging
import signal
import json
from os import getcwd
from datetime import datetime
from functools import partial


def signal_handler(signum: signal.SIGINT, frame, sockets: dict) -> None:
    for identity, sock in sockets.items():
        sock.close()
        logger.warning(f"{identity} sock closed.")

def register_signal_handler(sock, identity : str) -> None:
    global COUNT
    global SOCKETS
    
    logger.info(f'Registered sock: {sock.getsockname()} || {identity}')
    SOCKETS[f'{identity}-{COUNT}'] = sock
    COUNT += 1  # Detecter will open multiple sockets, having a unique identifier here is crucial

SOCKETS = {}
COUNT = 0


handler_with_args = partial(signal_handler, sockets=SOCKETS)
signal.signal(signal.SIGTERM, handler_with_args)


def initialize_logger_and_config() -> None:
    global logger, config
    
    if logger is None:
        log_filename = f'{cwd}/files/{datetime.today().strftime("%Y-%m-%d")}.log' 
        #  ^ if you start exactly at 11:59:58 PM this will spawn two log files making the logs annoying to read and is technically a bug :)
        logging.basicConfig(
            filename=log_filename,
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        logger = logging.getLogger('commonLogger')

        with open(f'{cwd}/files/config.json', 'r') as configfile:
            config = json.load(configfile)

logger = None
config = None
parent_path = getcwd().replace('/scripts', '')
cwd = getcwd()

initialize_logger_and_config()
