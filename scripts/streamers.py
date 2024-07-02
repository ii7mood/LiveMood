import yt_dlp
import requests
import sqlite3
import TwitchC
import datetime
import sys
import os
from time import sleep
from bs4 import BeautifulSoup
from common import logger, config, parent_path
from streamers_vars import avatars, yt_dlp_args, createTable, default_twitch_icon_path, default_twitch_icon_url, default_youtube_icon_path, default_youtube_icon_url

sys.path.append(parent_path)
logger.name = __file__

TEST_CASES = [
    ['lofigirl', 'https://www.youtube.com/@LofiGirl', 'not_live'],
    ['hamood', 'https://www.youtube.com/@hamood1884', 'not_live'],
    ['NevaGonnaGiveYouUp', 'https://www.youtube.com/channel/UCE9JOW3cOtAh_tvQixnTfZQ', 'not_live'],
    ['LeekBeats', 'https://www.twitch.tv/leekbeats', 'not_live'],
    ['siso_2', 'https://www.twitch.tv/siso_2', 'not_live']
]

# TO-DO: Test if Twitch scraper still works

DB = sqlite3.connect('files/Streamers.db') # establish a connection to Streamers.db holding various data about each streamer
CURSOR = DB.cursor()

if os.path.getsize('files/Streamers.db') == 0: # assume file was just created
    CURSOR.execute(createTable)
    DB.commit()


def _fetch_twitch_stream(uploader_name: str) -> dict:
    """
    Returns a dict containing 'viewer_count' and 'game_name' keys.
    Uses Twitch API to request stream data then returns those two selected fields.
    """
    if config['twitch_opts']['scrape'] == "1":
        return {'viewer_count': 0, 'game_name': 'Unknown'}  # Have not implemented a way to scrape stream data from Twitch
    
    try:
        stream = TwitchC.getStream(uploader_name)
        return stream['data'][0]
    except Exception as e:
        logger.warning(f"Failed to retrieve Twitch Stream data. \n{e}\n{stream}")
        return {'viewer_count': 0, 'game_name': 'Unknown'}


def _fetch_twitch_profile(uploader_name: str) -> dict:
    """
    Returns a string which holds the URL to the avatar of the streamer.
    Uses Twitch API to request profile data then return avatar_url as a specific value.
    """
    if config['twitch_opts']['scrape'] == "1":
        response = requests.get(uploader_url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Method 1: Look for the <meta> tag with property="og:image"
            meta_avatar = soup.find('meta', property='og:image')
            if meta_avatar:
                return meta_avatar['content']
            
            # Method 2: Look for the <img> tag with the class "tw-image-avatar"
            img_avatar = soup.find('img', class_='tw-image-avatar')
            if img_avatar:
                return img_avatar['src']
            
            # Method 3: Look for the <figure> tag with the class "channel-header__avatar"
            figure_avatar = soup.find('figure', class_='channel-header__avatar')
            if figure_avatar:
                img = figure_avatar.find('img')
                if img:
                    return img['src']
                else:
                    logger.info("soup.find returned None, Twitch.TV probably changed website structure. Using default Twitch icon.")
                    return default_twitch_icon_url
        else:
            logger.warning("Could not parse Twitch HTML structure. Fallbacking to default avatar.")
            return default_twitch_icon_url

    return TwitchC.getProfile(uploader_name)['data'][0]['profile_image_url']


def _fetch_avatar(uploader_name: str, uploader_url: str) -> tuple[str, str]:
    '''
    Returns a tuple holding the URL and path to the avatar.
    Attempts to cache both if a locally stored image does not exist.
    '''

    for char in r'*"/\<>:|?':  # A list of invalid characters on windows, also '/' which is invalid on Linux
        uploader_name = uploader_name.replace(char, '')

    cachepath = f'files/cache/{uploader_name.replace("/", "")}'
    url = None
    image = None

    if "youtube" in uploader_url:
        try:
            with yt_dlp.YoutubeDL(yt_dlp_args) as ytd:
                info_dict = ytd.extract_info(uploader_url)
                for thumbnail in info_dict['thumbnails']:
                    if thumbnail['id'] == "avatar_uncropped":
                        url = thumbnail['url']
                        image = requests.get(url)

        except Exception as e:
            logger.warning(f"Well, something went wrong. Default avatar path has been returned (YT). {e}")
            return (default_youtube_icon_url, default_youtube_icon_path)
        
    elif "twitch" in uploader_url:
        url = _fetch_twitch_profile(uploader_name)  # name is misleading as it only returns avatar URL, it might do more in the future tho
        if url == default_twitch_icon_url:
            return (default_twitch_icon_url, default_twitch_icon_path)
        image = requests.get(url)
    
    with open(cachepath, "wb+") as f:
        f.write(image.content)
    
    return (url, os.path.normpath(cachepath))



# Random errors refer to connection errors or anything that would be solved with a simple function re-call.
# Systematic errors are more complex and require some specific workaround.
def _extract_data(url: str, yt_dlp_args: dict) -> dict:
    """
    Returns the dictionary returned by yt_dlp on a successful call, on random errors it'll recursively call until it succeeds
    return types:
        on success: dict
        on systematic errors: None
    """
    with yt_dlp.YoutubeDL(yt_dlp_args) as ytdlp:
        try:
            info_dict = ytdlp.extract_info(url)
            return info_dict
        
        except yt_dlp.DownloadError as e:
            if 'not currently live' in str(e):
                return None
            
            elif "tab page" in str(e):
                logger.warning(f"Random Error: YT_FAILED_LOADING\n{str(e)}")
                sleep(15)
                return _extract_data(url, yt_dlp_args)

            elif "failure in name resolution" in str(e):
                logger.warning(f"Random Error: No Internet Connection. Attempting Extraction in 5 mins\n{str(e)}")
                sleep(300)
                return _extract_data(url, yt_dlp_args)
            
            elif "JSON metadata" in str(e):
                logger.warning(f"Random Error: Failed to download JSON metadata\n{str(e)}")
                sleep(15)
                return _extract_data(url, yt_dlp_args)

            else:
                logger.warning(f"Systematic Error: \n{str(e)}")
                return None


def getStreamerData(nickname: str, uploader_url: str, recorded_activity: str) -> dict:
    """
    Returns a dictionary containing data of a singular streamer.
    args:
        nickname: str
        url: str
        recorded_activity: str ('not_live', 'is_live', 'is_upcoming')
    """

    data = {}
    url = uploader_url
    logger.info(f"Retrieving {nickname}'s current status...")

    if "youtube" in uploader_url:
        url = url + '/live'
        platform = "youtube"
    else:
        platform = "twitch"
    
    if config['path_to_cookies']:
        yt_dlp_args['cookies'] = config['path_to_cookies']
    
    info_dict = _extract_data(url, yt_dlp_args)
        
    # At minimum the data dictionary should include: the uploader URL, current status, recorded status, and nickname.
    if info_dict is None:
        data['uploader_name'] = nickname
        data['live_status'] = 'not_live'
        data['recorded_live_status'] = recorded_activity
        data['uploader_url'] = uploader_url
        return data
        
    if info_dict['live_status'] == recorded_activity:  # Avoid processing already-known streams
        data['uploader_name'] = nickname
        data['live_status'] = recorded_activity
        data['recorded_live_status'] = recorded_activity
        data['uploader_url'] = uploader_url
        return data
    
    #  At this point we know that there is indeed a new stream
    logger.info(f"Stream Found. Status: {info_dict['live_status']}")

    #  Nested if-statements :)
    if info_dict['live_status'] == "is_upcoming":
        if info_dict['release_timestamp'] == None:
            data['release_timestamp'] = "in_moments"  # YT stops giving a precise value when nearing the time of a scheduled stream
        
        else:
            #  Streams scheduled to start in >24h will not be recorded
            hours_until_stream = (info_dict['release_timestamp'] - datetime.datetime.now().timestamp()) / 3600
            if hours_until_stream > 24:
                data['uploader_name'] = nickname
                data['live_status'] = 'not_live'
                data['recorded_live_status'] = recorded_activity
                data['uploader_url'] = uploader_url
                return data
            data['release_timestamp'] = info_dict['release_timestamp']
            
    
    # platform-specific data
    if platform == "twitch":
        tvData = _fetch_twitch_stream(info_dict['display_id'])
        data['viewer_count'] = tvData['viewer_count']
        data['category_name'] = tvData['game_name']
    else:
        data['viewer_count'] = info_dict['concurrent_view_count']

    data['live_status'] = info_dict['live_status']
    data['uploader'] = info_dict['uploader']
    data['thumbnail'] = info_dict['thumbnail']
    data['fulltitle'] = info_dict['fulltitle']
    data['recorded_live_status'] = recorded_activity
    data['platform'] = platform
    data['uploader_name'] = nickname
    data['uploader_url'] = uploader_url
    data['stream_url'] = url
    data['avatar_url'], data['avatar_path'] = _fetch_avatar(info_dict['display_id'], data['uploader_url'])

    return data


def updateStreamerActivity(url: str, activity: str) -> None:
    """
    Update the recorded_activity field of a streamer, using their URL as the identifier.
    """
    CURSOR.execute("UPDATE streamers SET RECORDED_ACTIVITY = ? WHERE URL = ?", (activity, url))
    DB.commit()


def getStreamersData() -> list[dict]:
    """
    Returns a list of dictionaries holding data of their corresponding streamers.
    """
    CURSOR.execute("SELECT * FROM streamers")
    rawStreamersData: list[list[str, str, str]] = CURSOR.fetchall()
    # rawStreamersData = TEST_CASES # uncomment to make use of test cases

    data = []
    for rawStreamerData in rawStreamersData:
        data.append(getStreamerData(rawStreamerData[0], rawStreamerData[1], rawStreamerData[2]))  # nickname, url, recorded_activity
        sleep(1)
    
    return data