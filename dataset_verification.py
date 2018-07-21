import ipdb
import pandas as pd
import os
import os.path as path
import sys
import make_lyrics_table as mlt
import time
import datetime
import nltk
import re
from shutil import copyfile
import glob
import subprocess
import re
from shlex import quote


filesystem_path = (path.abspath(path.join(path.dirname("__file__"), '../')) + '/youtdl/')

sys.path.append(filesystem_path)

from filesystem_tools import Filesystem
from youtube_query_for_video_ids import QueryVideo
from song import Song
import youtube_dl_client as ytc
#audios_path = "/media/frisco/FAT/cross-modal/audios/"





def make_audio_table(audios_path):
	files = [os.path.join(audios_path,fn) for fn in os.listdir(audios_path) if fn.endswith('.mp3')]
	data = {'mood':[], 'title':[], 'artist':[], 'lyric':[], 'youtube_video_id':[], 'file':[]}
	# Add artist and title data to dictionary
	for f in files:
		data['file'].append(f)
		audio_name = f.split('/')[-1]
		audio_data = audio_name.split('-')	
		#ipdb.set_trace()
		if len(audio_data) >= 3 :
		
			data['artist'].append(audio_data[0])
			data['title'].append(audio_data[1])
			data['youtube_video_id'].append(audio_data[2].split(".")[0])
		else:
			#ipdb.set_trace()
			data['artist'].append(audio_data[0])
			data['title'].append(audio_data[0])
			data['youtube_video_id'].append(audio_data[-1].split(".")[0])

		data['lyric'] = ""
		data['mood'] = ""
		# Convert dictionary to pandas DataFrame
		df = pd.DataFrame.from_dict(data, orient='columns')
		df = df[['mood', 'title', 'artist', 'lyric', 'youtube_video_id', 'file' ]]
	
	return df




def cut_30s_from_file(audio_new_name, file_path, output_path, start_time="00:30"):
	
	#"ffmpeg -i somefile.mp3 -f segment -segment_time 3 -c copy out%03d.mp3"

	subfolder_name = "30s_cuts/"
	if not os.path.isdir(output_path+subfolder_name):
		create_sub_dir = "mkdir "+ output_path+subfolder_name
		subprocess.call(create_sub_dir, shell=True)

	#file_path = escape_especial_chars(file_path)
	basename = os.path.basename(file_path)
	#command = "ffmpeg -i \""+ file_path +"\" -ab 160k -ac 1 -ar 22050 -t 30 -ss 00:00:30.000 -vn "+ output_path+subfolder_name + audio_new_name+ ".wav"
	file_to_cut = quote("/".join(file_path.split("/")[:-1]) +"/" +str(basename))
	command = 'ffmpeg -i '+ file_to_cut +' -ab 160k -ac 1 -ar 22050 -t 30 -ss 00:'+start_time+'.000 -vn "'+ output_path+subfolder_name + audio_new_name+ '".wav'
	result = subprocess.call(command, shell=True)
	if result:
		print(result)


def escape_especial_chars(input_string):
	escaped = input_string.translate(str.maketrans({"$":  r"\$"}))
	return escaped


def cleanup(audios_path, delivery_path):

	df = make_audio_table(audios_path)
	
	files = [os.path.join(filesystem_path,fn) for fn in os.listdir(filesystem_path) if fn.endswith('Synced_SongsMoodsFile.csv')]
	#ipdb.set_trace()
	analysis_result = {'found': 0, 'not_found': 0, 'other': 0 }
	print("Reading files found: ", len(files))
	for file in files:
		songs_lyrics_ids_file = pd.read_csv(file, delimiter=',', encoding="utf-8")

		song_lyrics_list = {'mood':[], 'title':[], 'artist':[], 'lyric':[], 'youtube_video_id':[], 'file':[]}

		print("This files contains rows", len(songs_lyrics_ids_file))
		for row_id, song in songs_lyrics_ids_file.iterrows():
			video_id = song['youtube_video_id']
			#video_id = songs_lyrics_ids_file[row_id]['youtube_video_id']
			query_result = df.query('youtube_video_id ==  @video_id')

			if len(query_result) == 1:
				#ipdb.set_trace()
				print("audio (and lyric) found in CSV")
				audios_found = glob.glob(audios_path+'*-'+video_id+'.mp3')
				if len(audios_found) > 1:
					print(audios_found)

				try:

					if os.path.exists(str(audios_found[0])):
						title = re.sub('\W+','_', song['title'].strip())
						artist = re.sub('\W+','_', song['artist'].strip())
						
						full_delivery_path = delivery_path+str(audios_found[0]).split('/')[-1]
						result = copyfile(str(audios_found[0]), full_delivery_path)						
						sample_audio_name_composition = title+"_"+artist
						
						sample_audio_name_composition = song['mood'].strip()+"_"+sample_audio_name_composition+"_"+video_id
						
						cut_30s_from_file(sample_audio_name_composition, str(audios_found[0]), delivery_path)

						saved_files = [os.path.join(delivery_path,fn) for fn in os.listdir(delivery_path) if fn.endswith('.mp3')]
						#ipdb.set_trace()
						
						if len(song_lyrics_list['file'])+1 == len(saved_files):
							
							print("song_lyrics_list len: ", len(song_lyrics_list['file']), "saved_files len: ",len(saved_files))

							analysis_result['found'] += 1 
							song_lyrics_list['title'].append(title)
							song_lyrics_list['artist'].append(artist)
							song_lyrics_list['mood'].append(song['mood'].strip())
							song_lyrics_list['lyric'].append(song['lyric'].strip())
							song_lyrics_list['youtube_video_id'].append(song['youtube_video_id'].strip())
							song_lyrics_list['file'].append(delivery_path+query_result['file'].values[0].split('/')[-1])
						
						#os.rename(query_result['file'].values[0], full_delivery_path)

					#ipdb.set_trace()
				except Exception as e:
					#ipdb.set_trace()
					print(e)
					
					#os.rename(delivery_path+query_result['file'].values[0].split('/')[-1], query_result['file'].values[0])
				
					#copyfile(src, dst)
			elif len(query_result) == 0:
				#ipdb.set_trace()
				analysis_result['not_found'] += 1
				print("audio not found in sounds folder: ", video_id)
				#songs_lyrics_ids_file.drop(songs_lyrics_ids_file.index[row_id])
				songs_lyrics_ids_file = songs_lyrics_ids_file[songs_lyrics_ids_file['youtube_video_id'] != video_id]


			else:
				#ipdb.set_trace()
				analysis_result['other'] += 1
				print("more than one result")
				print(query_result)

		print("audios, ids and lyrics list length", len(songs_lyrics_ids_file))

		songs_lyrics_ids_file.to_csv("ClearSongsMoodsFile.csv", index=False)
		
		dataframe = pd.DataFrame.from_dict(song_lyrics_list, orient='columns')
		dataframe = dataframe[['mood', 'title', 'artist', 'lyric', 'youtube_video_id', 'file' ]]
		date = str(datetime.datetime.now()).replace(" ", "_" )
		dataframe.to_csv(date+"_Synced_SongsMoodsFile.csv", index=False)
		"""
		audios_not_found = list()
		for row_id, song in df.iterrows():
			video_id = song['youtube_video_id']
			ipdb.set_trace
			query_result = songs_lyrics_ids_file.query('youtube_video_id == @video_id')	
			if len(query_result) == 0:
				audios_not_found.append(song)
				#os.remove(audios_path+"/"+song['file'])
				#print("Video removed: ", song)
		"""




    