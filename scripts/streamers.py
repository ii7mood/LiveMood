import yt_dlp
import requests
import sqlite3
import TwitchC
from os import path
from sys import path as Path
from time import sleep
from bs4 import BeautifulSoup
import datetime
from common import logger, config, parent_path
from streamers_vars import avatars, yt_dlp_args, createTable, default_twitch_icon_path, default_twitch_icon_url, default_youtube_icon_path, default_youtube_icon_url

Path.append(parent_path)
logger.name = __file__

# TO-DO: Test if Twitch scraper still works

db = sqlite3.connect('files/Streamers.db') # establish a connection to Streamers.db holding various data about each streamer
cursor = db.cursor()

if path.getsize('files/Streamers.db') == 0: # assume file was just created
    cursor.execute(createTable)
    db.commit()


def _fetchTwitchStream(uploader_name: str) -> dict:
    """
    Returns a dict containing 'viewer_count' and 'game_name' keys.
    Uses Twitch API to request stream data then returns those two selected fields.
    """
    if config['twitch_opts']['scrape'] == "1":
        return None  # Have not implemented a way to scrape stream data from Twitch
    
    try:
        stream = TwitchC.getStream(uploader_name)
        return stream['data'][0]
    except Exception as e:
        logger.warning(f"Failed to retrieve Twitch Stream data. \n{e}")
        return {'viewer_count': 0, 'game_name': 'Unknown'}


def _fetchTwitchProfile(uploader_name: str) -> dict:
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
            logger.warning("Could not retrieve Twitch HTML structure. Fallbacking to default avatar.")
            return default_twitch_icon_url

    return TwitchC.getProfile(uploader_name)['data'][0]['profile_image_url']


def _fetchAvatar(uploader_name: str, uploader_url: str) -> tuple[str, str]:
    '''
    Returns a tuple holding the URL and path to the avatar.
    Attempts to cache both if a locally stored image does not exist.
    '''

    cachepath = f'files/cache/{uploader_name.replace('/', '')}'  # TO-DO: Need to validate filename for Windows as well.
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
        url = _fetchTwitchProfile(uploader_name)  # name is misleading as it only returns avatar URL, it might do more in the future tho
        if url == default_twitch_icon_url:
            return (default_twitch_icon_url, default_twitch_icon_path)
        image = requests.get(url)
    
    with open(cachepath, "wb+") as f:
        f.write(image.content)
    
    return (url, cachepath)



# Random errors refer to connection errors or anything that would be solved with a simple function re-call.
# Systematic errors are more complex and require some specific workaround.
def _extractData(url: str, yt_dlp_args: dict) -> dict:
    """
    Returns the dictionary returned by yt_dlp on a successful call.
    return types:
        on success: dict
        on systematic errors: None
        on random errors: 0
    """
    with yt_dlp.YoutubeDL(yt_dlp_args) as ytdlp:
        try:
            info_dict = ytdlp.extract_info(url)
            return info_dict
        
        except yt_dlp.DownloadError as e:
            if 'not currently live' in str(e):
                return None
            
            elif "tab page" in str(e):
                logger.warning(f"Random Error: \n{str(e)}")
                return 0
            
            elif "JSON metadata" in str(e):
                logger.warning(f"Random Error: \n{str(e)}")
                return 0

            else:
                logger.error(f"Systematic Error: \n{str(e)}")
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
    
    info_dict = _extractData(url, yt_dlp_args)
    match info_dict:
        case None:
            pass  # All systematic errors will be treated as a result of a channel not being live
            # If that assesment is wrong it will be logged as such and should be dealt with especially.
        case 0:
            sleep(15)  # This is necessary for some random errors, sleep value does vary though.
            info_dict = _extractData(url, yt_dlp_args)
        
    # At minimum the data dictionary should include: the uploader URL, current status, recorded status, and nickname.
    if info_dict is None:
        data['uploader_name'] = nickname
        data['live_status'] = 'not_live'
        data['recorded_live_status'] = recorded_activity
        data['uploader_url'] = uploader_url
        return data
        
    if info_dict['live_status'] == recorded_activity:
        data['uploader_name'] = nickname
        data['live_status'] = recorded_activity
        data['recorded_live_status'] = recorded_activity
        data['uploader_url'] = uploader_url
        return data
    
    #  At this point we know there is indeed a new stream
    logger.info(f"Stream Found. Status: {info_dict['live_status']}")

    #  Chained if-statements :)
    if info_dict['live_status'] == "is_upcoming":
        if info_dict['release_timestamp'] == None:
            data['release_timestamp'] = "in_moments"  # YT stops giving a precise value when nearing a the time of a scheduled stream
        
        else:
            #  Streams scheduled to start in >24h will not be recorded
            hours_until_stream = info_dict['release_timestamp'] - datetime.datetime.now().timestamp() / 3600
            if hours_until_stream > 24:
                data['uploader_name'] = nickname
                data['live_status'] = 'not_live'
                data['recorded_live_status'] = recorded_activity
                data['uploader_url'] = uploader_url
                return data
    
    # platform-specific data
    if platform == "twitch":
        tvData = _fetchTwitchStream(info_dict['uploader'])
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
    data['avatar_url'], data['avatar_path'] = _fetchAvatar(info_dict['uploader'], data['uploader_url'])

    return data


def updateStreamerActivity(url: str, activity: str) -> None:
    """
    Update the recorded_activity field of a streamer, using their URL as the identifier.
    """
    logger.info(f"{url} : {activity}")
    cursor.execute("UPDATE streamers SET RECORDED_ACTIVITY = ? WHERE URL = ?", (activity, url))
    db.commit()


def getStreamersData() -> list[dict]:
    """
    Returns a list of dictionaries holding data of their corresponding streamers.
    """
    cursor.execute("SELECT * FROM streamers")
    rawStreamersData: list[list[str, str, str]] = cursor.fetchall()

    data = []
    for rawStreamerData in rawStreamersData:
        data.append(getStreamerData(rawStreamerData[0], rawStreamerData[1], rawStreamerData[2]))
        sleep(1)
    
    return data
