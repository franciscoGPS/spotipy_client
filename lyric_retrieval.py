import ipdb as bp
import os
import os.path as path
import sys
filesystem_path = (path.abspath(path.join(path.dirname("__file__"), '../')) + '/youtdl/')

sys.path.append(filesystem_path)

from filesystem_tools import Filesystem
from song import Song

filesystem = Filesystem("mood_songs_file", "r+")
#bp.set_trace()

spotify_path = (path.abspath(path.join(path.dirname("__file__"), '')) + "/spotipy_oauth_demo/")
print(spotify_path)
song_list = filesystem.get_songs_list(spotify_path, "mood_songs_file", "r+")

for row in song_list:

    song = Song(artist=row[2], title=row[1])
    lyr = song.lyricwikia()
    print(lyr)




