import socket
import pickle
import sys
from time import sleep
from common import logger, config, register_signal_handler
from streamers import *

LISTENERS = config["listeners"]
logger.name = __file__


def connect(listener : dict, identity: str) -> tuple:
    """
    Returns:
        on success: tuple(socket.AF_INET, socket.SOCK_STREAM)
        on failure: None
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.connect((listener["host"], listener["port"]))
        register_signal_handler(server, identity)
        logger.info(f"Connection to {identity} socket established.")
        return server

    except ConnectionRefusedError:
        logger.warning(f"Failed to establish a connection to {identity} socket. Connection Refused.")
        return None
    
    except ValueError:
        logger.warning("Incorrect type specified. Is the port an integer?")


def send_data(data : dict, servers: dict) -> bool:
    successful = True
    for server in SERVERS.items():
        name = server[0]
        connection = server[1]

        try:
            connection.sendall(pickle.dumps(data) + b"END")
            reply = connection.recv(1024)

            if reply != b"DONE":
                logger.warning(f"Unexpected response from {name}, shutting connection down.")
                connection.close()
                # not removing from servers dict as the listener *could* re-establish a connection on its side
            
        except TimeoutError:
            logger.warning(f"The {name} Connection timed. Moving on.")
            successful = False
        except ConnectionAbortedError:
            logger.warning(f"Failed to send data to {name}, shutting connection down.")
            successful = False
        except socket.error:
            logger.warning(f"Failed to send data to {name}. Socket Error, shutting connection down.")
            successful = False
    return successful
        

def process_data(STREAMERS_DATA : list, SERVERS : dict) -> bool:
    for streamerData in STREAMERS_DATA:
        change_in_activity = streamerData["live_status"] != streamerData["recorded_live_status"]

        if not change_in_activity:
            continue

        logger.info(f'Change in activity with {streamerData["uploader_name"]} | ' 
                    f'Before: {streamerData["recorded_live_status"]} | '
                    f'After: {streamerData["live_status"]} | ')
        sleep(1) # Sometimes Detector.py sends data before listener can process it. So wait a sec.

        if streamerData["live_status"] == "not_live":
            updateStreamerActivity(streamerData['uploader_url'], streamerData['live_status'])
            continue

        if not sendData(streamerData, SERVERS): 
            #  if an error occured with *any* listener then the table will not update the streamers' status, will attempt re-send next iteration.
            continue
        
        updateStreamerActivity(streamerData['uploader_url'], streamerData['live_status'])


SERVERS = {}
for identity, listener in LISTENERS.items():
    if not listener["enable"]:
        continue

    server = connect(listener, identity)
    if server: #  In case we get a None return
        SERVERS[identity] = server


def main():
    ERRORS = 0
    while True:
        try:
            streamersData = getStreamersData()
            process_data(streamersData, SERVERS)
            logger.info("Sleeping for 5 minutes")
            sleep(300)
            ERRORS = 0

        except Exception as e:
            logger.error(f"Major Error occured during processing. Details: {str(e)}. Error Count: {ERRORS}")
            if ERRORS >= 5:
                logger.error("Detector.py failed multiple times in a row. Will Exit.")
                sys.exit(1)
            ERRORS += 1

main()