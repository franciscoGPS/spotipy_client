import getopt
import os
import pandas as pd
import os.path as path
import sys
import make_lyrics_table as mlt
import time
import datetime
import nltk
from shutil import copyfile
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

filesystem_path = (path.abspath(path.join(path.dirname("__file__"), '../')) + '/youtdl/')

sys.path.append(filesystem_path)

from filesystem_tools import Filesystem
from youtube_query_for_video_ids import QueryVideo
from song import Song
import youtube_dl_client as ytc
import dataset_verification as dataset


AUDIO_STORAGE_PATH = ""
MOODS_SONGS_FILE_NAME = ""
OUTPUT_SONGS_LYRICS_FILE = ""
YDL_OPTS = {}
DATASET_AVAILABE = ""

def main(argv):
    try:
      global AUDIO_STORAGE_PATH, MOODS_SONGS_FILE_NAME, OUTPUT_SONGS_LYRICS_FILE, YDL_OPTS, DATASET_AVAILABE
      #"/media/frisco/FAT/cross-modal/audios2/", moods_songs_clear_names_file_small
      opts, args = getopt.getopt(argv,"hi:p:o:d:",["storage=","songsfile=", "outputfile=", "dataset="])
    except getopt.GetoptError:
      print('python video_lyric_retrieval.py -p <storage> -i <songsfile> -o <outputfile> -d <dataset> ')
      print('python video_lyric_retrieval.py -p "/media/frisco/FAT/cross-modal/audios2/" -i "moods_songs_clear_names_file_small" -o "moods_lyrics_files_dataset" -d "/media/frisco/FAT/cross-modal/audios/"')
      sys.exit(2)
    for opt, arg in opts:
      if opt == '-h':
         print('python video_lyric_retrieval.py -p <storage> -i <songsfile> -o <outputfile> -d <dataset> ')
         sys.exit()
      elif opt in ("-p", "--storage"):
         AUDIO_STORAGE_PATH = arg.strip()
      elif opt in ("-i", "--songsfile"):
         MOODS_SONGS_FILE_NAME = (path.abspath(path.join(path.dirname("__file__"), '../')) + '/spotify/spotipy_oauth_demo/') + arg.strip() + ".csv"
      elif opt in ("-o", "--outputfile"):
         OUTPUT_SONGS_LYRICS_FILE = arg.strip()
      elif opt in ("-d", "--outputfile"):
         DATASET_AVAILABE = arg.strip()

    print( 'Storage path is: ', AUDIO_STORAGE_PATH)
    print( 'Moods/songs file path: ', MOODS_SONGS_FILE_NAME)
    print( 'Output lyrics file: ', OUTPUT_SONGS_LYRICS_FILE)
    print( 'Dataset available: ', DATASET_AVAILABE)
    nltk.download('stopwords')
    nltk.download('punkt')
    start_process()




def download_video(video_id, song_title):
    YDL_OPTS = {
        'format': 'bestaudio/best',
        'extractaudio':True,
        #'audioformat':'mp3',
        #'outtmpl':u'%(title)s-%(id)s.%(ext)s',     #name the file the ID of the video
        'noplaylist':True,
        'nocheckcertificate':True,        
        #'outtmpl': u"audios/"+'%(title)s-%(id)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192'
        }],
        #'postprocessor_args':[{
        #    'ss':'00:00:10',
        #    't' :'00:00:30',

        #}]
        'outtmpl': AUDIO_STORAGE_PATH+song_title + '_%(id)s.%(ext)s',
        'retries': 10,
        'ignoreerrors':True,
        'forcefilename':True

    }
    downloader = ytc.YoutubeDLClient(YDL_OPTS)
    downloader.download_video(video_id)


def english_lyric(text):
    diff = eng_ratio(text)
    ## English returns diff 0.
    #If the diff is greater of 0.5 the lyric contains more non english words.
    if diff >= 0.5:
        print("Lyric has more than 50\% of non-english words")
        print(text)
        return 0
    else:
        return 1

def eng_ratio(text):
    ''' Returns the ratio of non-English to English words from a text '''

    english_vocab = set(w.lower() for w in nltk.corpus.words.words()) 
    text_vocab = set(w.lower() for w in text.split() if w.lower().isalpha()) 
    unusual = text_vocab.difference(english_vocab)
    diff = 1
    if len(text_vocab) > 0:
        diff = len(unusual)/len(text_vocab)
    return diff


def retrieve_audio_from_storage(video_id):
    try:
        audios= df.query('youtube_video_id ==  @video_id')
        return_val = len(audios) > 0
    except Exception as e:
        print("Error youtube_video_id: ", video_id)
        return_val = 0    
    return audios

def clean_lyric(lyric):
    stop_words = set(stopwords.words('english')) 
    
    #(" ").join(list(filter(lambda x: x != '', lyric.split("\n"))))
    word_tokens = word_tokenize(lyric)
    filtered_sentence = [w for w in word_tokens if not w in stop_words]
    filtered_sentence = []
    for w in word_tokens:
        if w not in stop_words:
            filtered_sentence.append(w)
    print("This lyric contains %03d", len(filtered_sentence))
    return filtered_sentence


def remove_audio_file(video_id):
    file = df.query('youtube_video_id ==  @video_id')
    #os.remove(file)
    print("Video (not)removed: ", video_id)

def copy_found_audios_to_new_location(audios_found, new_name):
    if os.path.exists(audios_found.iloc[0]['file']):
        print(audios_found)
        video_id = audios_found.iloc[0]['youtube_video_id']
        full_delivery_path = AUDIO_STORAGE_PATH+new_name +'_'+ video_id+".mp3"
        try:
            copyfile(str(audios_found.iloc[0]['file']), full_delivery_path)
        except Exception as e:
            print(e)

def already_downloaded(file):
    return os.path.exists(file)

        
        
def store_lyric(lyric, row, query):
    query_string = str(row[1]) + " " + str(row[2])
    video_id = query.query_video(query_string)
    if(english_lyric(lyric)):
        
        if video_id != '' and video_id != False:
            print(video_id)
            track_name = str(row[1]).strip().replace(" ", "-")
            artist_name = str(row[2]).strip().replace(" ", "-")
            complete_track_name = str(row[0]) +'_'+ track_name+'_'+artist_name
            song_lyrics_list['youtube_video_id'].append(str(video_id))
            song_lyrics_list['mood'].append(str(row[0]))
            song_lyrics_list['title'].append(str(row[1]))
            song_lyrics_list['artist'].append(str(row[2]))
            song_lyrics_list['lyric'].append(lyric)
            song_lyrics_list['bow'].append(clean_lyric(lyric))
            song_lyrics_list['file'].append(complete_track_name+ "_"+str(video_id)+".mp3")
            audios_found = retrieve_audio_from_storage(str(video_id))
            
            

            if len(audios_found) == 0:
                if not already_downloaded(AUDIO_STORAGE_PATH + complete_track_name+ "_"+str(video_id)+".mp3"):
                    download_video(video_id, complete_track_name)
                    if not already_downloaded(AUDIO_STORAGE_PATH + complete_track_name+ "_"+str(video_id)+".mp3"):
                
                        print("video not found. Removing from list: ")
                        print(song_lyrics_list['youtube_video_id'].pop())
                        print(song_lyrics_list['artist'].pop())
                        print(song_lyrics_list['title'].pop())
                        song_lyrics_list['mood'].pop()
                        song_lyrics_list['lyric'].pop()
                        song_lyrics_list['bow'].pop()
                        song_lyrics_list['file'].pop()


            else:
                copy_found_audios_to_new_location(audios_found, complete_track_name)
                print("Audio not needed to download: ", video_id)
    else:
        if len(retrieve_audio_from_storage(str(video_id))) == 1:
            remove_audio_file(video_id)

def start_process():

    date = str(datetime.datetime.now()).replace(" ", "_" )
    filesystem = Filesystem(MOODS_SONGS_FILE_NAME, "r+")
    #file_name = filesystem_path+'/'+date+'_moods_songs_lyrics.csv'
    file_name = filesystem_path + OUTPUT_SONGS_LYRICS_FILE+'.csv'

    song_list = filesystem.get_songs_list()



    song_lyrics_not_found = list()
    global song_lyrics_list 
    song_lyrics_list = {'mood':[], 'title':[], 'artist':[], 'lyric':[], 'youtube_video_id':[], 'file':[], 'bow':[]}

    song_lyrics_not_found = {'mood':[], 'title':[], 'artist':[]}

    global df
    df = dataset.make_audio_table(DATASET_AVAILABE)
    total_songs = len(song_list)
    service = ""
    global query 
    query = QueryVideo()

    starting_index=0
    lyr = ""

    COUNTER = 0
    for index, row in enumerate(song_list[starting_index:]):

        song = Song(artist=row[2], title=row[1])
        lyr = song.lyricwikia()
        if lyr == '':
            lyr = song.songlyrics()
            if lyr != '':
                service = "songlyrics" 
                store_lyric(lyr, row, query)
                COUNTER+=1
            else:

                ##Here one can add functionality if tryin to add another source or lyrics or another way to call the service
                song_lyrics_not_found['mood'].append(str(row[0]))
                song_lyrics_not_found['title'].append(str(row[1]))
                song_lyrics_not_found['artist'].append(str(row[2]))
                print("not found in both", str(index + starting_index )+"/"+str(total_songs),row[1], row[2])
                service = ""
                
        else:
            service = "lyricwikia"
            store_lyric(lyr, row, query)
            COUNTER+=1
            
        print("", str(COUNTER)+"/"+ str(index)+"/"+str(total_songs), service)
        if len(song_lyrics_list['mood']) % 5 == 0 and len(song_lyrics_list['mood']) > 4 :
            #ipdb.set_trace()
            #print("", str(index)+"/"+str(total_songs), service, lyr)
            dataframe = pd.DataFrame.from_dict(song_lyrics_list, orient='columns') 
            with open(file_name, 'a') as f:
                dataframe.to_csv(f, header=False)
            song_lyrics_list = {'mood':[], 'title':[], 'artist':[], 'lyric':[], 'youtube_video_id':[], 'file':[], 'bow':[]}    
        elif len(song_lyrics_list['mood']) == 1:
            dataframe = pd.DataFrame.from_dict(song_lyrics_list, orient='columns') 
            with open(file_name, 'a') as f:
                dataframe.to_csv(f)

            song_lyrics_list = {'mood':[], 'title':[], 'artist':[], 'lyric':[], 'youtube_video_id':[], 'file':[], 'bow':[]}        

    dataframe = pd.DataFrame.from_dict(song_lyrics_list, orient='columns') 
    with open(file_name, 'a') as f:
        dataframe.to_csv(f, header=False)
    song_lyrics_list = {'mood':[], 'title':[], 'artist':[], 'lyric':[], 'youtube_video_id':[], 'file':[], 'bow':[]} 


    #dataframe_not_found = pd.DataFrame.from_dict(song_lyrics_not_found, orient='columns')

    
    #df = df[['mood', 'title', 'artist', 'lyric', 'youtube_video_id']]

    #print(sum(df['lyric']!=''))
    #print(sum(df_not_found['title']!=''))


if __name__ == '__main__':
    main(sys.argv[1:])