import json
import os
import sys
import venv
from subprocess import run, CalledProcessError
from pathlib import Path

# I will eventually get to a formatting standard across all scripts, this one I just followed ChatGPT tips, sorry.
# But for now this will be the only script that won't use camelCase, because I like the way it looks 

PACKAGES = [
    'beautifulsoup4==4.12.3',
    'discord==2.3.2',
    'requests==2.32.2',
    'yt-dlp==2024.4.9',
    'plyer==2.1.0',
]

if os.name == "nt":
    PIP_PATH = "venv\\Scripts\\pip"
elif os.name == "posix":
    PIP_PATH = "venv/bin/pip"
    PACKAGES.append('dbus-python==1.3.2')
else:
    PIP_PATH = "venv/bin/pip"
    print("OS is neither Unix-like nor Windows. Defaulting to Unix-like behavior.")

CONFIG_PATH = Path('files/config.json')
VENV_DIR = Path('venv')

def load_config(path):
    with open(path, 'r') as configfile:
        return json.load(configfile)

def save_config(path, config):
    with open(path, 'w') as configfile:
        json.dump(config, configfile, indent=2)

def create_virtual_env(venv_dir):
    print("Creating a virtual environment..")
    try:
        venv.create(venv_dir, with_pip=True)
        print('/venv created!')
        return True
    except OSError as e:
        print(f"Failed to create virtual environment. Error: {e}")
        return False

def install_packages(pip_path, packages):
    print("Installing necessary packages via pip..")
    for package in packages:
        try:
            result = run([pip_path, 'install', package], check=True)
        except CalledProcessError as e:
            print(f"Failed to install package {package}. Error: {e}")
            return False
    return True

def setup_twitch(config):
    scrape = input("Would you prefer retrieving data through the Twitch API (need to acquire keys from developer portal, recommended)? Y/N: ").strip().lower() == "n"
    if not scrape:
        print("Visit the following URL and sign-in using your Twitch Account (official site of Twitch)\n\n-> https://dev.twitch.tv/")
        print("Click on: Your Console (top-right) -> Register Your Application (left-center)")
        print("Enter a name for your application; Can be anything you want. As for the OAuth Redirect URLs enter:\n\n-> http://localhost")
        print("Click on the category field and select 'application integration' (or anything, really.)")
        print("Check the 'Confidential' checkbox and solve the CAPTCHA (if required) and click 'Create'.")
        CLIENT_ID = input("\nNow a new 'Client ID' field should appear. Copy the Client ID and paste here: ").strip()
        CLIENT_SECRET = input("Next, Click on the purple 'New Secret' button and paste the Client Secret here: ").strip()

        config['twitch_opts']['client_id'] = CLIENT_ID
        config['twitch_opts']['client_secret'] = CLIENT_SECRET
        config['twitch_opts']['scrape'] = 0

def setup_discord(config):
    print('Visit the following URL and sign-in using your Discord Account\n-> https://discord.com/developers')
    print("Click on: New Application (top-right) -> Enter anything within the NAME field and tick the check box then 'Create'")
    TOKEN = input("\n\nOn the left-sidebar click on 'Bot' then press the 'Reset Token' button and paste the token here: ").strip()
    CLIENT_ID = input("\n\nNext, on the left-sidebar click on 'OAuth2' section, copy the CLIENT ID and enter it here: ").strip()

    print(f"Copy the following link and paste it into any browser:\n\n-> https://discord.com/oauth2/authorize?client_id={CLIENT_ID}&permissions=2048&scope=bot+applications.commands")
    print("This will add the Bot to your selected server.")

    print("Lastly, On Discord, Enter the user setting (bottom-left) and on the left-sidebar click on Advanced.")
    print("Enable Developer Mode. Then exit the settings and right-click any text-channel that you would like the Bot to send messages to and copy Channel ID (make sure the Bot CAN see the channel)")
    CHANNEL_ID = input("Paste the Channel ID here: ").strip()

    config['listeners']['discord']['channel_id'] = CHANNEL_ID
    config['listeners']['discord']['token'] = TOKEN
    config['listeners']['discord']['enable'] = 1

def main():
    config = load_config(CONFIG_PATH)
    
    if create_virtual_env(VENV_DIR):
        if not install_packages(PIP_PATH, PACKAGES):
            print("Something went wrong during package installation. Exiting.")
            sys.exit(1)
    else:
        print("Continuing without setting up a virtual environment or installing packages.")

    print('----------------------------------')  # Makes it a little cleaner :)
    if input("\nShould the script continue assisting in setting up the software? Y/N: ").strip().lower() != 'y':
        sys.exit(0)

    config['listeners']['desktop']['enable'] = input("\nWould you like to enable the Desktop module? Y/N: ").strip().lower() == 'y'

    if input("\nWould you like to enable and set-up the Discord module? Y/N: ").strip().lower() == 'y':
        setup_discord(config)

    setup_twitch(config)

    config['path_to_cookies'] = input("\n\nEnter the path to your cookies.txt (optional, leave blank if not needed.): ").strip()

    save_config(CONFIG_PATH, config)

    input("\n\n\nYou can now delete the setup.py file. Press any key to exit..")

if __name__ == "__main__":
    main()
