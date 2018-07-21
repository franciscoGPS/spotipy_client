import os
import pandas as pd

def make_artist_table(base):

# Get file names

    files = [os.path.join(base,fn) for fn in os.listdir(base) if fn.endswith('.h5')]
    data = {'file':[], 'artist':[], 'title':[]}

    # Add artist and title data to dictionary
    for f in files:
        store = pd.HDFStore(f)
        
        title = store.root.metadata.songs.cols.title[0]
        artist = store.root.metadata.songs.cols.artist_name[0]
        #data['file'].append(os.path.basename(f))
        data['title'].append(title.decode("utf-8"))
        data['artist'].append(artist.decode("utf-8"))
        store.close()
    
    # Convert dictionary to pandas DataFrame
    df = pd.DataFrame.from_dict(data, orient='columns')
    df = df[['file', 'artist', 'title']]
    return df