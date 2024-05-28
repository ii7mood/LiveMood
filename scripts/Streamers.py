import yt_dlp
import requests
import sqlite3
import TwitchC
from os import path, getcwd
from sys import path as Path
from time import sleep
from bs4 import BeautifulSoup
from datetime import datetime
from common import logger, config

parent_path = getcwd().replace('/scripts', '')
Path.append(parent_path)
logger.name = __file__

# TO-DO: Test if Twitch scraper still works

db = sqlite3.connect('files/Streamers.db') # establish a connection to Streamers.db holding various data about each streamer
cursor = db.cursor()
avatars = {}

if path.getsize('files/Streamers.db') == 0: # assume file was just created then (no table)
    cursor.execute('''
        CREATE TABLE "streamers" (
        "NAME" TEXT NOT NULL,
        "URL" TEXT NOT NULL,
        "RECORDED_ACTIVITY" TEXT NOT NULL DEFAULT "not_live"
    )''')
    db.commit()

default_twitch_icon_path = "files/.cache/twitch_icon"
default_youtube_icon_path = "files/.cache/youtube_icon"
default_twitch_icon_url = "https://imgur.com/1LHl1Rb"
default_youtube_icon_url = "https://imgur.com/a/yzm4t9E"

def _fetch_twitch_information(streamer_url : str, stream_info = False) -> str:
    '''
    Attempts to extract Twitch avatar by either scraping or using Twitch API if credentials are provided.
    IF Twitch API is used we can also get concurrent viewer count for active streams.
    This is optional, and only happens if stream_info is set to True which _fetch_avatar does not set.
    Should NOT be used by itself, instead should be called by _fetch_avatar
    '''
    if config["TWITCH"]['scrape'] == "1":
        if stream_info == True: # If stream_info was requested while Twitch API is disabled then simply return none as we have no way to get API-only data.
            return None

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }

        try:
            response = requests.get(streamer_url, headers=headers)
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

        except requests.RequestException as e:
            logger.warning(f"Failed to get avatar by scraping Twitch.tv, using default twitch icon. {e}")
            return default_twitch_icon_url

    else:
        try:
            streamer_name = streamer_url.replace('https://www.twitch.tv/', '')

            
            if stream_info:
                stream = TwitchC.getStream(streamer_name)
                return [stream['data'][0]['viewer_count'], stream['data'][0]['game_name']]

            
            else:
                profile = TwitchC.getProfile(streamer_name)
                return profile['data'][0]['profile_image_url']
    
        except Exception as e:
            logger.warning(f"Failed to get avatar/stream_info using Twitch API, using default twitch icon/unknown. {e}")
            
            if stream_info:
                return "an unknown number of" #  supposed to be a placeholder for number of viewers
            else:
                return default_twitch_icon_url


def _fetch_avatar(streamer_name, streamer_url : str, yt_dlp_args : dict) -> str:
    '''
    As the name suggests this will attempt to cache the avatar of each streamer.
    This is supposed to be called by fetch_streamer which should pass the yt_dlp arguments variable.
    Will utilize _fetch_twitch_information / yt-dlp to get avatar URL then write to files/.cache
    returns url [0] and path [1] to streamer avatar.
    '''

    cachepath = f'files/.cache/{streamer_name.replace('/', '')}'
    url = None

    if "youtube" in streamer_url:
        try:
            with yt_dlp.YoutubeDL(yt_dlp_args) as ytd:
                info_dict = ytd.extract_info(streamer_url.replace('/live', '')) # ytd returns thumbnails containing avatar when confronted with home page of a channel.
                for thumbnail in info_dict['thumbnails']:
                    if thumbnail['id'] == "avatar_uncropped":
                        url = thumbnail['url']
                        image = requests.get(url)

        except Exception as e:
            logger.warning(f"Well, something went wrong. Default avatar path has been returned (YT). {e}")
            return (default_youtube_icon_url, default_youtube_icon_path)
        
    elif "twitch" in streamer_url:
        url = _fetch_twitch_information(streamer_url)
        if url == default_twitch_icon_url:
            return (default_twitch_icon_url, default_twitch_icon_path)
        
        image = requests.get(url)
    
    with open(cachepath, "wb+") as f:
        f.write(image.content)
    
    return (url, cachepath)



def fetch_streamer(raw_streamer_data: list) -> dict:
    """
    This is the main function extracting all necessary information regarding a singular streamer.
    The raw_streamer_data is a list with three elements : URL and recorded_activity (within DB, example : 'is_live' or 'not_live' or 'is_upcoming'), and name.
    """

    data = {} #  instead of returning the full dictionary from yt_dlp (large!), just return needed data

    # Get URL and live stream status from input list
    name = raw_streamer_data[0]
    url = raw_streamer_data[1]
    recorded_activity = raw_streamer_data[2]

    logger.info(f"Currently working with {url}")

    # In youtube adding /live at the end of a channel's URL redirects us to a live-stream (if exists)
    if "youtube" in url:
        url = url + '/live'
        platform = "youtube"
    
    else:
        platform = "twitch"
    
    # Set up options for yt-dlp extractor
    yt_dlp_args = {
        'quiet': True,  # Suppress non-error output
        'skip_download': True,  # Don't download any media
        'playlist_items': '0',  # Only look at first item in playlist
        'ignore_no_formats_error' : True,
        'no_warnings' : True
    }

    # Use yt-dlp to extract video information from URL
    with yt_dlp.YoutubeDL(yt_dlp_args) as ytd:
        try:
            info_dict = ytd.extract_info(url)
        
        except yt_dlp.DownloadError as e:
            if 'The channel is not currently live' in str(e):
                data = None
            
            elif 'Unable to recognize tab page' in str(e):
                logger.warning("Unable to recognize tab page... re-calling the function.")
                sleep(3)  # I do not know why I added this
                data = fetch_streamer(raw_streamer_data)
                return data
            
            elif 'Unable to download JSON metadata' in str(e):
                logger.warning("Unable to download JSON metadata... re-calling the function.")
                sleep(30)  # This can happen when my proxy fails (do not know what that means), will add sleep(30) bcuz why not?
                data = fetch_streamer(raw_streamer_data)
                return data

            else:
                logger.error(str(e) + '\n Setting live_status to offline')
                data = None

        if data != None:
            logger.info(f"Stream found. Status: {info_dict['live_status']}")

            if info_dict['live_status'] != recorded_activity and name not in avatars:  # if avatar URL is not already cached then cache it
                avatars[name] = _fetch_avatar(info_dict['uploader'], url, yt_dlp_args)  # returns a tuple with [0] being URL, and [1] being the path
            data['avatar_url'] = avatars[name][0]
            data['avatar_path'] = avatars[name][1]

            if info_dict['live_status'] == "is_upcoming":
                if info_dict['release_timestamp'] == None:  # When a Live stream gets close to its scheduled time YT stops giving us an exact timestamp.
                    data['release_timestamp'] = 'in_moments' # I know this is not really a timestamp but :shrug:
                    logger.info('no release_timestamp given despite an upcoming stream. Set to starting in a few moments.')

                elif (((info_dict['release_timestamp'] - datetime.timestamp(datetime.now())) / 3600) > 24): # Avoid scheduled streams that will start in over 24 hours
                    data['live_status'] = 'not_live'  # This does mean that _fetch_avatar will be called every iteration.
                    logger.info("Scheduled stream will start in over 24 hours so we will set it to not_live and ignore it.") 
            
            # 09/09/2023
            # Upon ending a livestream youtube now uses 'post_live' to indicate that a stream has ended
            # I am not sure if this is set temporarily or if it has special conditions wherein it is used
            # Afaik we do not really care about that so we will instead just set live_status to not_live.
            elif info_dict['live_status'] == 'post_live':
                data['live_status'] = 'not_live'

            if (platform == "twitch") and (info_dict['live_status'] == 'is_live'): # With YouTube viewer count is extracted automatically while Twitch not. So we will extract it manually using Twitch API. (if enabled)
                twitch_ext = _fetch_twitch_information(url, stream_info=True)
                info_dict['concurrent_view_count'] = twitch_ext[0]
                data['category_name'] = twitch_ext[1]
        
        else: # Stream does not exist so just populate this with bare minimum data to save to DB.
            data['live_status'] = 'not_live'
            data['uploader_url'] = url.replace('/live', '')
        
    # Hand-pick needed metadata, ignore the rest
    data['live_status'] = info_dict['live_status']
    data['uploader'] = info_dict["uploader"]
    data["thumbnail"] = info_dict["thumbnail"]
    data["fulltitle"] = info_dict["fulltitle"]
    data["concurrent_view_count"] = info_dict["concurrent_view_count"]
    data['recorded_live_status'] = recorded_activity
    data['platform'] = platform
    data['name'] = name
    data['uploader_url'] = url.replace('/live', '')
    data['stream_url'] = url

    return data


def get_all_streamers_data() -> list:
    """
    Get a list of dictionaries of all streamers in the database
    """
    cursor.execute("SELECT * FROM streamers")
    raw_streamers_data_list = cursor.fetchall()

    data = []
    for streamer in raw_streamers_data_list:
        data.append(fetch_streamer(streamer))
        sleep(1) # Without it we get a connection refused somewhere along the fetch_streamer function so let's not do that.
    
    return data


def update_streamer(url : str, current_activity : str) -> None:
    """
    Update the recorded_activity field of a streamer when a change in activity is detected
    """
    cursor.execute(
        "UPDATE streamers SET RECORDED_ACTIVITY = :current_activity WHERE URL = :url",
        {'url': url.replace('/live', ''), 'current_activity': current_activity}
    )
    db.commit()
    logger.info("Streamer information updated within database")
