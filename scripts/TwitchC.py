import requests
from common import logger, config


# FUNCTION BELOW IS NEEDED FOR INIT BUT I WILL RE-WRITE IT LATER
def oAuthreinit() -> None:
    return None
#     config.read(config_path)
#     OAuth = config['TWITCH']
#     newAuthBearer = requests.post(f"https://id.twitch.tv/oauth2/token?client_id={OAuth['client_id']}&client_secret={OAuth['client_secret']}&grant_type=client_credentials").json();

#     try:
#         OAuth['access_token'] = newAuthBearer['access_token']
#     except KeyError:
#         if newAuthBearer['status'] == 400:
#             print("Twitch oauth details incorrectly entered.")
#             exit(1)

    
#     with open(config_path, 'w') as configfile:
#         config.write(configfile)



def getProfile(name):
    OAuth = config['listeners']["twitch_opts"]

    headers = {
        'Client-ID': OAuth['client_id'],
        'Authorization': 'Bearer ' + OAuth['access_token']}


    profile_json = requests.get(f'https://api.twitch.tv/helix/users?login={name}', headers=headers)

    if profile_json.status_code == 401: # Twitch tokens expire after some time, in which case we can re-generate one.
        oAuthreinit()
        getProfile(name)

    profile = profile_json.json();
    return profile


def getStream(name):
    OAuth = config['listeners']["twitch_opts"]

    headers = {
        'Client-ID': OAuth['client_id'],
        'Authorization': 'Bearer ' + OAuth['access_token']}

    stream_json = requests.get(f'https://api.twitch.tv/helix/streams?user_login={name}', headers=headers)

    if stream_json.status_code == 401: # Twitch tokens expire after some time, in which case we can re-generate one.
        oAuthreinit()
        getStream(name)

    stream = stream_json.json();
    return stream 