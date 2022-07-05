import os.path

download_file = 'C:/Users/shado/PycharmProjects/discord_bot.py/downloads'


def scan_files():
    song_files = os.listdir(download_file)
    if len(song_files) == 0:
        print('nothing inside the download folder')
    else:
        print(song_files)


def delete_files():
    for file in os.scandir(download_file):
        os.remove(os.path.join(download_file, file))


scan_files()
delete_files()
