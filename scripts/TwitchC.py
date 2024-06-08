import requests
from sys import exit as SysExit
from common import logger, config, parent_path
import json

logger.name = __file__

def oAuthreinit() -> None:
    logger.warning("Twitch Access Token failed to authenticate. Requesting a new token..")

    oAuth = config["twitch_opts"]
    newAuthBearer = requests.post(f"https://id.twitch.tv/oauth2/token?client_id={oAuth['client_id']}&client_secret={oAuth['client_secret']}&grant_type=client_credentials").json();

    try:
        oAuth['access_token'] = newAuthBearer['access_token']
    except KeyError:
        if newAuthBearer['status'] == 400:
            logger.warning("Twitch oAuth details incorrectly entered.")
            SysExit(1)

    with open(parent_path+'/files/config.json', 'w') as configfile:
        json.dump(config, configfile, indent=2)


def getProfile(name, _attempts = 0) -> dict:
    oAuth = config["twitch_opts"]

    headers = {
        'Client-ID': oAuth['client_id'],
        'Authorization': 'Bearer ' + oAuth['access_token']}


    profile_json = requests.get(f'https://api.twitch.tv/helix/users?login={name}', headers=headers)

    if profile_json.status_code == 401: # Twitch tokens expire after some time, in which case we can re-generate one.
        if _attempts >= 3:
            logger.error("These Twitch Credentials cannot be used to authorise. Exiting..")
            SysExit(1)
        oAuthreinit()
        return getProfile(name, _attempts+1)

    profile = profile_json.json();
    return profile


def getStream(name, _attempts = 0) -> dict:
    oAuth = config["twitch_opts"]

    headers = {
        'Client-ID': oAuth['client_id'],
        'Authorization': 'Bearer ' + oAuth['access_token']}

    stream_json = requests.get(f'https://api.twitch.tv/helix/streams?user_login={name}', headers=headers)

    if stream_json.status_code == 401: # Twitch tokens expire after some time, in which case we can re-generate one.
        if _attempts >= 3:
            logger.error("These Twitch Credentials cannot be used to authorise. Exiting..")
            SysExit(1)
        oAuthreinit()
        return getStream(name, _attempts+1)

    stream = stream_json.json();
    return stream 