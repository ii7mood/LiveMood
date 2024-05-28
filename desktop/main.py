import socket
import pickle
from os import getcwd
from sys import path
from plyer import notification

parent_path = getcwd().replace('/desktop', '')
path.append(parent_path)

from scripts.common import logger, config, register_signal_handler
logger.name = __file__

serverSocket = (config["listeners"]["desktop"]["host"], config["listeners"]["desktop"]["port"])
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(serverSocket)
server.listen(1)
register_signal_handler(server, "desktop")

HOST = config['listeners']['desktop']['host']
PORT = config['listeners']['desktop']['port']


def start_listening(conn : socket.socket.accept = None):
    """
    On the first iteration we create a connection and pass it around to avoid re-establishing the connection unless an error occurs.
    If an error happens we re-create a connection which Detector.py will switch to while in it's handling of the broken connection.
    """
    logger.info(f"DESKTOP currently listening on {HOST}:{PORT}")
    if conn == None:
        conn, addr = server.accept()

    try:
        packets = []
        while True:
            packet = conn.recv(4096)
            if not packet or packet[-3:] == b"END":
                packets.append(packet[:-3])
                break
            packets.append(packet)
        data = pickle.loads(b"".join(packets))

    except socket.error as e:
        logger.warning(e)
        return None, None # Should create a new connection as None is returned in place of a broken connection

    except EOFError:
        logger.warning("DESKTOP connection shutdown. Will attempt to re-establish a connection")
        return None, None

    except Exception as e:
        logger.warning(e) # This will help catch exceptions that are not already handled and log it.

    return data, conn

try:
    conn = None
    while True:
        info_dict, conn = start_listening(conn)

        if conn == None: # Connection error, nothing to do except hope for the best.
            continue

        elif info_dict == None: # An error occured with the data received. Lets just say we're done so that Detector.py does not have to timeout.
            conn.sendall(b"DONE")
            continue

        if info_dict['live_status'] == "is_live":
            
            notification.notify(
                title = "liveMood - LIVE",
                message = f"{info_dict['uploader']} is now live!",
                app_icon = f'{parent_path}/{info_dict["avatar_path"]}',
                timeout = 5 #  seconds
            )

        # Send acknowledgement to the server
        conn.sendall(b"DONE")

except Exception as e:
    logger.error(e)
    exit(1)