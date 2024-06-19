# LiveMood

![Example images of some listeners](https://picoshare.ii7mood.com/-xzQp74nsBx)

I first wrote LiveMood (under a different name) to be used as an alternative to YouTube & Twitch's official notification system as it was filled with flaws and would often not work. It used to be made to work exclusively with Discord but even that sucks now, so having the option to just quickly write up a module for any platform was added.

Now I continue updating this program simply because of how much nicer it is to have a detailed overview of each stream right from the notification (also gain experience :D). This will continue being updated so long as I use it.

* [Installation](#Installation)
    * [Updates](#Installation##Updates)
* [Configuration](#Configuration)
* [Writing Listeners](#Listeners)
* [Road Map](https://github.com/ii7mood/LiveMood/issues/4)

# Installation
Simply clone this repository and run setup.py then follow its instructions. From there you can delete the setup.py script (or keep it :shrug:) and run main.py:

```
git clone https://github.com/ii7mood/livemood
cd livemood
python setup.py
python main.py
```

## Updates
I still am not really sure how to handle updating this program. I think you can use `git pull origin` or download the latest release and simply overwrite everything. If there are any additional steps necessary I will make sure to note them down. It's recommended to make a back-up before updating, just in case. I will eventually look into an easy way to update this without hassle.

# Configuration
You can configure the program through the `livemood/files/config.js` file. Each module will have its own set of options under `listeners`. Other options include `path_to_cookies` which expects an absolute path. Lastly, you can add your Twitch application details under the `twitch_opts` key.

# Listeners
As per the [Project Principles document](https://github.com/ii7mood/LiveMood/blob/main/project_principles.md) you need to make sure to handle `SIGTERM` signals and close any instances properly. The server (Detector.py) expects an acknowledgement that the listener is done processing (b"DONE"). You can reference `livemood/desktop/main.py`. I will make it easier to write listeners eventually but for now this will have to do. Sorry.