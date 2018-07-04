# Sebastian Raschka, 2014
# 
# Script to download lyrics from http://lyrics.wikia.com/

import urllib
import lxml.html
import ipdb;

class Song(object):
    def __init__(self, artist, title):
        self.artist = self.__format_str(artist)
        self.title = self.__format_str(title)
        self.url = None
        self.lyric = None
        
    def __format_str(self, s):
        # remove paranthesis and contents
        s = s.strip()
        try:
            # strip accent
            s = ''.join(c for c in unicodedata.normalize('NFD', s)
                         if unicodedata.category(c) != 'Mn')
        except:
            pass
        s = s.title()
        return s
        
    def __quote(self, s):
         return urllib.parse.quote(s.replace(' ', '_'))

    def __make_url(self):
        artist = self.__quote(self.artist)
        title = self.__quote(self.title)
        artist_title = '%s:%s' %(artist, title)
        url = 'http://lyrics.wikia.com/' + artist_title
        self.url = url
        
    def update(self, artist=None, title=None):
        if artist:
            self.artist = self.__format_str(artist)
        if title:
            self.title = self.__format_str(title)
        
    def lyricwikia(self):
        self.__make_url()
        try:
            doc = lxml.html.parse(self.url)
            lyricbox = doc.getroot().cssselect('.lyricbox')[0]
            
        except (IOError, IndexError) as e:
            self.lyric = ''
            return self.lyric
        lyrics = []

        for node in lyricbox:
            if node.tag == 'br':
                lyrics.append('\n')
            if node.tail is not None:
                lyrics.append(node.tail)
        self.lyric =  "".join(lyrics).strip()    
        return self.lyric