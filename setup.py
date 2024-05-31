import venv
import json
from subprocess import run
import json

packages = [
'beautifulsoup4==4.12.3',
'discord==2.3.2',
'requests==2.32.2',
'yt-dlp==2024.4.9',
'plyer==2.1.0',
'dbus-python==1.3.2'
]

config = dict()
with open(f'files/config.json', 'r') as configfile:
    config = json.load(configfile)

def setup_twitch():
    scrape = input("Would you prefer retreiving data through the Twitch API (need to acquire keys from developer portal, recommended)? Y/N: ")
    scrape = scrape.lower() == "n"

    if not scrape:
        print("Visit the following URL and sign-in using your Twitch Account (official site of Twitch)\n\n-> https://dev.twitch.tv/")
        print("Click on: Your Console (top-right) -> Register Your Application (left-center)")
        print("Enter a name for your application; Can be anything you want. As for the OAuth Redirect URLs enter:\n\n-> http://localhost")
        print("Click on the category field and select 'application integration' (or anything, really.)")
        print("Check the 'Confidential' checkbox and solve the CAPTCHA (if required) and click 'Create'.")
        CLIENT_ID = input("\nNow a new 'Client ID' field should appear. Copy the Client ID and paste here: ")
        CLIENT_SECRET = input("Next, Click on the purple 'New Secret' button and paste the Client Secret here: ")

        config['twitch_opts']['client_id'] = CLIENT_ID
        config['twitch_opts']['client_secret'] = CLIENT_SECRET
        config['twitch_opts']['scrape'] = 0
    

def setup_discord():
    print('Visit the following URL and sign-in using your Discord Account\n-> https://discord.com/developers')
    print("Click on: New Application (top-right) -> Enter anything within the NAME field and tick the check box then 'Create'")
    TOKEN = input("\n\nOn the left-sidebar click on 'Bot' then press the 'Reset Token' button and paste the token here: ")
    CLIENT_ID = input("\n\nNext, on the left-sidebar click on 'OAuth2' section, copy the CLIENT ID and enter it here: ")

    print(f"Copy the following link and paste it into any browser:\n\n-> https://discord.com/oauth2/authorize?client_id={CLIENT_ID}&permissions=2048&scope=bot+applications.commands")
    print("This will add the Bot to your selected server.")

    print("Lastly, On Discord, Enter the user setting (bottom-left) and on the left-sidebar click on Advanced.")
    print("Enable Developer Mode. Then exit the settings and right-click any text-channel that you would like the Bot to send messages to and copy Channel ID (make sure the Bot CAN see the channel)")
    CHANNEL_ID = input("Paste the Channel ID here: ")

    config['listeners']['discord']['channel_id'] = CHANNEL_ID
    config['listeners']['discord']['token'] = TOKEN
    config['listeners']['discord']['enable'] = 1


# Creating a virtual environment and installing required packages
print("Creating a virtual environment..")
try:
  venv.create('venv', with_pip=True)
  print('/venv created!')

  print("Installing necessary packages via pip..")
  for package in packages:
    writeback = run(['venv/bin/pip', 'install', package])  # Does not work on Windows !!

  if writeback.returncode:
      print("Something went wrong. Exiting.")
      exit(1)
except OSError as e:
  print(f"Something went wrong. Error: {e}. Will continue without installing packages or creating a virtual environment.")

# Assist in setting up the necessary pre-requisites (if needed)
print('----------------------------------')  # Makes it a little cleaner :)
automatic = input("\nShould the script continue assisting in setting up the software? Y/N: ")
if automatic.lower() == "n":
    exit(0)

desktop = input("\nWould you like to enable the Desktop module? Y/N: ")
config['listeners']['desktop']['enable'] = desktop.lower() == 'y'

discord = input("\nWould you like to enable and set-up the Discord module? Y/N: ")
if discord.lower() == 'y':
    setup_discord()

setup_twitch()

path_to_cookies = input("\n\nEnter the pack to your cookies.txt (optional, leave blank if not needed.): ")
config['path_to_cookies'] = path_to_cookies

with open('files/config.json', 'w') as configfile:
    json.dump(config, configfile, indent=2)

input("\n\n\nYou can now delete the setup.py file. Press any key to exit..")



