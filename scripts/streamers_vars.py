default_twitch_icon_path = "files/cache/twitch_icon"
default_youtube_icon_path = "files/cache/youtube_icon"
default_twitch_icon_url = "https://imgur.com/1LHl1Rb"
default_youtube_icon_url = "https://imgur.com/a/yzm4t9E"

avatars = {}

createTable = '''
CREATE TABLE "streamers" (
"NAME" TEXT NOT NULL,
"URL" TEXT NOT NULL,
"RECORDED_ACTIVITY" TEXT NOT NULL DEFAULT "not_live")
'''

yt_dlp_args = {
    'quiet': True,
    'skip_download': True,
    'playlist_items': '0',
    'ignore_no_formats_error' : True,
    'no_warnings' : True
}