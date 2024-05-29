import venv
import json
from subprocess import run
from sys import executable

packages = [
'beautifulsoup4==4.12.3',
'discord==2.3.2',
'requests==2.32.2',
'yt-dlp==2024.4.9',
'plyer==2.1.0',
'dbus-python==1.3.2'
]

config = {
  "python_executable": "python",
  "path_to_cookies": "",

  "twitch_opts": {
    "scrape": 1,
    "client_id": "",
    "client_secret": "",
    "access_token": ""
  },

  "listeners": {

    "discord": {
      "enable": 0,
      "host": "127.0.0.1",
      "port": 9989,
      "token": "",
      "channel_id": "",
      "module_path": "discord/main.py"
    },

    "desktop": {
      "enable": 0,
      "external": 0, 
      "host": "127.0.0.1",
      "port": 9990,
      "module_path": "desktop/main.py"
    }

  }
}



def setup_twitch():
    print("Would you prefer retreiving data through the Twitch API (need to acquire keys from developer portal, recommended)? Y/N: ")
    scrape = input("").lower() == "y"

    if not scrape:
        print("Visit the following URL and sign-in using your Twitch Account (official site of Twitch)\n-> https://dev.twitch.tv/")
        print("Click on: Your Console (top-right) -> Register Your Application (left-center)")
        print("Enter a name for your application; Can be anything you want. As for the OAuth Redirect URLs enter:\nhttp://localhost")
        print("Click on the category field and select 'application integration' (or anything, really.)")
        print("Check the 'Confidential' checkbox and solve the CAPTCHA (if required) and click 'Create'.")
        CLIENT_ID = input("Now a new 'Client ID' field should appear. Copy the Client ID and paste here: ")
        CLIENT_SECRET = input("Next, Click on the purple 'New Secret' button and paste the Client Secret here: ")

        config['twitch_opts']['client_id'] = CLIENT_ID
        config['twitch_opts']['client_secret'] = CLIENT_SECRET
        config['twitch_opts']['scrape'] = 0
    

def setup_discord():
    print('Visit the following URL and sign-in using your Discord Account\n-> https://discord.com/developers')
    print("Click on: New Application (top-right) -> Enter anything within the NAME field and click on the check box then 'Create'")
    TOKEN = input("On the left-sidebar click on 'Bot' then press the 'Reset Token' button and paste the token here: ")
    CLIENT_ID = input("Next, on the left-sidebar click on 'OAuth2' section, copy the CLIENT ID and enter it here: ")

    print(f"Copy the following link and paste it into any browser:\n-> https://discord.com/oauth2/authorize?client_id={CLIENT_ID}&permissions=2048&scope=bot+applications.commands")
    print("This will add the Bot to your selected server.")

    print("Lastly, On Discord, Enter the user setting (bottom-left) and on the left-sidebar click on Advanced.")
    print("Enable Developer Mode. Then exit the settings and right-click any text-channel that you would like the Bot to send messages to and copy Channel ID (make sure the Bot CAN see the channel)")
    CHANNEL_ID = input("Paste the Channel ID here: ")

    config['listeners']['discord']['channel_id'] = CHANNEL_ID
    config['listeners']['discord']['token'] = TOKEN
    config['listeners']['discord']['enable'] = 1


# Creating a virtual environment and installing required packages
print("Creating a virtual environment..")
venv.create('venv')
print("Installing necessary packages via pip..")
exitcode = run([executable, '-m', 'pip', 'install'] + packages, capture_output=True, text=True)

if exitcode:
    print("Something went wrong. Exiting.")
    exit(1)


# Assist in setting up the necessary pre-requisites (if needed)
automatic = input("Exit here? (You will need to manually configure the program, for advanced users) Y/N: ")
if automatic.lower() == "y":
    exit(0)

desktop = input("Would you like to enable the Desktop module? Y/N: ")
config['listeners']['desktop']['enable'] = desktop.lower() == 'y'

discord = input("Would you like to enable and set-up the Discord module? Y/N: ")
if discord.lower() == 'y':
    setup_discord()

setup_twitch()

with open('files/config.json', 'w') as configfile:
    json.dump(config, configfile, indent=2)





