import sqlite3
from os import path

db = sqlite3.connect('files/Streamers.db')
cursor = db.cursor()

if path.getsize('files/Streamers.db') == 0:  # if true, asssume file was just created
    cursor.execute('''
        CREATE TABLE "streamers" (
        "NAME" TEXT NOT NULL,
        "URL" TEXT NOT NULL,
        "RECORDED_ACTIVITY" TEXT NOT NULL DEFAULT "not_live"
    )''')
    db.commit()

def follow():
    url = input("URL: ")
    name = input("NAME: ")

    cursor.execute("SELECT * FROM streamers WHERE NAME = ?", (name,))
    reply = cursor.fetchall()

    if reply:
        print("Name already used. Try again.")
        return
    
    if (not ("youtube" in url)) and (not ("twitch" in url)):
        print("Invalid URL")
        return
    
    if url[-1] == '/':
        print("Make sure not to leave any forward-slashs at the end of the URL")
        return
    
    if not('www' in url):
        print('Make sure to inlcude www. in your URL, otherwise Twicth API pisses itself.')
        return
    
    
    cursor.execute(f"INSERT INTO streamers (URL, RECORDED_ACTIVITY, NAME) VALUES (?, ?, ?)", (url, "not_live", name.lower()))
    db.commit()

def unfollow():
    name = input("Streamers Name: ")
    cursor.execute(f"DELETE FROM streamers WHERE name = ?", (name.lower(),))
    db.commit()

def list_streamers():
    cursor.execute(f"SELECT * FROM streamers")
    raw_streamers_list = cursor.fetchall()

    streamers_list = []
    for streamer in raw_streamers_list:
        streamers_list.append(str(streamer[0]))

    print(" | ".join(streamers_list))

def search():
    criteria = input("Criteria: ")
    states = ['is_upcoming', 'is_live', 'not_live']
    if criteria in states:
        cursor.execute("SELECT * FROM streamers WHERE RECORDED_ACTIVITY=?", (criteria,))
    
    else:
        cursor.execute("SELECT * FROM streamers WHERE NAME = ?", (criteria,))
    
    query = cursor.fetchall()
    print(query)

while True:
    print(f"""
1 - Follow Streamer
2 - Remove Streamer
3 - List all Streamers
4 - Search with certain criteria\n""")
    
    opt = input("Select an option: ")
    match opt:
        case "1":
            follow()
        case "2":
            unfollow()
        case "3":
            list_streamers()
        case "4":
            search()
        case _:
            print("Please select an option by inputing a number between 1 and 4!\n")
