import requests
from sys import exit as SysExit
from common import logger, config, parent_path
import json


def oAuthreinit() -> None:
    logger.warning("Twitch Acess Token failed to authenticate. Requesting a new token..")

    oAuth = config["twitch_opts"]
    newAuthBearer = requests.post(f"https://id.twitch.tv/oauth2/token?client_id={oAuth['client_id']}&client_secret={oAuth['client_secret']}&grant_type=client_credentials").json();

    try:
        oAuth['access_token'] = newAuthBearer['access_token']
    except KeyError:
        if newAuthBearer['status'] == 400:
            print("Twitch oAuth details incorrectly entered.")
            SysExit(1)

    with open(parent_path+'/files/config.json', 'w') as configfile:
        json.dump(config, configfile, indent=2)


def getProfile(name) -> dict:
    oAuth = config["twitch_opts"]

    headers = {
        'Client-ID': oAuth['client_id'],
        'Authorization': 'Bearer ' + oAuth['access_token']}


    profile_json = requests.get(f'https://api.twitch.tv/helix/users?login={name}', headers=headers)

    if profile_json.status_code == 401: # Twitch tokens expire after some time, in which case we can re-generate one.
        oAuthreinit()
        return getProfile(name)

    profile = profile_json.json();
    return profile


def getStream(name) -> dict:
    oAuth = config["twitch_opts"]

    headers = {
        'Client-ID': oAuth['client_id'],
        'Authorization': 'Bearer ' + oAuth['access_token']}

    stream_json = requests.get(f'https://api.twitch.tv/helix/streams?user_login={name}', headers=headers)

    if stream_json.status_code == 401: # Twitch tokens expire after some time, in which case we can re-generate one.
        oAuthreinit()
        return getStream(name)

    stream = stream_json.json();
    return stream 